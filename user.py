from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, Table
#from sqlalchemy.ext.declarative import declarative_base
import bcrypt
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

engine = create_engine('sqlite:///user.db',echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)

    students = relationship('Student', back_populates='user')
    
    def set_password(self, plain_password):
        self.password = bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, plain_password):
        return bcrypt.checkpw(plain_password.encode(),self.password.encode())
    
class University(Base):
    __tablename__ = 'university'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable = False)

    colleges = relationship('College', back_populates='university')
    students = relationship('Student', back_populates='university')


class Course_College(Base):
    __tablename__ = 'course_college'

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('course.id'))
    college_id = Column(Integer, ForeignKey('college.id'))

class College(Base):
    __tablename__ = 'college'

    id = Column(Integer, primary_key= True)
    name = Column(String, nullable=False)
    uni_id = Column(Integer, ForeignKey('university.id'))

    university = relationship('University', back_populates='colleges')
    enrollments = relationship('Enrollment', back_populates='colleges')

class Course(Base):
    __tablename__ = 'course'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    

    enrollments = relationship('Enrollment', back_populates='courses', cascade='all, delete-orphan',single_parent=True)
    marks = relationship('Marks', back_populates = 'course', cascade='all, delete-orphan',single_parent=True)



class Student(Base):
    __tablename__ = 'student'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String, nullable=False)
    uni_id = Column(Integer, ForeignKey('university.id'))
    
    user = relationship('User', back_populates='students')
    enrollments = relationship('Enrollment',back_populates='student')
    marks = relationship('Marks', back_populates='students')
    university = relationship('University', back_populates='students')

class Semester(Base):
    __tablename__ = 'semester'

    id = Column(Integer, primary_key=True)
    term = Column(String, nullable=False)

    enrollments = relationship('Enrollment',back_populates='semesters')

class Marks(Base):
    __tablename__ = 'marks'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('student.id'))
    semester_id = Column(Integer, ForeignKey('semester.id'))
    course_id = Column(Integer, ForeignKey('course.id'))
    mark = Column(Float)

    students = relationship('Student',back_populates='marks')
    course = relationship('Course', back_populates= 'marks')

class Enrollment(Base):
    __tablename__ = 'enrollment'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('student.id'))
    course_id = Column(Integer, ForeignKey('course.id'))
    semester_id = Column(Integer, ForeignKey('semester.id'))
    college_id = Column(Integer, ForeignKey('college.id'))
    
    
    student = relationship('Student',back_populates='enrollments')
    courses = relationship('Course',back_populates='enrollments')
    semesters = relationship('Semester',back_populates='enrollments')
    colleges = relationship('College', back_populates='enrollments')



# when creating relationships, name used in back_populates should same as attribute in another table

#Base.metadata.create_all(engine)

'''
user1 = User(username = 'user1')
user1.set_password('password1')
session.add(user1)

user2 = User(username = 'user2')
user2.set_password('password2')
session.add(user2)

session.commit()

user3 = User(username = 'user2')
user3.set_password('password3')
session.add(user3)

session.commit()'''
