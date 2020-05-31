import pymongo
import datetime
from bson import ObjectId
from db.validation import validate
from db.student import StudentJson
from db.user import User
from flask_caching import Cache


class Datalayer:

    def __init__(self,app):
        self.__client = pymongo.MongoClient('localhost', 27017)
        self.__db = self.__client["Hogwarts"]
        list_skills = self.__db.info.find_one({"name": "list_skills"})
        house_list = self.__db.info.find_one({"name": "house_list"})
        self.Validation = validate(list_skills["list"], house_list["list"])
        cache = Cache(config={'CACHE_TYPE': 'simple', 'CACHE_THRESHOLD': 1000})
        cache.init_app(app)
        self.__cache = cache

    def getStudents(self):
        students_cached=self.__cache.get("list")
        if students_cached :
            return students_cached
        else:
            students = self.__db.students.find()
            newlist = []
            for x in students:
                newlist.append(x)
            self.__cache.set("list", newlist)
            return newlist

    def addStudent(self, student):
        validation = self.Validation.validateStudent(student)
        if validation["response"] == "ok":
            student_to_add = StudentJson(student)
            json_student=student_to_add.makeADict()
            self.__db.date.insert_one({"student":json_student["firstName"] ,"date":json_student["createdDate"]})
            stu=self.__db.students.insert_one(json_student)
            self.__cache.set(stu.inserted_id,json_student)
            return {"response": "ok", "status": 200}
        return {"response": "bad", "status": 400, "message": validation["message"]}

    def getStudentById(self, id):
        if len(id) < 24:
            return False
        student_cached = self.__cache.get(id)
        if student_cached :
            print("I'm cached")
            return student_cached
        else:
            student = self.__db.students.find_one({"_id": ObjectId(id)})
            if student:
                self.__cache.set(id, student, timeout=30)
            print("I'm not cached")
            return student

    def registerUser(self, user):
        validation = self.Validation.ValidationUser(user)
        if validation["response"] == "ok":
            duplicate = self.__db.users.find_one({"username": user["username"]})
            if duplicate:
                return {"response": "bad", "status": 400, "message": "username already exists in the database"}
            if user["admin"] and user["code"] != self.__db.info.find_one(({"name":"secret_code"}))["code"]:
                return {"response":"bad","status":400,"message":"wrong secret code"}
            if (not user["admin"]) and  (self.__db.students.find_one({"firstName":user["firstName"],"lastName":user["lastName"]}) is None):
                return {"response":"bad","status":400,"message":"The user is not in the database"}
            user_to_add = User(user)
            self.__db.users.insert_one(user_to_add.makeADict())
            return {"response": "ok", "status": 200}
        return {"response": "bad", "status": 400, "message": validation["message"]}

    def findUser(self, username, password):
        user = self.__db.users.find_one({"username": username, "password": password})
        if user:
            return {"response":"ok","data":user,"status":200}
        else:
             return {"response":"bad","message":"no user found","status":400}

    def deleteStudent(self, id, password):
        secret_code = self.get_code()
        if password == secret_code["code"]:
            try:
                user = self.__db.students.delete_one({"_id": ObjectId(id)})
                self.__cache.delete(id)
                self.__cache.delete("list")
                return {"status": "ok", "code": 200}
            except Exception as e:
                print(e)
                return {"status": "bad", "message": "wrong id", "code": 400}
        else:
            return {"status": "bad", "message": "wrong code", "code": 400}

    def get_student_today(self, date):
        students = self.__db.date.find({"date": str(date)})
        return students

    def get_magic_skills(self, type):
        newdict = {"Metamorphmagi": 0, "Animagus": 0, "Potion": 0, "Apparition": 0, "Wandless_Magic": 0,
                   "Legilimency_And_Occlumency": 0}
        students = self.getStudents()
        for student in students:
            for skill in student[type]:
                newdict[skill] += 1

        return newdict

    def get_top(self):
        students = self.__db.students.find()
        newstudents = []
        for x in students:
            m = 0
            for level in x["magicskills"].values():
                m += level
            m = m / len(x["magicskills"].keys())
            newstudents.append({"firstName": x["firstName"], "lastName": x["lastName"], "m": m})
        newlist = sorted(newstudents, key=lambda k: k['m'], reverse=True)
        return newlist[0:3]

    def get_student_by_name(self, name):
        students = self.__db.students.find()
        newlist = []
        if students:
            for student in students:
                self.__cache.set(student["_id"] , student)
                newlist.append(student)

            sortedStudents = [k for k in newlist if name.lower() in k["lastName"].lower()]
            classstudents=  sorted(sortedStudents, key=lambda student: student["lastName"].lower())
            return classstudents
        else:
            return False

    def get_code(self):
        return self.__db.info.find_one({"name": "secret_code"})

    def update_date_student(self, id):
        student=self.__db.students.update({"_id": ObjectId(id)}, {"$set": {"lastUpdate": str(datetime.date.today())}})
        self.__cache.delete(id)
        student=self.getStudentById(id)
        self.__cache.set(id,student)

    def get_user(self,username):
        user =self.__db.users.find_one({"username":username})
        return user

    def update_student(self,student):
        try:
            student["_id"]=ObjectId(student["_id"])
            validation = self.Validation.validateStudent(student)
            if validation["response"] == "ok":
                self.__db.students.update({"_id":ObjectId(student["_id"])}, student)
                self.__cache.set(student["_id"], student)
                self.__cache.delete("list")
                return ({"response":"everything is ok" , "status":200})
            return {"response": "bad", "status": 400, "message": validation["message"]}
        except Exception as e :
            print(e)
            return {"response" :"data is badly formated" ,"status":400}