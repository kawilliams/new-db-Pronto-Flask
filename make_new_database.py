#!/usr/bin/python
"""
Creates the course/syllabi database from a Banner dump csv.
"""

import os
import csv
import logging
from flask import (Flask, request, url_for, 
                   redirect, render_template)
from werkzeug import secure_filename
from flask_sqlalchemy import SQLAlchemy


# Table Header indices
ACADEMIC_PERIOD = 0 #2016
MAJOR_CODE = 1
SUBJECT = 2
COURSE_NUMBER = 3
SEQ_NUMBER = 4
CRN = 5
COURSE_TITLE = 6
CREDIT_HRS = 7
COURSE_CREDIT_RANGE = 8
CREDIT_HR_SESSION = 9
MEET_DAYS = 10
BEGIN_TIME = 11
END_TIME = 12
CLASS_TIME = 13
BLDG_CODE = 14 
ROOM_CODE = 15
INSTRUCTOR1 = 16
INSTRUCTOR2 = 17
INSTRUCTOR3 = 18
COURSE_NOTES = 19
COURSE_ATTRIBUTES = 20
MAX_ENROLL = 21
CURR_ENROLL = 22
SEATS_REMAINING = 23


##########################################################################

def read_csv(filename):
    
    """Reads in filename ('filename.csv'), writes contents to nested list"""
    
    courses = []   
    
    CRNs = set()
    
    with open(filename, 'rU') as f:
        
        fReader = csv.reader(f, quotechar = '"', delimiter = ',')
        header = True
        
        for line in fReader: 
            
            if header:
                header = False
                pass            
            else:     
		line[COURSE_ATTRIBUTES] = line[COURSE_ATTRIBUTES].replace(
                    '\r\n', '')   
                courses.append(line)
		
		if ("REGISTER" in line[COURSE_TITLE] or 
		    "REG" in line[COURSE_TITLE] or 
		    "Register" in line[COURSE_TITLE]):
		    
		    CRNs.add(line[CRN])
		
    return courses

##########################################################################

app = Flask(__name__, template_folder = 'templates')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///1617ClassSched.db' 
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


	
class Course(db.Model):
    """ 
    Build outline for Course object. Link instructor# to Professor object 
    """
    __tablename__='courses'
    id = db.Column(db.Integer, primary_key=True)
    
    acad_period = db.Column(db.String(10))
    major_code = db.Column(db.String(10))
    subject = db.Column(db.String(10))
    course_num = db.Column(db.String(10))
    seq_num = db.Column(db.String(10))
    CRN = db.Column(db.String(20))
    course_title = db.Column(db.String(50))
    credit_hrs = db.Column(db.Integer) # changed from string
    crs_cred_range = db.Column(db.String(20))
    cred_hr_session = db.Column(db.String(10))
    meet_days = db.Column(db.String(20))
    begin_time = db.Column(db.String(10))
    end_time = db.Column(db.String(10))
    class_time = db.Column(db.String(20))
    bldg_code = db.Column(db.String(10))
    room_code = db.Column(db.String(10))
    instructor1 = db.Column(db.String(30),db.ForeignKey('professor.dbname'))
    instructor2 = db.Column(db.String(30),db.ForeignKey('professor.dbname'))
    instructor3 = db.Column(db.String(30),db.ForeignKey('professor.dbname'))
    course_notes = db.Column(db.String(20))
    course_attrib = db.Column(db.String(20))
    max_enroll = db.Column(db.Integer) # changed from string
    curr_enroll = db.Column(db.Integer) # changed from string
    seats_remain = db.Column(db.Integer) # changed from string
    
    
    
    syllabus_link = db.Column(db.String(1000), default="")
    visitable= db.Column(db.String(100), default="Can visit" )
    privacy= db.Column(db.String(100), default="All")
    learning_outcomes = db.Column(db.String(2000), default="Cut learning outcomes from syllabus and paste them here")
    lo_status = db.Column(db.String(50), default="Not submitted") 
    all_data = db.Column(db.String(1000))
    
    
    
    def __init__(self, acad_period, major_code, subject, course_num, seq_num,
                 CRN, course_title, credit_hrs, crs_cred_range, cred_hr_session,
                 meet_days, begin_time, end_time, class_time, bldg_code, 
                 room_code, instructor1, instructor2, instructor3, course_notes,
                 course_attrib, max_enroll, curr_enroll, seats_remain, 
                 syllabus_link, visitable, privacy, learning_outcomes, 
                 lo_status): 
	""" 
	Initialization method. Note that the field 'all_data' is 
	generated in this function, it is not passed as a parameter. 
	""" 
	
	self.acad_period = acad_period
	self.major_code = major_code
	self.subject = subject
	self.course_num = course_num
	self.seq_num = seq_num
	self.CRN = CRN
	self.course_title = course_title
	self.credit_hrs = credit_hrs
	self.crs_cred_range = crs_cred_range
	self.cred_hr_session = cred_hr_session
	self.meet_days = meet_days
	self.begin_time = begin_time
	self.end_time = end_time
	self.class_time = class_time
	self.bldg_code = bldg_code
	self.room_code = room_code
	self.instructor1 = instructor1
	self.instructor2 = instructor2
	self.instructor3 = instructor3
	self.course_notes = course_notes
	self.course_attrib = course_attrib
	self.max_enroll = max_enroll
	self.curr_enroll = curr_enroll
	self.seats_remain = seats_remain
	
	self.syllabus_link = syllabus_link
	self.visitable = visitable 
	self.privacy = privacy
	self.learning_outcomes = learning_outcomes
	self.lo_status = lo_status
	self.all_data = (acad_period+subject+course_num+seq_num+
	                 CRN+major_code+course_title+credit_hrs+crs_cred_range+
	                 cred_hr_session+meet_days+begin_time+end_time+
	                 class_time+bldg_code+room_code+instructor1+
	                 instructor2+instructor3+course_notes+course_attrib+
	                 max_enroll+curr_enroll+seats_remain+syllabus_link+
	                 visitable+privacy+learning_outcomes+lo_status)
    
	
    
