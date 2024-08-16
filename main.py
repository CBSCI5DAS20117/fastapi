from fastapi import FastAPI, Depends, HTTPException, Query
from authentication import  get_current_user, create_access_token
#from user import session, University, College, Course, Student, Semester, Enrollment, Marks,User, Course_College
from user1 import session, University, College, Course, Student, Semester, Enrollment, Marks, course_college, engine
import uvicorn
from fastapi.security import OAuth2PasswordRequestForm
from pydantic_form_details import CourseStudents,Publish_marks,Scholarship_NoHigher,CombinedResponse,UniversityCreate,UniversityTopper,StudentDetails,CurrentSemester,CourseDetails,CourseTopper,CollegePerformance,CoursePerformance,CourseEnrollment,CourseEnrollment,CourseSchema,SemesterSchema,StudentPerformance,CollegeSchma,UniversitySummary, CollegeCreate, CourseCreate, StudentCreate, SemesterCreate, MarkCreate, EnrollmentCreate, AssignCourse
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import select
from sqlalchemy import func, desc
from typing import List, Union
# from collections import Counter
import json

app = FastAPI()

@app.get("/")
async def read_root():
    return {'message':'Welcome to fastapi-authentication'}
'''
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
'''

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
    #college.courses.append(new_course)
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
    course.colleges.append(college)
    session.commit()
    
    return {"message": "Course assigned to college"}

@app.post("/create_Student")
async def Create_Student(form_data: StudentCreate):
    university = session.query(University).get(form_data.uni_id)
    if university is None:
        raise HTTPException(status_code=404, detail="University not found")
    new_student = Student(name = form_data.name ,uni_id = university.id)
    session.add(new_student)
    session.commit()

    return {"message":"New Student created"}

@app.post("/create_Semester")
async def Create_Semester(form_data: SemesterCreate):
    new_semester = Semester(term = form_data.term)
    session.add(new_semester)
    session.commit()

    return {"message":"New Semester created"}

@app.post("/create_Enrollment")
async def Create_Enrollment(form_data: EnrollmentCreate):
    student = session.query(Student).filter(Student.id == form_data.student_id).first()
    semester = session.query(Semester).filter(Semester.term == form_data.term).first()
    course = session.query(Course).filter(Course.id == form_data.course_id).first()

    college = session.query(College).get(form_data.college_id)
    if student is None or course is None or semester is None or college is None:
        raise HTTPException(status_code=404, detail="Student or Course or semester or college not found")
    if college.uni_id != student.uni_id:
        raise HTTPException(status_code = 404, detail = "Student is not part of that university")
    enrollment = session.query(Enrollment).filter(Enrollment.student_id == student.id, Enrollment.course_id == course.id).first()
    if enrollment:
        raise HTTPException(status_code=409, detail="Student has already enrolled or completed this course")
    stmt = select(course_college).where(
        course_college.c.course_id == course.id,
        course_college.c.college_id == college.id
    )
    result = session.execute(stmt).fetchone()
    if result is None:
        raise HTTPException(status_code=409, detail="This course is not currently offered by this college")
    new_enrollment = Enrollment(student_id = student.id,semester_id = semester.id, course_id = course.id, college_id = college.id)
    session.add(new_enrollment)
    session.commit()

    return {"message":"Student Enrolled"}

@app.post("/create_Mark")
async def Create_Mark(form_data: MarkCreate):
    student = session.query(Student).filter(Student.id == form_data.student_id).first()
    semester = session.query(Semester).filter(Semester.term == form_data.term).first()
    course = session.query(Course).filter(Course.id == form_data.course_id).first()
    if student is None or course is None or semester is None:
        raise HTTPException(status_code=404, detail="Student or Course or semester not found")
    enrollment = session.query(Enrollment).filter(Enrollment.student_id == student.id, Enrollment.semester_id == semester.id, Enrollment.course_id == course.id).first()
    if enrollment is None:
        raise HTTPException(status_code=404, detail = "Student has not been enrolled for this course in this semester. So mark cannot be entered")
    else:
        new_mark = Marks(mark = form_data.mark)
        session.add(new_mark)
        session.commit()
        enrollment.mark_id = new_mark.id
        session.commit()

    return {"message":"Mark Updated"}

@app.get('/university_summary',response_model=UniversitySummary)
async def University_Summary(uni_id: int = Query(...,description="University ID")):
    university = session.query(University).options(
        joinedload(University.colleges).joinedload(College.courses)
    ).filter(University.id == uni_id).one_or_none()
    if university is None:
        return HTTPException(status_code=404, detail='University do not exist')
    college_list = []
    for college in university.colleges:
        college_list.append(CollegeSchma(
            id = college.id,
            name = college.name,
            courses = [course.name for course in college.courses]
        ))
    return UniversitySummary(
        id = university.id,
        name = university.name,
        colleges = college_list
    )

