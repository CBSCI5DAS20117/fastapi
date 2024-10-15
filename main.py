from fastapi import FastAPI, Depends, HTTPException, Query
from authentication import  get_current_user, create_access_token
from user1 import session,User,Subjects, Hostel_PG,University, College, Course, Student, Student_Process, Student_Admission, Marks, course_college, engine
import uvicorn
from fastapi.security import OAuth2PasswordRequestForm
from pydantic_form_details import SubjectCreate, CollegeEnrollments,ListHostels,HostelCreate,CourseStudents,Publish_marks,Scholarship_NoHigher,CombinedResponse,UniversityCreate,UniversityTopper,StudentDetails,CurrentSemester,CourseDetails,CourseTopper,CollegePerformance,CoursePerformance,CourseEnrollment,CourseEnrollment,CourseList,SemesterSchema,StudentPerformance,UniversitySummary, CollegeCreate, CourseCreate, StudentAdmission, SemesterCreate, MarkCreate, EnrollmentCreate, AssignCourse
#from sqlalchemy.orm import joinedload
from sqlalchemy.sql import select
from sqlalchemy import func, desc #case,text
from typing import List, Union
from geopy.geocoders import Nominatim
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

app = FastAPI()
geolocator = Nominatim(user_agent="app")
origins=["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])

@app.get("/")
async def read_root():
    return {'message':'Welcome to fastapi-authentication'}

@app.get("/login/{regnum}/{password}")
async def login_for_access_token(regnum: str, password: str):
    users = session.query(User).filter(User.username == regnum).all()
    if users is None:
        raise HTTPException(status_code=400, detail="Incorrect Username or Password")
    else:
        for user in users:
            if user.check_password(password):
                access_token = create_access_token(data = {"sub":user.username, "userid":user.id})
        
    return {"access_token": access_token,'username':user.username, "token_type": "bearer"}

@app.get('/university_options')
async def University_Options():
    universities = (
        select(University.name)
        .select_from(University)
    )
    unis = session.scalars(universities).all()
    return unis

@app.get('/college_options/{uni_name}')
async def College_Options(uni_name: str):
    colleges = (
        select(College.name)
        .select_from(College)
        .join(University, College.uni_id == University.id)
        .filter(University.name == uni_name)
    )
    c = session.scalars(colleges).all()
    return c

@app.get('/course_options/{college_name}')
async def Course_Options(college_name: str):
    courses = (
        select(Course.name)
        .select_from(Course)
        .join(College, Course.colleges)
        .filter(College.name == college_name)
    )
    c=session.scalars(courses).all()
    return c

@app.post('/create_admission')
async def Create_Admission(form_data: StudentAdmission):
    college = session.query(College).filter(College.name == form_data.college).first()
    course = session.query(Course).filter(Course.name == form_data.course).first()
    if  college and course:
        # create student
        new_student = Student(name = form_data.name, uni_id = college.uni_id,
                              date_of_birth = form_data.dob, qualification = form_data.qualification,
                              address = form_data.address)
        session.add(new_student)
        session.flush()
        # create admission
        new_admission = Student_Admission(student_id = new_student.id, course_id = course.id,
                                          register_num = course.course_code+str(new_student.id),
                                          date = date.today(), college_id = college.id,
                                          university_id = college.uni_id)
        session.add(new_admission)
        session.flush()
        new_student.admission_id = new_admission.id
        new_user = User(username = new_admission.register_num)
        new_user.set_password(new_admission.register_num)
        session.add(new_user)
        session.commit()
        return {'message':'Enrollment completed successfully'}
    else:
        return {'message':'Error occured'}
    
@app.get('/student_details/{username}')
async def Student_Details(username: str):
    student_details_query = (
        select(func.json_build_object(
            'name', Student.name,
            'dob',Student.date_of_birth,
            'qualification',Student.qualification,
            'address',Student.address,
            'university',University.name,
            'college',College.name,
            'course',Course.name,
            'reg_num',Student_Admission.register_num,
            'date',Student_Admission.date
        ))
        .select_from(Student)
        .join(University, Student.uni_id == University.id)
        .join(Student_Admission, Student.student_admission)
        .join(College, Student_Admission.college)
        .join(Course, Student_Admission.course)
        .filter(Student_Admission.register_num == username)
    )
    result = session.execute(student_details_query).first()
    student_details = result[0]
    return student_details


# @app.post("/create_University")
# async def Create_University(form_data: UniversityCreate,userinfo: dict = Depends(get_current_user)):
#     if userinfo:
#         new_university = University(name = form_data.name)
#         session.add(new_university)
#         session.commit()

#         return {"message":"New University created"}

# @app.post("/create_College")
# async def Create_College(form_data: CollegeCreate,userinfo: dict = Depends(get_current_user)):
#     if userinfo:
#         university = session.query(University).filter(University.name == form_data.uni_name).first()
#         if university is None:
#             raise HTTPException(status_code=404, detail="University not found")
#         location = geolocator.reverse(str(form_data.latitude)+","+str(form_data.longitude))
#         address = location.raw['address']
#         new_college = College(name = form_data.name, uni_id = university.id,
#                             latitude = form_data.latitude, longitude = form_data.longitude,zip = address.get('postcode'),
#                             city = address.get('city'),state = address.get('state'),phone = form_data.phone)
#         session.add(new_college)
#         session.commit()

#         return {"message":"New College created"}

# @app.post("/create_Course")
# async def Create_Course(form_data: CourseCreate,
#                         userinfo: dict = Depends(get_current_user)):
#     if userinfo:
#         new_course = Course(name = form_data.name,course_num = form_data.course_num)
#         session.add(new_course)
#         #college.courses.append(new_course)
#         session.commit()

#         return {"message":"New Course created"}

# @app.post("/create_Subject")
# async def Create_Subject(form_data: SubjectCreate,
#                          userinfo: dict=Depends(get_current_user)):
#     if userinfo:
#         course = session.query(Course).get(form_data.course_id)
#         semester = session.query(Semester).get(form_data.semester_id)
#         university = session.query(University).get(form_data.university_id)

#         if course and semester and university:
#             stmt = select(course_university).where(
#                 course_university.c.course_id == course.id,
#                 course_university.c.university_id == university.id
#             )
#             result = session.execute(stmt).fetchone()
#             if result is None:
#                 raise HTTPException(status_code=409, detail="This course is not currently offered by this college")
#             new_subject = Subjects(name = form_data.name,
#                                    course_id = course.id,
#                                    semester_id = semester.id,
#                                    university_id = university.id)
#             session.add(new_subject)
#             session.commit()
#             return {"message":"New Subject Created"}
#         else:
#             raise HTTPException(status_code=404, detail="Course or semester or university not found")


# @app.post("/assign_course_to_university")
# async def Assign_Course_to_College(form_data: AssignCourse,
#                                    userinfo: dict = Depends(get_current_user)):
#     if userinfo:
#         course = session.query(Course).get(form_data.course_id)
#         university = session.query(University).get(form_data.university_id)

#         if course is None:
#             raise HTTPException(status_code=404, detail="Course not found")
#         if university is None:
#             raise HTTPException(status_code=404, detail="College not found")
#         course.universities.append(university)
#         session.commit()
        
#         return {"message": "Course assigned to university"}

# @app.post("/create_Student")
# async def Create_Student(form_data: StudentCreate,
#                          userinfo: dict = Depends(get_current_user)):
#     if userinfo:
#         university = session.query(University).get(form_data.uni_id)
#         if university is None:
#             raise HTTPException(status_code=404, detail="University not found")
#         new_student = Student(name = form_data.name ,uni_id = university.id,
#                             date_of_birth = form_data.dob)
#         session.add(new_student)
#         session.commit()

#         return {"message":"New Student created"}

# @app.post("/create_Semester")
# async def Create_Semester(form_data: SemesterCreate,
#                           userinfo: dict = Depends(get_current_user)):
#     if userinfo:
#         new_semester = Semester(term = form_data.term)
#         session.add(new_semester)
#         session.commit()

#         return {"message":"New Semester created"}

# @app.post("/create_Enrollment")
# async def Create_Enrollment(form_data: EnrollmentCreate,
#                             userinfo: dict = Depends(get_current_user)):
#     if userinfo:
#         student = session.query(Student).filter(Student.id == form_data.student_id).first()
#         semester = session.query(Semester).filter(Semester.term == form_data.term).first()
#         university = session.query(University).filter(University.id == form_data.university_id).first()
#         course = session.query(Course).filter(Course.id == form_data.course_id).first()
#         subject = session.query(Subjects).filter(Subjects.id == form_data.subject_id).first()
        
#         if student is None or course is None or semester is None:
#             raise HTTPException(status_code=404, detail="Student or Course or semester not found")
#         if university.id != student.uni_id:
#             raise HTTPException(status_code = 404, detail = "Student is not part of that university")
#         if subject.semester_id != semester.id:
#             raise HTTPException(status_code = 404, detail = "Subject is not taken in this semester")
#         enrollment = session.query(Enrollment).filter(Enrollment.student_id == student.id,
#                                                       Enrollment.course_id == course.id, 
#                                                       Enrollment.subject_id == subject.id).first()
#         if enrollment:
#             raise HTTPException(status_code=409, detail="Student has already enrolled or completed this course")
#         stmt = select(course_university).where(
#             course_university.c.course_id == course.id,
#             course_university.c.university_id == university.id
#         )
#         result = session.execute(stmt).fetchone()
#         if result is None:
#             raise HTTPException(status_code=409, detail="This course is not currently offered by this college")
#         new_enrollment = Enrollment(student_id = student.id,
#                                     semester_id = semester.id, 
#                                     course_id = course.id, 
#                                     subject_id = subject.id,
#                                     register_num = course.course_num)
#         session.add(new_enrollment)
#         session.commit()

#         return {"message":"Student Enrolled"}

# @app.post("/create_Mark")
# async def Create_Mark(form_data: MarkCreate,
#                       userinfo: dict = Depends(get_current_user)):
#     if userinfo:
#         student = session.query(Student).filter(Student.id == form_data.student_id).first()
#         semester = session.query(Semester).filter(Semester.term == form_data.term).first()
#         subject = session.query(Subjects).filter(Subjects.id == form_data.subject_id).first()
#         if student is None or subject is None or semester is None:
#             raise HTTPException(status_code=404, detail="Student or Subject or semester not found")
#         enrollment = session.query(Enrollment).filter(Enrollment.student_id == student.id, Enrollment.semester_id == semester.id, Enrollment.subject_id == subject.id).first()
#         if enrollment is None:
#             raise HTTPException(status_code=404, detail = "Student has not been enrolled for this course in this semester. So mark cannot be entered")
#         else:
#             new_mark = Marks(mark = form_data.mark, student_id = student.id,
#                              subject_id = subject.id, semester_id = semester.id)
#             session.add(new_mark)
#             session.commit()
#             enrollment.mark_id = new_mark.id
#             session.commit()

#         return {"message":"Mark Updated"}

# @app.post("/create_hostel")
# async def Create_Hostel(form_data: HostelCreate,
#                         userinfo: dict = Depends(get_current_user)):
#     if userinfo:
#         location = geolocator.reverse(str(form_data.latitude)+","+str(form_data.longitude))
#         address = location.raw['address']
#         hostel = Hostel_PG(name = form_data.hostel_name,
#                         type = form_data.type,
#                         latitude = form_data.latitude,
#                         longitude = form_data.longitude,
#                         zip = address.get('postcode'),
#                         city = address.get('city'),state = address.get('state'),phone = form_data.phone)
#         session.add(hostel)
#         session.commit()
#         return {"message":"Hostel Created"}

# @app.get('/university_summary',response_model=UniversitySummary)
# async def University_Summary(uni_id: int = Query(...,description="University ID"),
#                              userinfo: dict = Depends(get_current_user)):
    
#     if userinfo:
#         course_info = (
#         select(
#             func.json_build_object(
#                 'id',Course.id,
#                 'name',Course.name,
#                 'register_number',Course.course_num,
#                 'subjects',func.json_agg(
#                     Subjects.name
#                 )
#             )
#         )
#         .select_from(Course)
#         .join(Subjects, Course.subjects)
#         .join(course_university,course_university.c.university_id
#               == uni_id)
#         .filter(course_university.c.course_id == Course.id,
#                 Subjects.university_id==uni_id)
#         .group_by(Course.id, Course.name, Course.course_num)
#     )
    
#         courses = session.scalars(course_info).all()
#         university = session.query(University).get(uni_id)
#         return UniversitySummary(
#             id = university.id,
#             name = university.name,
#             courses = courses
#     )

# @app.get('/student_performance_semester',response_model = StudentPerformance)
# async def Student_Performance_Semester(student_id: int = Query(..., description='Student ID'),
#                                        userinfo: dict = Depends(get_current_user)):
    
#     if userinfo:
#         student_enrollments = (
#         select(func.json_build_object('id',Semester.id,
#                                        'term',Semester.term,'subjects',
#                       func.json_agg(func.json_build_object('subject_id',Subjects.id,'subject_name', Subjects.name, 'marks',Marks.mark))))
#                       .select_from(Student)
#                       .join(Enrollment, Enrollment.student_id == Student.id)
#                       .join(Semester, Semester.id == Enrollment.semester_id)
#                       .join(Course, Course.id == Enrollment.course_id)
#                       .join(Subjects, Subjects.id == Enrollment.subject_id)
#                       .join(Marks, Marks.subject_id == Enrollment.subject_id)
#                       .filter(Student.id == student_id)
#                       .group_by(Semester.id,Semester.term)
                      
#                            )
#         s = session.scalars(student_enrollments).all()
#         return StudentPerformance(
#             id = student_id,
#             semesters = s
#     )
    
# @app.get("/course_enrollment_statistics",response_model=List[CourseEnrollment])
# async def Course_Enrollment_Statistics(semester_id: int = Query(...,description='Semester ID'),
#                                        userinfo: dict = Depends(get_current_user)):
    
#    if userinfo:
#         course_enrollment_counts = (
#         select(func.json_build_object(
#         'course_id',Enrollment.course_id, 
#         'count',func.count(Enrollment.id)
#     ))
#     .filter(Enrollment.semester_id == semester_id)
#     .group_by(Enrollment.course_id)
#     .order_by(desc(func.count(Enrollment.id)))
# )
#         c_list = session.scalars(course_enrollment_counts).all()
#         return c_list

# @app.get("/university_performance_overview",response_model = CollegePerformance)
# async def University_Performance_Overview(university_id: int = Query(...,description='University ID'), semester_id: int=Query(...,description='Semester ID'),
#                                        userinfo: dict = Depends(get_current_user)):
   
#     if userinfo:
#         course_performance_subquery = (
#         select(func.json_build_object(
#         'course_id',Enrollment.course_id,
#         'course_name',Course.name,
#         'subjects',
#             func.json_build_object(
#                 'id',Subjects.id,
#                 'name',Subjects.name,
#                 'min_marks',func.min(Marks.mark),
#                 'avg_marks',func.avg(Marks.mark),
#                 'max_marks',func.max(Marks.mark)
#             )
        
#         )
#         )
#         .select_from(Enrollment)
#         .join(Course, Enrollment.course_id == Course.id)
#         .join(Subjects, Enrollment.subject)
#         .join(Marks, Enrollment.subject_id == Marks.subject_id)
#         .filter(Enrollment.semester_id == semester_id, Subjects.university_id == university_id)
#         .group_by(Enrollment.course_id,Course.name,Subjects.id,Subjects.name)
#         )
#         university_details = session.scalars(course_performance_subquery).all()
#         university = session.query(University).get(university_id)
#         return CollegePerformance(
#             id = university.id,
#             name = university.name,
#             performance = university_details
#         )

# @app.get("/find_coursetopper_semester",response_model=CourseTopper)
# async def Find_CourseTopper_Semester(course_id: int = Query(..., description = 'Course ID'), semester_id: int = Query(..., description = 'Semester ID'),
#                                      userinfo: dict = Depends(get_current_user)):
#     if userinfo:
#         max_subject = (
#         select(
#         Subjects.id.label('subject_id'),
#         func.max(Marks.mark).label('marks')
#         )
#         .select_from(Enrollment)
#         .join(Student, Enrollment.student)
#         .join(Subjects, Enrollment.subject)
#         .join(Marks, Subjects.marks)
#         .filter(
#         Subjects.course_id == course_id,
#         Subjects.semester_id == semester_id,
#         Marks.student_id == Student.id
#         )
#         .group_by(Subjects.id)
#         .subquery()
#         )
#         max_student = (
#             select(
#         Student.id.label('student_id'),
#         Subjects.id.label('subject_id'),
#         Marks.mark.label('marks')
#         )
#         .select_from(Student)
#         .join(Enrollment, Student.enrollments)
#         .join(Subjects, Enrollment.subject)
#         .join(Marks, Subjects.marks)
#         .filter(
#         max_subject.c.subject_id == Subjects.id,
#         max_subject.c.marks == Marks.mark,
#         Marks.student_id == Student.id
#         )
#         .group_by(Student.id,Subjects.id,Marks.mark)
#         .subquery()
#         )
#         count_stud = (
#             session.query(max_student.c.student_id.label('student_id'),
#                     func.count(max_student.c.student_id).label('count'))
#             .select_from(max_student)
#             .group_by(max_student.c.student_id)
#             .order_by(desc(func.count(max_student.c.student_id)))
#             .first()
#         )
#         student = session.query(Student).get(count_stud.student_id)
#         university = session.query(University).get(student.uni_id)
#         return CourseTopper(
#             student_id = student.id,
#             student_name = student.name,
#             university_name = university.name

#         )
    
# # FastAPI endpoint to find university topper for a semester
# @app.get("/find_uni_topper_semester",response_model = UniversityTopper)
# async def find_uni_topper_semester(semester_id: int = Query(..., description='Semester ID'),uni_id: int = Query(..., description='University ID'),
#                                    userinfo: dict = Depends(get_current_user)):
#     if userinfo:
#         max_mark_student = (
#         session.query(
#             Enrollment.student_id.label('student_id'),
#             Enrollment.course_id.label('course_id'),
#             func.max(Marks.mark).label('max_mark')
#         )
#         .select_from(Enrollment)
#         .join(College, College.uni_id == uni_id)
#         .join(Marks, Enrollment.mark_id == Marks.id)
#         .filter(Enrollment.semester_id == semester_id, Enrollment.college_id == College.id)  
#         .group_by(Enrollment.student_id, Enrollment.course_id)  
#         .subquery()
#     )
#         count_students = (session.query(max_mark_student.c.student_id.label('student_id'),
#                                         func.count(max_mark_student.c.student_id))
#                                         .group_by(max_mark_student.c.student_id)
#                                         .order_by(desc(func.count(max_mark_student.c.student_id)))
#                                         .first())
        
#         top_student_details = (session.query(Enrollment.student_id,
#                     Student.name.label('student_name'),func.json_agg(
#                         func.json_build_object(
#                     'course_id',max_mark_student.c.course_id, 
#                     'course_name',Course.name, 
#                     'marks', max_mark_student.c.max_mark
#                             )
#                 ).label('course_details'))
#                     .select_from(Enrollment)
#                     .join(Student, Student.id == Enrollment.student_id)
#                     .join(Course, Course.id == Enrollment.course_id)
#                     .join(College, College.id == Enrollment.college_id)
#                     .filter(Enrollment.semester_id == semester_id, 
#                     College.uni_id == uni_id, 
#                     Enrollment.student_id == count_students.student_id,
#                     max_mark_student.c.student_id == count_students.student_id,
#                     max_mark_student.c.course_id == Enrollment.course_id)
#                     .group_by(Enrollment.student_id,Student.name)
#                             .one_or_none())
    
    
#         university = session.query(University).get(uni_id)
#         return UniversityTopper(
#             id = university.id,
#             name = university.name,
#             student_id = top_student_details.student_id,
#             student_name = top_student_details.student_name,
#             topped_courses = top_student_details.course_details
#         )

# @app.get("/college_under_which_university")
# async def College_Under_Which_University(college_name: str = Query(..., description = "Name of College"),
#                                          userinfo: dict = Depends(get_current_user)):
#     if userinfo:
#         college = session.query(College).filter(College.name == college_name).first()
#         if college is None:
#             raise HTTPException(status_code=404, detail="College not found")
#         university = session.query(University).get(college.uni_id)
        
#         return {"This college is under":university.name}
    
# @app.get('/brilliant_colleges')
# async def Brilliant_Colleges(userinfo: dict = Depends(get_current_user),course_id: int=Query(...,description = "Course ID")):
#     if userinfo:
#         colleges = (
#             select(College.name)
#             .select_from(College)
#             .join(Enrollment, College.enrollments)
#             .join(Marks, Enrollment.mark_id == Marks.id)
#             .filter(Enrollment.course_id == course_id,Enrollment.college_id == College.id)
#             .order_by(desc(func.avg(Marks.mark)), College.name)
#             .group_by(College.name)
#         )

#         college_list = session.scalars(colleges).all()
#         return college_list

# @app.get('/scholarship_higherstudies_eligibility',response_model = CombinedResponse)
# async def Scholarship_Higherstudies_Eligibility(userinfo: dict = Depends(get_current_user),semester_id: int = Query(..., description = "Semester ID")):
#     if userinfo:
#         scholarship_students = (
#         select(func.json_build_object(
#                 'student_id',Student.id,
#                 'name',Student.name, 
#                 'aggregate',func.avg(Marks.mark)
                
#                 ).label('scholarship'))
#             .select_from(Student)
#             .join(Enrollment, Student.enrollments)
#             .join(Marks, Enrollment.mark)
#             .filter(Enrollment.semester_id == semester_id)
#             .group_by(Student.id, Student.name)
#             .having(func.avg(Marks.mark) >= 80)
#     )
#         # result1 = session.execute(scholarship_students).scalars().all()
#         no_higherstudies_students = (
#             select(func.json_build_object(
#                 'student_id',Student.id,
#                 'name',Student.name, 
#                 'aggregate',func.avg(Marks.mark)
                
#                 ).label('no_higherstudies'))
#             .select_from(Student)
#             .join(Enrollment, Student.enrollments)
#             .join(Marks, Enrollment.mark)
#             .filter(Enrollment.semester_id == semester_id)
#             .group_by(Student.id, Student.name)
#             .having(func.avg(Marks.mark) <= 40)
#         )
#         data1 = (
#             session.scalars(
#                 scholarship_students
#             ).all()
#         )
        
#         data2 = (
#             session.scalars(
#                 no_higherstudies_students
#             ).all()
#         )

#         return CombinedResponse(
#             scholarship = data1,
#             no_higherstudies = data2
#         )

# @app.get('/publish_marks',response_model=Union[Publish_marks,str])
# async def Publish_Marks(userinfo: dict = Depends(get_current_user),student_registernum: str = Query(..., description = "Student Register number"),semester_id: int = Query(..., description = "Semester ID")):
#     if userinfo:
#         student_marks = (
#             select(func.json_build_object(
#                 'student_reg',Student.register_number, 
#                         'student_name',Student.name,
#                         'dob',Student.date_of_birth, 
#                         'semester_id',Semester.id, 
#                         'semester_name',Semester.term,
#                         'course_details',func.json_agg(
#                             func.json_build_object('course_id',Course.id,
#                                             'course_name', Course.name, 
#                                             'marks',Marks.mark)),
#                             'aggregate',func.avg(Marks.mark)).label('publish_marks'))
#                             .select_from(Student)
#                             .join(Enrollment, Student.enrollments)
#                             .join(Semester, Enrollment.semester)
#                             .join(Course, Enrollment.course)
#                             .join(Marks, Enrollment.mark)
#                             .filter(Student.register_number == student_registernum, Enrollment.semester_id == semester_id)
#                             .group_by(Student.id,Student.name, 
#                                     Semester.id,Semester.term)
#         )
#         sm = session.execute(student_marks).scalar_one_or_none()
        
#         if student_marks is None:
#             return "Marks not yet published"
        
#         sm['scholarship'] = True if sm.get('aggregate') >= 80 else False
#         sm['higherstudies'] = False if sm.get('aggregate') <= 40 else True
#         return sm

# @app.get('/students_list',response_model = List[CourseStudents])
# async def Semester_Students(userinfo: dict = Depends(get_current_user),semester_id: int = Query(..., description = "Semester ID")):
#     if userinfo:
#         course_students = (
#             select(
#                 func.json_build_object(
#                         'student_id',Student.id,
#                         'student_name',Student.name,
#                         'marks',func.avg(Marks.mark)
#                 )
#                         ).select_from(Student)
#                         .join(Enrollment, Student.enrollments)
#                         .join(Marks, Enrollment.mark)
#                         .filter(Enrollment.semester_id == semester_id)
#                         .group_by(Student.id,Student.name)
#                         .order_by(desc(func.avg(Marks.mark)), Student.name)
                        
#         ) 
#         students_list_json = session.scalars(course_students).all()
#         return students_list_json

# @app.get('/college_enrollments',response_model = List[CollegeEnrollments])
# async def College_Enrollments(userinfo: dict = Depends(get_current_user),college_id: int = Query(...,description = "college id"),
#                               semester_id: int = Query(...,description = "semester id")):
#     if userinfo:
#         course_enrollments = (
#             select(
#                 func.json_build_object(
#                     'course_id', Enrollment.course_id,
#                     'course_name',Course.name,
#                     'students',func.json_agg(
#                         func.json_build_object(
#                             'student_id',Enrollment.student_id,
#                             'student_name',Student.name
#                         )
#                     )
#                 )
#             ).select_from(Enrollment)
#             .join(Course, Enrollment.course)
#             .join(Student, Enrollment.student)
#             .filter(Enrollment.college_id == college_id,
#                     Enrollment.semester_id == semester_id)
#             .group_by(Enrollment.course_id,Course.name)
#         )
#         course_enrollments_list = session.scalars(course_enrollments).all()
#         return course_enrollments_list

# def geo_dist(lat1,long1,lat2,long2):
    
#     return (
# func.acos(
# func.sin(func.radians(lat1)) * func.sin(func.radians(lat2)) +
# func.cos(func.radians(lat1)) * func.cos(func.radians(lat2)) *
# func.cos(func.radians(long2) - func.radians(long1))
# ) * 6371)

# @app.get('/list_hostels', response_model = List[ListHostels])
# async def LIst_Hostels(userinfo: dict = Depends(get_current_user),college_id: int = Query(..., description="college_id")):
#     if userinfo:
#         college_location_query = (
#             session.query(College.latitude.label('latitude'),
#                 College.longitude.label('longitude'))
#             .filter(College.id == college_id)
#             .one_or_none()
#         )
        
#         hostel_college_distances = (
#             select(Hostel_PG.id.label('hostel_id'),
#                 geo_dist(college_location_query.latitude, college_location_query.longitude, Hostel_PG.latitude, Hostel_PG.longitude).label('distance'))
#                 .select_from(Hostel_PG)
#                 .subquery()
#         )
        
#         hostels = (
#             select(func.json_build_object(
#                 'hostel_id',Hostel_PG.id,
#                 'hostel_name',Hostel_PG.name,
#                 'type',Hostel_PG.type,
#                 'distance',func.min(hostel_college_distances.c.distance)
#             ))
#             .select_from(Hostel_PG)
#             .join(hostel_college_distances, hostel_college_distances.c.hostel_id == Hostel_PG.id)
#             .group_by(Hostel_PG.id)
#             .order_by(func.min(hostel_college_distances.c.distance))
#         )
#         hostels_list = session.scalars(hostels).all()
#         return hostels_list

if __name__ == '__main__':
    uvicorn.run("main:app",host="127.0.0.1",port=8000,reload=True)
