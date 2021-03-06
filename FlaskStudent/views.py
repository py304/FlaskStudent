"""
视图和路由文件
"""
import hashlib
from flask import jsonify
from flask import request
from flask import redirect

from flask import render_template
from FlaskStudent.main import app
from FlaskStudent.models import *
from FlaskStudent.main import csrf
from FlaskStudent.main import session
from FlaskStudent.forms import TeacherForm


def SetPassword(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    return md5.hexdigest()

def loginValid(fun):
    def inner(*args,**kwargs):
        cookie_username = request.cookies.get("username")
        id = request.cookies.get("user_id")
        session_username = session.get("username")
        if cookie_username and id and session_username:
            if cookie_username == session_username:
                fun(*args,**kwargs)
        return redirect('/login/')
    return inner

@csrf.exempt
@app.route("/register/",methods=["GET","POST"])
def register():
    if request.method == 'POST':
        form_data = request.form
        username = form_data.get("username")
        password = form_data.get("password")
        identity = form_data.get("identity")

        user = User()
        user.username = username
        user.password = SetPassword(password)
        user.identity = int(identity)
        user.save()

        return redirect('/login/')
    return render_template("register.html")

@app.route("/login/",methods=["GET","POST"])
def login():
    if request.method == "POST":
        form_data = request.form
        username = form_data.get("username")
        password = form_data.get("password")

        user = User.query.filter_by(username=username).first()
        if user:
            db_password = user.password
            md5_password = SetPassword(password)
            if md5_password == db_password:
                # 验证成功，跳转首页
                response = redirect('/index/')
                # 设置cookie
                response.set_cookie("username",username)
                response.set_cookie("user_id",str(user.id))
                # 设置session
                session["username"] = username
                # 返回跳转页面
                return response
    return render_template("login.html")

@app.route("/index/")
@loginValid
def index():
    # print(session.get('username'))
    return render_template("index.html")

@app.route("/logout/",methods=["GET","POST"])
def logout():
    response = redirect('/login/')
    for key in request.cookies:
        response.delete_cookie(key)
    del session["username"]
    return response

# @csrf.exempt # 临时关闭csrf校验
@app.route("/add_teacher/",methods=["GET","POST"])
def add_teacher():
    teacher_form = TeacherForm()
    if request.method == "POST":
        name = request.form.get("name")
        age = request.form.get("age")
        gender = request.form.get("gender")
        course = request.form.get("course")

        teacher = Teacher()
        teacher.name = name
        teacher.age = age
        teacher.gender = gender
        teacher.course_id = course
        teacher.save()
    return render_template("add_teacher.html",**locals())

# csrf 如果没有配置跳转的错误页面
@csrf.error_handler
@app.route("/csrf_403/")
def csrf_tonken_error(reason):
    return render_template("csrf_403.html")

# ajax 前端校验
@app.route("/userValid/",methods=["GET","POST"])
def userValid():
    # 定义json字典数据格式
    result = {
        "code":"",
        "data":""
    }
    if request.method == "POST":
        username = request.form.get("username")
        if username:
            user = User.query.filter_by(username=username).first()
            if user:
                result["code"] = 400
                result["data"] = "用户名已存在"
            else:
                result["code"] = 200
                result["data"] = "用户名未被注册，可以使用"
    return jsonify(result)

@app.route("/student_list/")
def student_list():
    students = Student.query.all()
    return render_template("student_lists.html",**locals())