@app.get('/student_performance_semester',response_model = StudentPerformance)
async def Student_Performance_Semester(student_id: int = Query(..., description='Student ID')):
    student_enrollments = (
        session.query(Semester.id,Semester.term,
                      func.json_group_array(func.json_object('course_id',Course.id,'course_name', Course.name, 'marks',Marks.mark)).label('course_details'))
                      .select_from(Student)
                      .join(Enrollment, Enrollment.student_id == Student.id)
                      .join(Semester, Semester.id == Enrollment.semester_id)
                      .join(Course, Course.id == Enrollment.course_id)
                      .join(Marks, Marks.id == Enrollment.mark_id)
                      .filter(Student.id == student_id)
                      .group_by(Semester.term)
                      .all()
                           )
    details=[]
    for semester_id, semester_term, course_details in student_enrollments:
        details.append(
            SemesterSchema(
                id = semester_id,
                term = semester_term,
                courses = [CourseSchema(**course) for course in list(eval(course_details))]
            )
        )
        
    #return details
    return StudentPerformance(
        id = student_id,
        semesters = details
    )
    
@app.get("/course_enrollment_statistics", response_model=List[CourseEnrollment])
async def Course_Enrollment_Statistics(semester_id: int = Query(...,description='Semester ID')):
    count_list = []
    course_enrollment_counts = (
    session.query(Enrollment.course_id, func.count(Enrollment.id))
    .filter(Enrollment.semester_id == semester_id)
    .group_by(Enrollment.course_id)
    .order_by(desc(func.count(Enrollment.id)))
    .all()
)
    for course_id, count in course_enrollment_counts:
        count_list.append(CourseEnrollment(
            course_id = course_id,
            count = count
        ))
    return count_list

@app.get("/college_performance_overview",response_model = CollegePerformance)
async def College_Performance_Overview(college_id: int = Query(...,description='College ID'), semester_id: int=Query(...,description='Semester ID')):
    course_stats = (
    session.query(
        Course.id.label('course_id'),
        Course.name.label('course_name'),
        func.min(Marks.mark).label('min_marks'),
        func.avg(Marks.mark).label('avg_marks'),
        func.max(Marks.mark).label('max_marks')
    )
    .join(Enrollment, Enrollment.course_id == Course.id)
    .join(Marks, Marks.id == Enrollment.mark_id)
    .filter(
        Enrollment.college_id == college_id,
        Enrollment.semester_id == semester_id
    )
    .group_by(Course.id, Course.name)
    .all()
)
    course_stats_list = []
    for row in course_stats:
        course_stats_list.append(CoursePerformance(
            course_id = row.course_id,
            course_name = row.course_name,
            min_marks = row.min_marks,
            avg_marks = row.avg_marks,
            max_marks = row.max_marks
        ))
    return CollegePerformance(
        id = college_id,
        performance = course_stats_list
    )

@app.get("/find_coursetopper_semester",response_model = CourseTopper)
async def Find_CourseTopper_Semester(course_id: int = Query(..., description = 'Course ID'), semester_id: int = Query(..., description = 'Semester ID')):
    #max_mark = session.query(func.max(Marks.mark)).filter(Marks.course_id == course_id, Marks.semester_id == semester_id).scalar()
    max_mark_student = (
        session.query(Enrollment.student_id,Enrollment.course_id,func.max(Marks.mark).label('max_marks'))
        .join(Marks.enrollment).filter(Enrollment.course_id == course_id, Enrollment.semester_id == semester_id)
        .one_or_none()
    )
    return CourseTopper(
        student_id = max_mark_student.student_id,
        course_id = max_mark_student.course_id,
        maxmarks = max_mark_student.max_marks
    )

