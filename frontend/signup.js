const form = document.querySelector("#signup-form");
// const div = document.querySelector("#info");

const checkPassword = () => {
  const formData = new FormData(form);
  const password1 = formData.get("password");
  const password2 = formData.get("password2");

  if (password1 === password2) {
    return true;
  } else return false;
};

const checkId = async (event) => {
  console.log("시작");
  const formData = new FormData(form);
  const getId = formData.get("id");
  console.log(getId);

  const cnt = await fetch("/getId/" + getId);

  console.log(cnt);
  if (cnt > 0) {
    div.innerText = "다른아이디를 사용하세요!!";
  } else {
    div.innerText = "사용가능한 아이디입니다!!";
  }
};

const checkBtn = document.querySelector("#check");
checkBtn.addEventListener("click", checkId);

const handleSubmit = async (event) => {
  event.preventDefault();
  const formData = new FormData(form);
  const sha256Password = sha256(formData.get("password"));
  formData.set("password", sha256Password);

  const div = document.querySelector("#info");

  if (checkPassword()) {
    const res = await fetch("/signup", {
      method: "post",
      body: formData,
    });
    const data = await res.json();

    if (data === "200") {
      // div.innerText = "회원가입에 성공했습니다.";
      // div.style.color = "blue";
      alert("회원가입에 성공했습니다.");
      window.location.pathname = "/login.html";
    }
  } else {
    div.innerText = "비밀번호가 같지 않습니다.";
    div.style.color = "red";
  }
};

form.addEventListener("submit", handleSubmit);
