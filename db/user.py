import json
class User:
    def __init__(self,user):
        self.firstname=user["firstName"]
        self.lastname=user["lastName"]
        self.username=user["username"]
        self.house=user["house"]
        self.year=user["year"]
        self.password=user["password"]
        self.admin=user["admin"]

    def makeADict(self):
        return json.loads(json.dumps(self.__dict__))
