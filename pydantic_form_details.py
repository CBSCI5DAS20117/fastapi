from pydantic import BaseModel

class UniversityCreate(BaseModel):
    name: str

class CollegeCreate(BaseModel):
    name: str
    uni_name: str

class CourseCreate(BaseModel):
    name: str
    college_name: str

class StudentCreate(BaseModel):
    user_id: int
    name: str
    uni_id: int

class SemesterCreate(BaseModel):
    term: str

class MarkCreate(BaseModel):
    student_id: int
    term: str
    course_id: int
    mark: float

class EnrollmentCreate(BaseModel):
    student_id: int
    term: str
    course_id: int
    college_id: int