# FastAPI endpoint to find university topper for a semester
@app.get("/find_uni_topper_semester",response_model = UniversityTopper)
async def find_uni_topper_semester(semester_id: int = Query(..., description='Semester ID'),uni_id: int = Query(..., description='University ID')):
    #enrollments = session.query(Enrollment).join(Enrollment.colleges).filter(Enrollment.semester_id == semester_id, College.uni_id == uni_id).all()
    max_mark_student = (
    session.query(
        Enrollment.student_id.label('student_id'),
        Enrollment.course_id.label('course_id'),
        func.max(Marks.mark).label('max_mark')
    )
    .select_from(Enrollment)
    .join(College, College.uni_id == uni_id)
    .join(Marks, Enrollment.mark_id == Marks.id)
    .filter(Enrollment.semester_id == semester_id, Enrollment.college_id == College.id)  
    .group_by(Enrollment.student_id, Enrollment.course_id)  
    .subquery()
)
    count_students = (session.query(max_mark_student.c.student_id.label('student_id'),
                                    func.count(max_mark_student.c.student_id))
                                    .group_by(max_mark_student.c.student_id)
                                    .order_by(desc(func.count(max_mark_student.c.student_id)))
                                    .first())
    
    top_student_details = (session.query(Enrollment.student_id,
                                         Student.name.label('student_name'),func.json_group_array(
                                                 func.json_object(
                                                     'course_id',max_mark_student.c.course_id, 
                                                     'course_name',Course.name, 
                                                     'marks', max_mark_student.c.max_mark
                                                 )
                                             ).label('course_details'))
                                        .select_from(Enrollment)
                                        .join(Student, Student.id == Enrollment.student_id)
                                        .join(Course, Course.id == Enrollment.course_id)
                                        .join(College, College.id == Enrollment.college_id)
                                        .filter(Enrollment.semester_id == semester_id, 
                                                College.uni_id == uni_id, 
                                                Enrollment.student_id == count_students.student_id,
                                                max_mark_student.c.student_id == count_students.student_id,
                                                max_mark_student.c.course_id == Enrollment.course_id)
                                                .group_by(Enrollment.student_id)
                                                .one_or_none())
    
    
    university = session.query(University).get(uni_id)
    return UniversityTopper(
        id = university.id,
        name = university.name,
        student_id = top_student_details.student_id,
        student_name = top_student_details.student_name,
        topped_courses = [CourseSchema(**course) for course in list(eval(top_student_details.course_details))]
    )

@app.get("/college_under_which_university")
async def College_Under_Which_University(college_name: str = Query(..., description = "Name of College")):
    college = session.query(College).filter(College.name == college_name).first()
    if college is None:
        raise HTTPException(status_code=404, detail="College not found")
    university = session.query(University).get(college.uni_id)
    
    return {"This college is under":university.name}
'''
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
'''
# Student details: name, uni_name, enrollment details, marks, subjects taken and from which college they are taken in each semester
@app.get("/student_details", response_model = StudentDetails)
async def student_details(student_id: int = Query(..., description="Student details")):
    student_current_semester = (session.query(func.max(Enrollment.semester_id).label('semester_id'),
                                              Semester.term.label('term'))
                                .join(Semester)
                               .filter(Enrollment.student_id == student_id)
                                       .one_or_none())
    
    current_semester_courses = (session.query(Enrollment.course_id, Course.name)
                               .join(Course, Course.id == Enrollment.course_id )
                               .filter(Enrollment.semester_id == student_current_semester.semester_id,
                                       Enrollment.student_id == student_id)
                               .all())
   
    current_course_details = []
    for course_id, course_name in current_semester_courses:
        current_course_details.append(CourseDetails(
           course_id = course_id,
           course_name = course_name
       ))
    
    current_semester = CurrentSemester(
        id = student_current_semester.semester_id,
        term = student_current_semester.term,
        courses = current_course_details
    )
   
    previous_semesters = (session.query(Enrollment.semester_id.label('semester_id'), 
                                             Semester.term.label('term'),
                                             func.json_group_array(
                                                 func.json_object(
                                                     'course_id',Course.id, 
                                                     'course_name',Course.name, 
                                                     'marks', Marks.mark
                                                 )
                                             ).label('course_details'))
                               .join(Semester, Enrollment.semester_id == Semester.id)
                               .join(Course, Course.id == Enrollment.course_id)
                               .join(Marks, Enrollment.mark_id == Marks.id)
                               .filter(Enrollment.student_id == student_id, 
                                       Enrollment.semester_id != student_current_semester.semester_id)
                                    .group_by(Enrollment.semester_id, Semester.term)
                                .all())
    previous_semester_list = []
    for semester_id, term, course_details in previous_semesters:
        previous_semester_list.append(SemesterSchema(
           id = semester_id,
           term = term,
           courses = [CourseSchema(**course) for course in list(eval(course_details))]
       ))
    student = session.query(Student).get(student_id)    
    return StudentDetails(
        id = student_id,
        name = student.name,
        current_semester = current_semester,
        previous_semesters = previous_semester_list
    )
    
@app.get('/brilliant_colleges')
async def Brilliant_Colleges(course_id: int=Query(...,description = "Course ID")):
    
    colleges = (
        select(College.name)
        .join(Marks, Enrollment.mark_id == Marks.id)
        .filter(Enrollment.course_id == course_id,Enrollment.college_id == College.id)
        .order_by(desc(func.avg(Marks.mark)), College.name)
        .group_by(College.name)
    )

    colleges_list = session.scalars(colleges).all()
    
    return colleges_list