class Professor(db.Model):
    """
    Build outline for Professor object. Link primary_classes (those for which
    the Professor is listed as instructor1), secondary_classes (those for 
    which the Professor is listed as instructor2), and tertiary_classes (those 
    for which the Professor is listed as instructor3) to the respective 
    Course objects.
    """
    id = db.Column(db.Integer, primary_key=True)
    
    email = db.Column(db.String(30))
    fullname = db.Column(db.String(30))
    dbname = db.Column(db.String(30))
    
    primary_classes = db.relationship("Course", foreign_keys = [Course.instructor1])
    secondary_classes = db.relationship("Course", foreign_keys = [Course.instructor2])
    tertiary_classes = db.relationship("Course", foreign_keys = [Course.instructor3])
    
    def __init__(self,dbname,full_name,username):
	self.dbname=dbname
	self.fullname = full_name
	self.email = username	



# Constant values that depend on the CSV file
FACULTY_NAME = 1
EMAIL = 4
PROF_CSV = "FacultyInformation.csv" # file with most of the faculty
PROF2_CSV = "Additional.csv" # faculty that weren't in PROF_CSV




def make_faculty_fromCSV(csvFile):
    """
    Constructs Professor objects from a csv file that contains the professor's 
    name and email address. The objects contain db_name (last name + ' ' + 
    first initial e.g. Staff S), f_name (full name), f_email 
    (username@davidson.edu).
    
    Parameters: 
        csvFile - a csv file of professor information (full name, email)
    Returns: 
        faculty_list - a list of Professor objects
    """
    faculty_list = []

    # open file and create reader
    with open(csvFile, 'rU') as c:
	reader = csv.reader(c, delimiter=',', quotechar='"',
                            skipinitialspace=True)

	row_count = 0
	for row in reader:
	    if row_count != 0:

		f_name = row[FACULTY_NAME].strip()
		db_name = (f_name.split(",")[0].strip() + " " + 
		           f_name.split(",")[1].strip()[:1])
		f_email = row[EMAIL].strip()

		a_faculty = Professor(db_name,f_name,f_email)
		
		faculty_list.append(a_faculty)

	    row_count+=1
	    
    return faculty_list

	
def build_db(courses):
    """
    Builds a database of Courses from a list of the rows from the course csv.
    Prints the number of rows and the number of database entries, which
    should be equal.
    
    Parameters: 
        courses - a list of rows (list) where each row is information about a course
        
    """
    db.create_all()
    count = 0
    for c in courses:	
	count += 1
	course = Course(c[ACADEMIC_PERIOD], c[MAJOR_CODE], c[SUBJECT], 
	                c[COURSE_NUMBER], c[SEQ_NUMBER], c[CRN], 
	                c[COURSE_TITLE], c[CREDIT_HRS], c[COURSE_CREDIT_RANGE],
	                c[CREDIT_HR_SESSION], c[MEET_DAYS], c[BEGIN_TIME],
	                c[END_TIME], c[CLASS_TIME], c[BLDG_CODE], c[ROOM_CODE], 
	                c[INSTRUCTOR1], c[INSTRUCTOR2], c[INSTRUCTOR3],
	                c[COURSE_NOTES], c[COURSE_ATTRIBUTES], c[MAX_ENROLL],
	                c[CURR_ENROLL], c[SEATS_REMAINING], "", "Can visit", 
	                "All", "Cut learning outcomes from syllabus and paste them here", "Not submitted")
	
	db.session.add(course)
	
    
    faculty_list1 = make_faculty_fromCSV(PROF_CSV)
    faculty_list2 = make_faculty_fromCSV(PROF2_CSV)
    faculty_list = faculty_list1 + faculty_list2
    db.session.add_all(faculty_list)
    db.session.commit()
    
    print "CSV COUNT = " + str(count)
    q = Course.query.count()
    print "DATABASE COUNT = ", q 
    return



def main():
    """
    To construct the database, comment in the first three lines with the 
    app.run line commented out. Save this file. Run this file. Comment back 
    out the three lines.
    
    To view the database, make sure the three lines are commented out. 
    Comment-in the app.run line. Go to http://127.0.0.1:5000/
    
    If the database was built properly, in the terminal window you should
    see "CSV COUNT" and "DATABASE COUNT" are equal. If DATABASE COUNT is
    multiple times greater than CSV COUNT, check how you constructed the
    database.
    """
    # Comment-in these 3 lines to build the database
    filename = "static/1617ClassSchedule.csv"
    courses = read_csv(filename)
    build_db(courses)
    # end of "Build Database" part


if __name__ == "__main__":
    main()
    