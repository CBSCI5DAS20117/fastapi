from fastapi import FastAPI, Depends, HTTPException, Query
from authentication import  get_current_user, create_access_token
from user import User, session, University, College, Course, Student, Semester, Enrollment, Marks, Course_College
import uvicorn
from fastapi.security import OAuth2PasswordRequestForm
from pydantic_form_details import UniversityCreate, CollegeCreate, CourseCreate, StudentCreate, SemesterCreate, MarkCreate, EnrollmentCreate, AssignCourse
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import select
from sqlalchemy import func
import pandas as pd

app = FastAPI()

@app.get("/")
async def read_root():
    return {'message':'Welcome to fastapi-authentication'}

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    users = session.query(User).filter(User.username == form_data.username).all()
    if users is None:
        raise HTTPException(status_code=400, detail="Incorrect Username or Password")
    else:
        for user in users:
            if user.check_password(form_data.password):
                access_token = create_access_token(data = {"sub":user.username, "userid":user.id})
        
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/protected")
async def protected_route(userinfo: dict = Depends(get_current_user)):
    username = userinfo['username']
    userid = userinfo['userid']
    return {"message":f"Hello, {username} with user ID {userid} ! This is a protected resource."}

@app.post("/create_University")
async def Create_University(form_data: UniversityCreate):
    new_university = University(name = form_data.name)
    session.add(new_university)
    session.commit()

    return {"message":"New University created"}

@app.post("/create_College")
async def Create_College(form_data: CollegeCreate):
    university = session.query(University).filter(University.name == form_data.uni_name).first()
    if university is None:
        raise HTTPException(status_code=404, detail="University not found")
    new_college = College(name = form_data.name, uni_id = university.id)
    session.add(new_college)
    session.commit()

    return {"message":"New College created"}

@app.post("/create_Course")
async def Create_Course(form_data: CourseCreate):
    new_course = Course(name = form_data.name)
    session.add(new_course)
    session.commit()

    return {"message":"New Course created"}

@app.post("/assign_course_to_college")
async def Assign_Course_to_College(form_data: AssignCourse):
    course = session.query(Course).get(form_data.course_id)
    college = session.query(College).get(form_data.college_id)

    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    if college is None:
        raise HTTPException(status_code=404, detail="College not found")
    cc = session.query(Course_College).filter(Course_College.college_id == college.id, Course_College.course_id == course.id).first()
    if cc:
        raise HTTPException(status_code=409, detail="This course is already assigned to this college")
        
    new_cc = Course_College(course_id = course.id, college_id = college.id)
    session.add(new_cc)
    session.commit()
    
    return {"message": "Course assigned to college"}

