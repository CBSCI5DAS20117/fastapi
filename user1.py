from sqlalchemy import create_engine,Column,Date, Integer, String, ForeignKey, Float, Table
import bcrypt
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
import random
from collections import defaultdict

engine = create_engine("postgresql://postgres:Passw0rd@localhost:5432/University")
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_name = Column(String)
    password = Column(String)

    #students = relationship('Student', back_populates='user')
    
    def set_password(self, plain_password):
        self.password = bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, plain_password):
        return bcrypt.checkpw(plain_password.encode(),self.password.encode())

    
class University(Base):
    __tablename__ = 'university'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable = False, unique=True)

    colleges = relationship('College', back_populates='university',cascade='all, delete-orphan',single_parent=True)
    students = relationship('Student', back_populates='university',cascade='all, delete-orphan',single_parent = True)

course_college = Table(
    'course_college', Base.metadata,
    Column('college_id',Integer, ForeignKey('college.id'), primary_key=True),
    Column('course_id', Integer, ForeignKey('course.id'),primary_key = True)
)


class College(Base):
    __tablename__ = 'college'

    id = Column(Integer, primary_key= True)
    name = Column(String, nullable=False, unique=True)
    uni_id = Column(Integer, ForeignKey('university.id'))
    latitude = Column(Float)
    longitude = Column(Float)

    university = relationship('University', back_populates='colleges')
    enrollments = relationship('Enrollment', back_populates='college', cascade='all, delete-orphan',single_parent=True)
    courses = relationship('Course', back_populates='colleges',secondary=course_college, cascade='all, delete-orphan',single_parent=True)
    # distance = relationship('Hostel_College_Distance',back_populates='colleges')


class Course(Base):
    __tablename__ = 'course'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique = True)
    
    enrollments = relationship('Enrollment', back_populates='course', cascade='all, delete-orphan',single_parent=True)
    #marks = relationship('Marks', back_populates = 'course', cascade='all, delete-orphan',single_parent=True)
    colleges = relationship('College', back_populates='courses',secondary=course_college)

class Student(Base):
    __tablename__ = 'student'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    uni_id = Column(Integer, ForeignKey('university.id'))
    date_of_birth = Column(Date, nullable=True)
    register_number = Column(String)
    
    enrollments = relationship('Enrollment',back_populates='student', cascade = 'all, delete-orphan', single_parent = True)
    university = relationship('University', back_populates='students')

class Semester(Base):
    __tablename__ = 'semester'

    id = Column(Integer, primary_key=True)
    term = Column(String, nullable=False, unique=True)

    enrollments = relationship('Enrollment',back_populates='semester', cascade = 'all, delete-orphan', single_parent = True)

class Enrollment(Base):
    __tablename__ = 'enrollment'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('student.id'))
    course_id = Column(Integer, ForeignKey('course.id'))
    semester_id = Column(Integer, ForeignKey('semester.id'))
    college_id = Column(Integer, ForeignKey('college.id'))
    mark_id = Column(Integer, ForeignKey('marks.id'),unique=True)
    
    student = relationship('Student', back_populates='enrollments')
    course = relationship('Course', back_populates='enrollments')
    semester = relationship('Semester', back_populates='enrollments')
    college = relationship('College', back_populates='enrollments')
    mark = relationship('Marks', back_populates='enrollment')  

class Marks(Base):
    __tablename__ = 'marks'

    id = Column(Integer, primary_key=True)
    mark = Column(Float)
    
    enrollment = relationship('Enrollment', back_populates='mark')

class Hostel_PG(Base):
    __tablename__ = 'hostel_pg'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable = False)
    type = Column(String, nullable = False)
    latitude = Column(Float)
    longitude = Column(Float)
    
# user = User(user_name = 'user1',password = User.set_password('password1'))
# session.add(user)
# session.commit()

# when creating relationships, name used in back_populates should same as attribute in another table

#Base.metadata.create_all(engine)

