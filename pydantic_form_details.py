from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import date

class LoginCreate(BaseModel):
    access_token: str
    username: str
    token_type: str

class Options(BaseModel):
    name: list[str]

class StudentDetails(BaseModel):
    name: str
    dob: date
    qualification: str
    address: str
    university: str
    college: str 
    course:  str
    reg_num:  str
    date:  date

class CollegeDetails(BaseModel):
    name: str
    zip:  str
    city:  str
    state: str
    phone: str
    code: str


class UniversityDetails(BaseModel):
    University_code: str
    University_address: str
    college_details: List[CollegeDetails]
    class Config:

        from_attributes = True

class CourseCreate(BaseModel):
    name: str
    course_num: str

class AssignCourse(BaseModel):
    university_id: int
    course_id: int

class StudentAdmission(BaseModel):
    name: str
    dob: date
    qualification: str
    address:str
    uni: str
    college: str
    course: str

class SemesterCreate(BaseModel):
    term: str

class MarkCreate(BaseModel):
    student_id: int
    term: str
    subject_id: int
    mark: float

class EnrollmentCreate(BaseModel):
    student_id: int
    term: str
    course_id: int
    university_id: int
    subject_id: int

class SubjectCreate(BaseModel):
    name: str
    course_id: int
    semester_id: int
    university_id: int

class CourseList(BaseModel):
    id: int
    name:str
    register_number: str
    subjects : list
    class Config:

        from_attributes = True

class UniversitySummary(BaseModel):
    id :int
    name : str
    courses : List[CourseList]

    class Config:

        from_attributes = True

class CourseSchema(BaseModel):
    subject_id : int
    subject_name : str
    marks : float

class SemesterSchema(BaseModel):
    id : int
    term : str
    subjects : List[CourseSchema]
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

class SubjectPerformance(BaseModel):
    id: int
    name: str
    min_marks: float
    avg_marks: float
    max_marks: float

class CoursePerformance(BaseModel):
    course_id: int
    course_name: str
    subjects: SubjectPerformance
    class Config:
        from_attributes = True

class CollegePerformance(BaseModel):
    id: int
    name: str
    performance: List[CoursePerformance]
    class Config:
        from_attributes = True

class CourseTopper(BaseModel):
    student_id: int
    student_name: str
    university_name: str


class CourseDetails(BaseModel):
    course_id: int
    course_name: str

class CurrentSemester(BaseModel):
    id: int
    term: str
    courses: List[CourseDetails]
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

class HostelCreate(BaseModel):
    hostel_name: str
    type: str
    latitude: float
    longitude: float
    phone: str


class ListHostels(BaseModel):
    hostel_id: int
    hostel_name: str
    type: str
    distance: float

class StudentEnrollments(BaseModel):
    student_id: int
    student_name: str
    
class CollegeEnrollments(BaseModel):
    course_id: int
    course_name: str
    students: List[StudentEnrollments]
    class Config:
        from_attributes = True