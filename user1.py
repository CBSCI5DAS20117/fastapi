from sqlalchemy import create_engine, Column,Date, Integer, String, ForeignKey, Float, Table, select, exists
#from sqlalchemy.ext.declarative import declarative_base
import bcrypt
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
import random
from collections import defaultdict

engine = create_engine('sqlite:///rough.db',echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()
    
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

    university = relationship('University', back_populates='colleges')
    enrollments = relationship('Enrollment', back_populates='college', cascade='all, delete-orphan',single_parent=True)
    courses = relationship('Course', back_populates='colleges',secondary=course_college, cascade='all, delete-orphan',single_parent=True)


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
    #marks = relationship('Marks', back_populates='students', cascade = 'all, delete-orphan', single_parent = True)
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
    #enroll_id = Column(Integer, ForeignKey('enrollment.id'),unique=True)
    mark = Column(Float)
    
    enrollment = relationship('Enrollment', back_populates='mark')

# when creating relationships, name used in back_populates should same as attribute in another table

#Base.metadata.create_all(engine)

