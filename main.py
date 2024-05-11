from fastapi import FastAPI, UploadFile, Form, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
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
async def get_items():
    # 컬럼명도 같이 가져옴
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    rows = cur.execute(f"""
                       SELECT * FROM items;
                       """).fetchall()
    
    # rows = [['id',1],['title','젤리팔아요'],['description','맛있어요']...]
    # dict(row) for row in rows : rows 중에 각각 array를 돌면서 array를 dictionary(객체형태)로 만들어 주는 문법
    
    return JSONResponse(jsonable_encoder(dict(row) for row in rows))
    
@app.get('/images/{item_id}')
async def get_image(item_id):
    cur = con.cursor()
    # 16진법
    image_bytes = cur.execute(f"""
                              SELECT image from items WHERE id={item_id}
                              """).fetchone()[0]
    return Response(content=bytes.fromhex(image_bytes), media_type='image/*')

@app.post('/signup')
def signup(id:Annotated[str,Form()],
           password:Annotated[str,Form()],
           name:Annotated[str,Form()],
           email:Annotated[str,Form()]):
    cur.execute(f"""
                INSERT INTO users(id,name, email, password)
                VALUES ('{id}','{name}','{email}','{password}')
                """)
    
    con.commit()
    return '200'
    
@app.get('/getId/{id}')
async def get_id(id):
    # 아이디 중복체크
    print("아이디 중복체크");
    cur = con.cursor();
    getid = cur.execute(f"""
                       SELECT COUNT(id) FROM users WHERE id={id};
                       """).fetchone()[0]
    
    return  Response(getid)

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
