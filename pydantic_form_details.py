from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import date

class UniversityCreate(BaseModel):
    name: str

class CollegeCreate(BaseModel):
    name: str
    uni_name: str

class CourseCreate(BaseModel):
    name: str

class AssignCourse(BaseModel):
    college_id: int
    course_id: int

class StudentCreate(BaseModel):
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

class CollegeSchma(BaseModel):
    id: int
    name:str
    courses : list
    class Config:

        from_attributes = True

class UniversitySummary(BaseModel):
    id :int
    name : str
    colleges : List[CollegeSchma]

    class Config:

        from_attributes = True

class CourseSchema(BaseModel):
    course_id : int
    course_name : str
    marks : float

class SemesterSchema(BaseModel):
    id : int
    term : str
    courses : List[CourseSchema]
    class Config:
        from_attributes=True

class StudentPerformance(BaseModel):
    id: int
    semesters: List[SemesterSchema]
    class Config:
        from_attributes=True

class CourseEnrollment(BaseModel):
    course_id: int
    count: int

class CoursePerformance(BaseModel):
    course_id: int
    course_name: str
    min_marks: float
    avg_marks: float
    max_marks: float

class CollegePerformance(BaseModel):
    id: int
    performance: List[CoursePerformance]
    class Config:
        from_attributes = True

class CourseTopper(BaseModel):
    student_id: int
    course_id: int
    maxmarks: float

class CourseDetails(BaseModel):
    course_id: int
    course_name: str

class CurrentSemester(BaseModel):
    id: int
    term: str
    courses: List[CourseDetails]
    class Config:
        from_attributes = True

class StudentDetails(BaseModel):
    id: int
    name: str
    current_semester: CurrentSemester
    previous_semesters: List[SemesterSchema]
    class Config:
        from_attributes = True

class UniversityTopper(BaseModel):
    id: int
    name: str
    student_id: int
    student_name: str
    topped_courses: List[CourseSchema]
    class Config:
        from_attributes = True

class Scholarship_NoHigher(BaseModel):
    student_id: int
    name: str
    aggregate: float

class CombinedResponse(BaseModel):
    scholarship: List[Scholarship_NoHigher]
    no_higherstudies: List[Scholarship_NoHigher]
    class Config:
        from_attributes = True

class Publish_marks(BaseModel):
    student_reg: str
    student_name: str
    dob: date
    semester_id: int
    semester_name: str
    course_details: List[CourseSchema]
    aggregate: float
    scholarship: bool
    higherstudies: bool
    class Config:
        from_attributes = True

class CourseStudents(BaseModel):
    student_id: int
    student_name: str
    marks: float
