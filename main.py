from fastapi import FastAPI, UploadFile, Form, Response, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from typing import Annotated
import sqlite3

con = sqlite3.connect('db.db', check_same_thread=False)
cur = con.cursor()

cur.execute(f"""
            CREATE TABLE IF NOT EXISTS items (
	        id INTEGER PRIMARY KEY,
	        title TEXT NOT NULL,
	        image BLOB,
	        price INTEGER NOT NULL,
	        description TEXT,
	        place TEXT NOT NULL,
	        insertAt INTEGER NOT NULL
            );
            """)

app = FastAPI()

SECRET = "super-coding"
manager = LoginManager(SECRET,'/login')


@manager.user_loader()
def query_user(data):
    WHERE_STATEMENTS = f'id="{data}"'
    if type(data) == dict:
        WHERE_STATEMENTS = f'''id="{data['id']}"'''
        
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    user = cur.execute(f"""
                       SELECT * from users WHERE {WHERE_STATEMENTS}
                       """).fetchone()
    return user
    

@app.post('/login')
def login(id:Annotated[str,Form()],
           password:Annotated[str,Form()]):
    user = query_user(id)
    if not user:
        # InvalidCredentialsException:자동으로 401을 생성해서 내려줌
        raise InvalidCredentialsException
    elif password != user['password']:
        raise InvalidCredentialsException
    
    access_token = manager.create_access_token(data={
        'sub': {
        'id':user['id'],
        'name':user['name'],
        'email':user['email']
        }
    })
    
    return {'access_token':access_token}
    
    # return값을 200으로 지정하지 않아도 자동으로 선택코드를 200으로 내려줌
    # return "하이"


@app.post('/signup')
def signup(id:Annotated[str,Form()],
           password:Annotated[str,Form()],
           name:Annotated[str,Form()],
           email:Annotated[str,Form()]):
    cur.execute(f"""
                INSERT INTO users(id,name,email,password)
                VALUES ('{id}','{name}','{email}','{password}')
                """)
    con.commit()
    return '200'


# @app.get('/getId/{id}')
# async def get_id(id):
#     # 아이디 중복체크
#     print("아이디 중복체크");
#     cur = con.cursor();
#     getid = cur.execute(f"""
#                        SELECT COUNT(id) FROM users WHERE id={id};
#                        """).fetchone()[0]
    
#     return  Response(getid)


@app.post('/items')
async def create_items(image:UploadFile,
                 title:Annotated[str,Form()],
                 price:Annotated[int,Form()],
                 description:Annotated[str,Form()],
                 place:Annotated[str,Form()],
                 insertAt:Annotated[int,Form()]
                ):
    image_bytes = await image.read()
    cur.execute(f"""
                INSERT INTO
                items(title, image, price, description, place, insertAt)
                VALUES
                ('{title}','{image_bytes.hex()}',{price},'{description}','{place}', '{insertAt}')
                """)
    con.commit()
    return '200'

@app.get('/items')
async def get_items(user=Depends(manager)):
    # 컬럼명도 같이 가져옴
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    rows = cur.execute(f"""
                       SELECT * from items;
                       """).fetchall()
    
    return JSONResponse(jsonable_encoder(dict(row) for row in rows))
    
    # rows = [['id',1],['title','젤리팔아요'],['description','맛있어요']...]
    # dict(row) for row in rows : rows 중에 각각 array를 돌면서 array를 dictionary(객체형태)로 만들어 주는 문법
    
@app.get('/images/{item_id}')
async def get_image(item_id):
    cur = con.cursor()
    # 16진법
    image_bytes = cur.execute(f"""
                              SELECT image from items WHERE id={item_id}
                              """).fetchone()[0]
    return Response(content=bytes.fromhex(image_bytes), media_type='image/*')

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