@app.post("/create_Student")
async def Create_Student(form_data: StudentCreate):
    user = session.query(User).filter(User.id == form_data.user_id).first()
    university = session.query(University).get(form_data.uni_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if university is None:
        raise HTTPException(status_code=404, detail="University not found")
    new_student = Student(name = form_data.name, user_id = user.id, uni_id = university.id)
    session.add(new_student)
    session.commit()

    return {"message":"New Student created"}

@app.post("/create_Semester")
async def Create_Semester(form_data: SemesterCreate):
    new_semester = Semester(term = form_data.term)
    session.add(new_semester)
    session.commit()

    return {"message":"New Semester created"}

@app.post("/create_Mark")
async def Create_Mark(form_data: MarkCreate):
    student = session.query(Student).filter(Student.id == form_data.student_id).first()
    semester = session.query(Semester).filter(Semester.term == form_data.term).first()
    course = session.query(Course).filter(Course.id == form_data.course_id).first()
    if student is None or course is None:
        raise HTTPException(status_code=404, detail="Student or Course not found")
    enrollment = session.query(Enrollment).filter(Enrollment.student_id == student.id, Enrollment.semester_id == semester.id, Enrollment.course_id == course.id).first()
    if enrollment is None:
        raise HTTPException(status_code=404, detail = "Student has not been enrolled for this course in this semester. So mark cannot be entered")
    new_mark = Marks(student_id = student.id,semester_id = semester.id, course_id = course.id, mark = form_data.mark)
    session.add(new_mark)
    session.commit()

    return {"message":"Mark Updated"}

@app.post("/create_Enrollment")
async def Create_Enrollment(form_data: EnrollmentCreate):
    student = session.query(Student).filter(Student.id == form_data.student_id).first()
    semester = session.query(Semester).filter(Semester.term == form_data.term).first()
    course = session.query(Course).filter(Course.id == form_data.course_id).first()

    college = session.query(College).get(form_data.college_id)
    if student is None or course is None or semester is None or college is None:
        raise HTTPException(status_code=404, detail="Student or Course or semeter or college not found")
    if college.uni_id != student.uni_id:
        raise HTTPException(status_code = 404, detail = "Student is not part of that university")
    enrollment = session.query(Enrollment).filter(Enrollment.student_id == student.id, Enrollment.course_id == course.id).first()
    if enrollment:
        raise HTTPException(status_code=409, detail="Student has already enrolled or completed this course")
    cc = session.query(Course_College).filter(Course_College.course_id == course.id, Course_College.college_id == college.id).first()
    if cc is None:
        raise HTTPException(status_code=409, detail="This course is not currently offered by this college")
    new_enrollment = Enrollment(student_id = student.id,semester_id = semester.id, course_id = course.id, college_id = college.id)
    session.add(new_enrollment)
    session.commit()

    return {"message":"Student Enrolled"}
# Student details: name, uni_name, enrollment details, marks, subjects taken and from which college they are taken in each semester
@app.get("/student_details")
async def student_details(student_id: int = Query(..., description="Student details")):
    std_list = []
    # Retrieve the student along with their enrollments and related data using eager loading
    
    student = session.query(Student).options(
            joinedload(Student.enrollments).joinedload(Enrollment.semesters),
            joinedload(Student.enrollments).joinedload(Enrollment.courses),
            joinedload(Student.enrollments).joinedload(Enrollment.colleges),
            joinedload(Student.marks)
        ).filter(Student.id == student_id).one_or_none()

    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    for enrollment in student.enrollments:
        semester = enrollment.semesters
        course = enrollment.courses
        college = enrollment.colleges
            
        
        marks = next(
            (m for m in student.marks if m.semester_id == semester.id and m.course_id == course.id),
             None
        )
        enrollment_details = {
            'ID': student.id,
            'Name': student.name,
            'Semester': semester.term,
            'Course ID': course.id,
            'Course Name': course.name,
            'College': college.name,
            'Marks': marks.mark if marks else 'N/A'
        }
        std_list.append(enrollment_details)

    return std_list

@app.get("/find_coursetopper_semester")
async def Find_CourseTopper_Semester(course_id: int = Query(..., description = 'Course ID'), semester_id: int = Query(..., description = 'Semester ID')):
    #max_mark = session.query(func.max(Marks.mark)).filter(Marks.course_id == course_id, Marks.semester_id == semester_id).scalar()
    max_mark = (
        select(func.max(Marks.mark)).filter(Marks.course_id == course_id, Marks.semester_id == semester_id).scalar_subquery()
    )
    max_mark_student = (
        select(Marks.student_id).filter(Marks.mark.in_(max_mark)).subquery()
    )
    #mark = session.query(Marks).filter(Marks.course_id == course_id, Marks.semester_id == semester_id, Marks.mark == max_mark).one_or_none()
    student = (select(Student).filter(Student.id.in_(max_mark_student)))
    student_execute = session.execute(student).scalars().one_or_none()
    return student_execute.name

@app.get("/find_uniTopper_semester")
async def Find_UniTopper_Semester(semester_id: int = Query(..., description='Semester ID'), uni_id: int = Query(..., description='University ID')):
    # Subqueries for college ids and course ids
    subquery_colleges = (
        select(College.id).filter(College.uni_id == uni_id).subquery()
    )
    #subquery_courses = (
    #    select(Course.id).join(Course.colleges).filter(College.id.in_(subquery_colleges)).distinct().subquery()
    #)
    subquery_courses = (
        select(Course.id).join(Course_College).filter(Course_College.college_id.in_(subquery_colleges)).distinct().subquery()
    )
    # Subquery to find max marks in each course in a semester
    subquery_maxmarks = (
        select(Marks.course_id, func.max(Marks.mark).label('Max_Mark')).filter(Marks.semester_id == semester_id).group_by(Marks.course_id).subquery()
    )
    # subquery to get student ids with max marks
    subquery_student_maxmarks = (
        select(Marks.student_id).join(subquery_maxmarks, (Marks.course_id == subquery_maxmarks.c.course_id)&(Marks.mark == subquery_maxmarks.c.Max_Mark)
                                      ).subquery()
    )
    #Query to find student names
    student_maxmarks = (select(Student.name).join(Marks, Student.id == Marks.student_id).filter(Marks.student_id.in_(subquery_student_maxmarks))
                     .filter(Marks.course_id.in_(subquery_courses))
                     )
    student_names = session.execute(student_maxmarks).scalars().all()
    
    # Compute frequency of each student name
    series = pd.Series(student_names)
    frequency = series.value_counts()
    max_frequency = frequency.max()
    university_topper = frequency[frequency == max_frequency].index.tolist()
    
    return university_topper

@app.get("/college_under_which_university")
async def College_Under_Which_University(college_name: str = Query(..., description = "Name of College")):
    college = session.query(College).filter(College.name == college_name).first()
    if college is None:
        raise HTTPException(status_code=404, detail="College not found")
    university = session.query(University).get(college.uni_id)
    
    return {"This college is under":university.name}


@app.get("/get_University")
async def Get_University():
    all_uni = session.query(University).all()
    uni_details = []

    for uni in all_uni:
        uni_details.append({"ID": uni.id,
                            "Name": uni.name})
        
    return uni_details

@app.get("/get_College")
async def Get_College():
    all_college = session.query(College).all()
    college_details = []

    for college in all_college:
        college_details.append({"ID": college.id,
                            "Name": college.name,
                            "Uni_name": college.university.name})
        
    return college_details

@app.get("/get_Course")
async def Get_Course():
    all_course = session.query(Course).all()
    course_details = []

    for course in all_course:
        cc = session.query(College).join(Course_College).filter(Course_College.college_id == College.id, Course_College.course_id == course.id).all()
        college_names = [college.name for college in cc]
        course_details.append({"ID": course.id,
                            "Name": course.name,
                            "College_name": college_names if college_names else ['No colleges Available']})
        
    return course_details

if __name__ == '__main__':
    uvicorn.run("main:app",host="127.0.0.1",port=8000,reload=True)
