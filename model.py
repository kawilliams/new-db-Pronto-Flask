model.py

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, relationship, scoped_session,mapper
from sqlalchemy.ext.declarative import declarative_base
import datetime
# set up connection and connect

with open("connection_string.txt",'r') as f:
    CONNECTION_STR = f.read()

engine = create_engine(CONNECTION_STR)
meta = MetaData(bind=engine)

faculty_view = Table('FACULTY',
                     meta,
                     # set primary_key
                     Column('instr_id',primary_key=True),
                     
                     # very important beacuse the 'names' we have are actually
                     # synonyms
                     
                     oracle_resolve_synonyms=True,
                     autoload=True)

course_view = Table('COURSE_SCHEDULE_DC_EXT',
                    meta,
                    # set foreign keys
                    Column('instructor1_id',Integer,ForeignKey('FACULTY.instr_id')),
                    Column('instructor2_id',Integer,ForeignKey('FACULTY.instr_id')),
                    Column('instructor3_id',Integer,ForeignKey('FACULTY.instr_id')),
                    
                    # set how to uniquely identify courses
                    Column('academic_period',primary_key=True),
                    Column('major_code',primary_key=True),
                    Column('seq_number',primary_key=True),
                    Column('crn',primary_key=True),
                    Column('course_title',primary_key=True),
                    Column('subject',primary_key=True),
                    Column('class_time',primary_key=True),
                    Column('bldg_code',primary_key=True),
                    Column('room_code',primary_key=True),
                    
                    # very important beacuse the 'names' we have are actually
                    # synonyms
                    
                    oracle_resolve_synonyms=True,
                    autoload=True)





class Course(object):
    def __repr__(self):
        
        return ("<"+" ".join([self.acad_period,self.subject,
                self.course_number,self.major_code,self.seq_num,
                self.course_title,self.instructor1,self.bldg_code,
                             self.room_code])+">")
    

mapper(Course,course_view,
       properties={
                   'acad_period':course_view.c.academic_period,
                   'CRN':course_view.c.crn,
                   'seats_remain':course_view.c.seats_remaining,
                   'seq_num':course_view.c.seq_number,
                   'course_attrib':course_view.c.course_attributes
                   })
    

    
class Faculty(object):
    
    def __repr__(self):
        
        return "<"+self.fullname + " " + self.email+">"
    
    
    def primary_classes(self,acd):
        classes = []
        for i in self.primary:
            if i.acad_period == acd:
                classes.append(i)
        return classes
    
    def secondary_classes(self,acd):
        classes = []
        for i in self.secondary:
            if i.acad_period == acd:
                classes.append(i)
        return classes
    
    def tertiary_classes(self,acd):
        classes = []
        for i in self.tertiary:
            if i.acad_period == acd:
                classes.append(i)
        return classes    
        

mapper(Faculty,faculty_view,
       properties={
                   'id':faculty_view.c.instr_id,
                   'fullname':faculty_view.c.name,
                   'email':faculty_view.c.campus_email,
                   'primary' : relationship(Course,foreign_keys=[Course.instructor1_id]),
                   'secondary' : relationship(Course,foreign_keys=[Course.instructor2_id]),
                   'tertiary' : relationship(Course,foreign_keys=[Course.instructor3_id]),
                   })



Session = scoped_session(sessionmaker(bind=engine))


if __name__ == "__main__":
    s=Session()
    heyer = s.query(Faculty).filter(Faculty.fullname.ilike("%heyer%")).all()[0]
    a=heyer.primary_classes("201601")
    print len(a)
    for i in a:
        print i