class validate:

    def __init__(self, list_skills , house_list):
        self.houseList = house_list
        self.StudentKeys = ["firstName", "lastName", "magicskills", "desired_skills", "course"]
        self.magic_skills = list_skills
        self.Userkeys = ["firstName", "lastName", "username", "house", "year","password","admin"]

    def validateStudent(self, student):
            if not all(key in student.keys() for key in self.StudentKeys):
                return {"response": "bad", "message": "missing data"}
            if type(student["firstName"]) is not str or len(student["firstName"]) < 2:
                return {"response": "bad", "message": "First Name must be at least 3 letters"}
            if type(student["lastName"]) is not str or len(student["lastName"]) < 2:
                return {"response": "bad", "message": "Last Name must be at least 3 letters"}
            if not (type(student["magicskills"]) is dict and all(
                    key in student["magicskills"].keys() for key in self.magic_skills)):
                return {"response": "bad", "message": "The magic skills are badly formated or they are missing values"}
            if not (type(student["desired_skills"]) is dict and all(
                    key in student["desired_skills"].keys() for key in self.magic_skills)):
                return {"response": "bad",
                        "message": "the desired magic skills are baddly formated or they are are missing values"}
            if type(student["course"]) is not list or len(student["course"])==0:
                return {"response": "bad", "message": "the course are badly formated"}
            return {"response": "ok", "message": "all is perfect"}

    def ValidationUser(self, user):
            if not all(key in user.keys() for key in self.Userkeys):
                return {"response": "bad", "message": "missing data"}
            if len(user["firstName"]) < 2:
                return {"response": "bad", "message": "firstName must be at least 3 letters"}
            if len(user["lastName"]) < 2:
                return {"response": "bad", "message": "lastNameName must be at least 3 letters"}
            if len(user["username"]) < 3:
                return {"response": "bad", "message": "User Name must be at least 4 letters"}
            if user["house"] not in self.houseList:
                return {"response": "bad", "message": "The house specified does not exist"}
            if len(user["password"])<6:
                return {"response":"bad","message":"the password must be at least 6 letters"}
            if not (type(user["year"]) is int and 1 <= user["year"] <= 7):
                return {"response": "bad", "message": "The year specified is not revealant"}
            if type(user["admin"]) is not bool :
                return {"response":"bad" , "message":"The admin must be true or false"}
            if user["admin"] and "code" not in user.keys():
                return {"response": "bad", "message": "The code was forgotten"}
            return {"response": "ok", "message": "all is perfect"}

