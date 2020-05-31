import datetime
import json
class BaseStudent:
    def __init__(self,student):
        self.firstName=student["firstName"]
        self.lastName=student["lastName"]
        self.magicskills=student["magicskills"]
        self.desired_skills=student["desired_skills"]
        self.course=student["course"]

class ExtendedStudent(BaseStudent):

    def __init__(self,student):
        super().__init__(student)
        self.createdDate=str(datetime.date.today())
        self.lastUpdate=str(datetime.date.today())
        newlist=[]
        for skill , grade  in student["magicskills"].items():
            if grade>=3:
                newlist.append(skill)
        desired_list=[]
        for skill , grade  in student["desired_skills"].items():
            if grade>=3:
                desired_list.append(skill)
        self.magic_skills_aquired=newlist
        self.desired_skills_aquired=desired_list
class StudentJson(ExtendedStudent):

    def __init__(self,student):
        super().__init__(student)

    def makeADict(self):
        return json.loads(json.dumps(self.__dict__))


