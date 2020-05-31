from flask import Flask, jsonify, request, render_template, json ,redirect, url_for, escape
import jwt
from db.datalayer import Datalayer
from flask_cors import CORS
from functools import wraps
import datetime
session={}


app = Flask(__name__)
app.config["SECRET_KEY"]="My_KEY"
CORS(app)
datalayer = Datalayer(app)
def check_for_token(func):
    @wraps(func)
    def wrapped(*args , **kwargs):
        token=request.headers.get("Authorization")
        if not  token :
            return jsonify({"message" :"Missing Token"}),403
        try:
            data=jwt.decode(token , app.config["SECRET_KEY"])
        except:
            return jsonify({"message":"invalid token"})
        return func(*args,**kwargs)
    return wrapped


@app.route("/students")
@check_for_token
def get_students():
        students = datalayer.getStudents()
        response = app.response_class(response=json.dumps({"data": students}, default=str),
                                      status=200,
                                      mimetype="application/json")
        return response


@app.route("/students/<id>")
@check_for_token
def get_student_by_id(id):
    student = datalayer.getStudentById(id)
    if student:
        datalayer.update_date_student(id)
        response = app.response_class(response=json.dumps({"data": student}, default=str),
                                    status=200,
                                    mimetype="application/json")
        return response

    else:
        response=app.response_class(response=json.dumps({"data":"no user found"}),
                                      status=400,
                                      mimetype="application/json")
        return response


@app.route("/add/student", methods=["GET", "POST"])
@check_for_token
def addStudent():
        content = request.json
        result = datalayer.addStudent(content)
        response = app.response_class(response=json.dumps(result),
                                      status=result["status"],
                                      mimetype="application/json"
                                      )
        return response




@app.route("/student/register", methods=["GET", "POST"])
def student_register():
    form = request.json
    if (request.method == "POST"):
        result =datalayer.registerUser(form)
        if result["status"]==200 :
            token = jwt.encode({
                "user": form["username"],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
            },
                app.config["SECRET_KEY"])
            result["token"] = token.decode("utf-8")
        response=app.response_class(response=json.dumps(result),
                                    status=result["status"],
                                    mimetype="application/json")
        return response


@app.route("/student/login/username/<username>/password/<password>",methods=["GET","POST"])
def user_log_in(username, password):
    response = datalayer.findUser(username, password)
    if response["status"]==200:
        token=jwt.encode({
            "user":response["data"]["username"],
            "exp":datetime.datetime.utcnow()+datetime.timedelta(hours=2)
        },
        app.config["SECRET_KEY"])
        response["token"]=token.decode("utf-8")
    res = app.response_class(response=json.dumps(response ,default=str),
                             status=response["status"],
                             mimetype="application/json")
    return res


@app.route("/delete/student/<id>/code/<code>")
@check_for_token
def delete_user(id,code):
        student = datalayer.deleteStudent(id,code)
        response = app.response_class(response=json.dumps(student),
                                    status=student["code"],
                                    mimetype="application/json")
        return response

@app.route("/students/added/today/<date>")
@check_for_token
def get_student_added(date):
        count=0
        newlist=[]
        students=datalayer.get_student_today(date)
        if students:
            count=students.count()
            for student in students:
                    newlist.append(student)
            response=app.response_class(response=json.dumps({"data":newlist,"count":count},default=str),
                                        status=200,
                                        mimetype="application/json")
        else:
            response=app.response_class(response=json.dumps({"error":"no students added today"}),
                                        status=400,
                                        mimetype="application/json")


        return response


@app.route("/get/magicskills")
@check_for_token
def get_magicskills():
        newdict=datalayer.get_magic_skills("magic_skills_aquired")
        response=app.response_class(response=json.dumps(newdict),
                                    status=200,
                                    mimetype="application/json")
        return response

@app.route("/get/desiredskills")
@check_for_token
def get_desiredskills():
        newdict=datalayer.get_magic_skills("desired_skills_aquired")
        response=app.response_class(response=json.dumps(newdict),
                                    status=200,
                                    mimetype="application/json")
        return response


@app.route("/get/10")
@check_for_token
def gettop():
        newlist=datalayer.get_top()
        response=app.response_class(response=json.dumps({"data":newlist}),
                                    status=200,
                                    mimetype="application/json")
        return response

@app.route("/get/student/name/<name>")
@check_for_token
def student_by_name(name):
        students=datalayer.get_student_by_name(name)
        if students and len(students)>0:
            response=app.response_class(response=json.dumps({"data":students}, default=str),
                                        status=200,
                                        mimetype="application/json"
                                        )
        else:
            response=app.response_class(response=json.dumps({"message":"No Students Found"}),
                                        status=400,
                                        mimetype="application/json")
        return response

@app.route("/get/session/<token>")
def get_session(token):
    try:
        data = jwt.decode(token, app.config["SECRET_KEY"])
        user=datalayer.get_user(data["user"])
        return app.response_class(response=json.dumps(user,default=str),
                                  status=200,
                                  mimetype="application/json"
                                  )
    except Exception as e:
        print(e)
        return jsonify({"message": "invalid token"}),400

@app.route("/get/code")
@check_for_token
def get_code():
        code=datalayer.get_code()
        ressponse=app.response_class(response=json.dumps({"code":code["code"]}),
                                     status=200,
                                     mimetype="application/json")
        return ressponse
@app.route("/update/student" ,methods=["GET", "POST"])
@check_for_token
def update_student():
    student=request.json
    response=datalayer.update_student(student)
    return  app.response_class(response=json.dumps(response),
                               status=response["status"],
                               mimetype="application/json")


if __name__ == "__main__":
    app.run(debug=True)