@app.get('/scholarship_higherstudies_eligibility', response_model=CombinedResponse)
async def Scholarship_Higherstudies_Eligibility(semester_id: int = Query(..., description = "Semester ID")):
    
    scholarship_students = (
        session.query(Student.id.label('student_id'),
                      Student.name.label('student_name'), 
                      func.avg(Marks.mark).label('aggregate_marks'))
        .select_from(Student)
        .join(Enrollment, Student.enrollments)
        .join(Marks, Enrollment.mark)
        .filter(Enrollment.semester_id == semester_id)
        .group_by(Student.id, Student.name)
        .having(func.avg(Marks.mark) >= 80)
        .all()
    )

    no_higherstudies_students = (
        session.query(Student.id.label('student_id'),
                      Student.name.label('student_name'), 
                      func.avg(Marks.mark).label('aggregate_marks'))
        .select_from(Student)
        .join(Enrollment, Student.enrollments)
        .join(Marks, Enrollment.mark)
        .filter(Enrollment.semester_id == semester_id)
        .group_by(Student.id, Student.name)
        .having(func.avg(Marks.mark) <= 40)
        .all()
    )
    scholarship_list = []
    no_higherstudies_students_list = []
    for m in scholarship_students:
        scholarship_list.append(
            Scholarship_NoHigher(
                student_id=m.student_id,
                name=m.student_name,
                aggregate= m.aggregate_marks
            )
        )
    for m in no_higherstudies_students:
        no_higherstudies_students_list.append(
            Scholarship_NoHigher(
                student_id=m.student_id,
                name=m.student_name,
                aggregate= m.aggregate_marks
            )
        )
    return CombinedResponse(
        scholarship = scholarship_list,
        no_higherstudies = no_higherstudies_students_list
    )

@app.get('/publish_marks',response_model = Union[Publish_marks, str])
async def Publish_Marks(student_registernum: str = Query(..., description = "Student Register number"),semester_id: int = Query(..., description = "Semester ID")):
    student_marks = (
        session.query(Student.register_number.label('student_register_number'), 
                      Student.name.label('student_name'),
                      Student.date_of_birth.label('dob'), 
                      Semester.id.label('semester_id'), 
                      Semester.term.label('semester_name'),
                      func.json_group_array(
                          func.json_object('course_id',Course.id,
                                           'course_name', Course.name, 
                                           'marks',Marks.mark))
                                           .label('course_details'),
                        func.avg(Marks.mark).label('aggregate'))
                        .select_from(Student)
                        .join(Enrollment, Student.enrollments)
                        .join(Semester, Enrollment.semester)
                        .join(Course, Enrollment.course)
                        .join(Marks, Enrollment.mark)
                        .filter(Student.register_number == student_registernum, Enrollment.semester_id == semester_id)
                        .group_by(Student.id,Student.name, 
                                  Semester.id,Semester.term)
                        .one_or_none()
    )
    if student_marks is None:
        return "Marks not yet published"

    return Publish_marks(
        student_reg = student_marks.student_register_number,
        student_name = student_marks.student_name,
        dob = student_marks.dob,
        semester_id = student_marks.semester_id,
        semester_name = student_marks.semester_name,
        course_details = [CourseSchema(**course) for course in list(eval(student_marks.course_details))],
        aggregate = student_marks.aggregate,
        scholarship=True if student_marks.aggregate >= 80 else False,
        higherstudies=False if student_marks.aggregate <= 40 else True
    )

@app.get('/students_list', response_model=List[CourseStudents])
async def Semester_Students(semester_id: int = Query(..., description = "Semester ID")):
    course_students = (
        session.query(Student.id.label('student_id'),
                      Student.name.label('student_name'),
                      func.avg(Marks.mark).label('avg_marks')
                      ).select_from(Student)
                      .join(Enrollment, Student.enrollments)
                      .join(Marks, Enrollment.mark)
                      .filter(Enrollment.semester_id == semester_id)
                      .group_by(Enrollment.student_id)
                      .order_by(desc(func.avg(Marks.mark)), Student.name)
                      .all()
    ) 
    students_list = []
    for l in course_students:
        students_list.append(CourseStudents(
            student_id = l.student_id,
            student_name = l.student_name,
            marks = l.avg_marks
        ))
    return students_list
    
if __name__ == '__main__':
    uvicorn.run("main:app",host="127.0.0.1",port=8000,reload=True)
