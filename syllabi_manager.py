import os

from flask import (Flask, render_template, redirect, url_for,
                   request, send_from_directory, send_file)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import distinct,func
#from flask_mail import Mail,Message
from make_new_database import *
import dropbox

import logging
import datetime



app = Flask(__name__)
app.debug=True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# mail setup. Assumes a gmail account
#SENDER_ACC = "someemail@gmail.com"
#ACC_PASSWORD = "passwordForTheAcc"

#app.config["MAIL_SERVER"] = "smtp.gmail.com"
#app.config["MAIL_PORT"] = 465
#app.config["MAIL_USERNAME"] = SENDER_ACC
#app.config["MAIL_PASSWORD"] = ACC_PASSWORD
#app.config["MAIL_USE_TLS"] = False
#app.config["MAIL_USE_SSL"] = True
#app.config["MAIL_DEFAULT_SENDER"] = SENDER_ACC
#mail = Mail(app)

# need to replace this with dropbox download
UPLOAD_FOLDER = 'all_syllabi/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def initialize():
    semester=determine_semester()
    
    courses = Course.query.filter_by(acad_period=semester).all()
    allcourses = Course.query.all()
    
    prof=set()
    subject=set()
    
    for c in courses:
	prof.add(c.instructor1.strip())
	prof.add(c.instructor2.strip())
	prof.add(c.instructor3.strip())
    if "" in prof:
	prof.remove('')
    for c in courses:
	subject.add(c.subject.strip())
	
    return prof,subject

def determine_semester():
    
    current = datetime.date.today()
    first_sem = current.replace(month=7, day=1), current.replace(month=12, day=20)
    if first_sem[0] <= current <= first_sem[1]:
	# first semester
	return str(current.year) + "01"
    else:
	# second semester
	previous_yr = current.replace(month=1, day=1) - datetime.timedelta(days=1)
	return str(previous_yr.year) + "02"
    

def count_mis_syll(subj):
    """
    Get the number of classes with missing syllabus in a given
    subject.
    """
    semester=determine_semester()
    if subj != "":
	
	courses = Course.query.filter_by(subject=subj).filter_by(acad_period=semester).\
	    filter_by(syllabus_link="").\
	    count()
    else:
	courses = Course.query.filter_by(acad_period=semester).filter_by(syllabus_link="").count()
        
    return str(courses)



def count_mis_prof(subj):
    """
    Get the number of professors who haven't yet submitted a syllabus for
    any of their classes in that subject.
    """
    semester=determine_semester()
    if subj != "":
	courses = Course.query.filter_by(subject=subj).\
	    filter_by(acad_period=semester).filter_by(syllabus_link="").all()
    else:
	courses = Course.query.filter_by(acad_period=semester).filter_by(syllabus_link="").all()	
    
    pro_miss=set()
    for i in courses:
	pro_miss.add(i.instructor1.strip())
	#pro_miss.add(i.instructor2.strip())
	#pro_miss.add(i.instructor3.strip())
    if "" in pro_miss:
	pro_miss.remove('')   
	
    return str(len(pro_miss))

def binary_prof(num_prof_is_missing):
    if num_prof_is_missing > 0:
	return 1
    return 0
    
def syllabi_prof(prof, semester, subject):
    prof_courses = Course.query.filter_by(instructor1=prof).\
        filter_by(syllabus_link="").\
        filter_by(acad_period=semester).\
        filter_by(subject=subject).all()
    unique_courses = determine_unique(prof_courses)

    return len(unique_courses)

def determine_unique(primary):
    unique = []
    for course in primary:
        if "REG" not in course.course_title:
            if not (course.CRN in build_CRN_string(unique)):
                unique.append(course)
    return unique

def build_CRN_string(unique):
    """ Helper function for determine_unique """
    CRN_string =""
    for i in unique:
        CRN_string += i.CRN+" "
    return CRN_string
    


def format_prof(profSet,subj):
    """
    Given a set of professors, this function returns a dictionary whose keys
    are the professors and the value is either the string 'True' or 'False'.
    It is 'True' if the professor submitted syllabus for all his courses under
    the given department. Otherwise its 'False'
    """
    semester=determine_semester()
           
    #courses = Course.query.filter_by(subject=subj).filter_by(acad_period=semester)
    prof_dict ={}
    
    for i in profSet:
        prof_dict[i] = "True"
        pro_cour = Course.query.filter_by(acad_period=semester).\
	    filter_by(subject=subj).\
	    filter_by(instructor1=i).all()
        for j in pro_cour:
            if j.syllabus_link == "":
                prof_dict[i] = "False"
   
    return prof_dict

def format_subj(subjset):
    """
    Given a set of department, this function returns a dictionary whose keys
    are the department and the value is either the string 'True' or 'False'.
    It is 'True' if all the courses under the department have a corresponding
    syllabus submitted. Otherwise its 'False'
    """
    semester=determine_semester()
           
    subj_dict = {}
    for i in subjset:
        subj_dict[i] = "True"
        subj_cour = Course.query.filter_by(subject=i).\
	    filter_by(acad_period=semester).all()
        for j in subj_cour:
            if j.syllabus_link == "":
                subj_dict[i] = "False"
    
    return subj_dict

def find_recip(PROFESSORS):
    semester=determine_semester()
           
    courses = Course.query
    
    profList=[]
    
    for i in PROFESSORS:

	pro_courses = Course.query.filter_by(instructor1=i).\
	    filter_by(acad_period=semester).all()


    return profList
    
    
@app.route("/", methods=["GET", "POST"])
def manage_form():
    semester=determine_semester()
           
    PROFESSORS,SUBJ_SET=initialize()
    subjList = format_subj(SUBJ_SET)
    profs_no_syl = []    
       
    if request.method == 'POST':

    	active_pro = request.form["active_prof"]
    	active_subj = request.form["active_dep"]
		
	#find button values
    	subject_btn_on = request.form["dep_btn_submit"]
    	prof_btn_on = request.form["prof_btn_submit"]

    	sub = request.form['submit']    	
	 
        # A department has been selected.
    	if sub in subjList:
	    
	    subject_courses = Course.query.filter_by(subject=sub).\
			filter_by(acad_period=semester).order_by(Course.course_num)
	    
    	    active_subj = sub
	    
	    # compute percentage
	    percent_syl = (float(count_mis_syll(active_subj))/
			           subject_courses.count())*100
		        
    	    prof_inDep = set()
	    
    	    for dc in subject_courses:
    		prof_inDep.add(dc.instructor1.strip())
				
	    if "" in prof_inDep:
		prof_inDep.remove("")
	    
	    profList = format_prof(prof_inDep,active_subj)
	 
	    
    	    return render_template("syllabi_manager.html", deps=subjList,
	                               depsSorted=sorted(subjList.keys()),
	                               depBtnOn=subject_btn_on,profBtnOn=prof_btn_on,
	                               profs=profList,
	                               profsSorted=sorted(profList.keys()),
	                               profs_courses="",
	                               miss_syl=count_mis_syll(sub),
	                               miss_prof=count_mis_prof(sub),
	                               active_dep=active_subj,
	                               active_prof = active_pro,
	                               recipients=profs_no_syl, 
	                               syll_percent=str(percent_syl),
	                               semester=semester)

        # A professor in a department has been selected
    	if sub in PROFESSORS:
	    
	    active_pro = sub
	    # compute percentage
	    percent_syl = (float(count_mis_syll(active_pro))/
			           Course.query.filter(Course.subject.like(
	                               active_subj)).filter_by(acad_period=semester).count())*100

	    subject_btn_on = request.form["dep_btn_submit"]
	    prof_btn_on = request.form["prof_btn_submit"]	    
	    
    	    subject_courses = Course.query.filter_by(subject=active_subj).\
	            filter_by(acad_period=semester).\
	            order_by(Course.course_num)
    	    prof_inDep = set()
	        
	    
    	    for dc in subject_courses:
                prof_inDep.add(dc.instructor1.strip())
		
		#remove courses that are listed under multiple majors
		
		
    	    profs_courses = subject_courses.filter_by(instructor1=sub).all()
            profList = format_prof(prof_inDep,active_subj)
	    num_prof_is_missing = syllabi_prof(active_pro, semester, active_subj)
    	    return render_template("syllabi_manager.html", deps=subjList,
	                            depsSorted=sorted(subjList.keys()),
	                            depBtnOn=subject_btn_on,profBtnOn=prof_btn_on,
	                            profs=profList,
	                            profsSorted=sorted(profList.keys()),
	                            profs_courses=profs_courses,
	                            miss_syl=num_prof_is_missing,
	                            miss_prof=binary_prof(num_prof_is_missing),
	                            active_dep=active_subj,
	                            active_prof=active_pro,
	                            recipients=profs_no_syl,
	                            syll_percent=str(percent_syl),
	                            semester=semester)

    miss_syll = count_mis_syll("")
    miss_prof = count_mis_prof("")
    
    return render_template("syllabi_manager.html", deps=subjList,
                           depsSorted=sorted(subjList.keys()),
                           depBtnOn="False", profBtnOn="False",
                           profs='',profs_courses='',
                           miss_syl=miss_syll,
                           miss_prof=miss_prof,active_dep="",
                           active_prof="",
                           recipients=profs_no_syl,
                           syll_percent=99,
                           semester=semester)


def get_professors(profs):
    # right now nothing but it could be as simple as follows:
    # return Professor.query.filter(Professor.user_name.in_(profs))
    # the professor table must have a user_name file that is exactly like
    # the Course.instructor1 field.
    pass
    
@app.route("/email",methods=["GET","POST"])
def email():
    """
    This might need editing. We can not test this now since we don't have
    professors table
    """
    semester=determine_semester()
    PROFESSORS,SUBJ_SET=initialize()
    subjList = format_subj(SUBJ_SET)
    
    if request.method == "POST":
        recipients = str(request.form["recipients"]).split(",")
        #message = request.form["message"]
	
        # Idealy we would have a professors table with email and name (at least)
        # the get_professors function would query from that table
        #professor = get_professors(recipients)

        #with mail.connect() as conn:
            #for prof in recipients:
                #name = prof.fname + " " +prof.lname
                #message = "Hello, " + name +"\n\n" + message
                #msg = Message(recipients=[prof.email],
                              #body=message,subject="Missing Syllabus")
                #conn.send(msg)


    # Maybe we need to add some page or message that says emails have been sent
    semester=determine_semester()
           
    courses = Course.query.filter_by(acad_period=semester).all()
    #get all professors
    profsSet = set()
    for c in courses:
        profsSet.add(c.instructor1.strip())
    #get all departments
    subjList = format_subj(SUBJ_SET)

    profs_no_syl = find_recip(PROFESSORS)

    return render_template("syllabi_manager.html", deps=subjList,
                           depsSorted=sorted(subjList.keys()),
                           depBtnOn="False", profBtnOn="False",
                           profs='',profs_courses='',
                           miss_syl=count_mis_syll(""),
                           miss_prof=count_mis_prof(""),active_dep="",
                           active_prof="",
                           recipients=profs_no_syl,
                           semester=semester)

@app.route('/update_status', methods=["GET", "POST"])
def update_status():
    semester=determine_semester()
    PROFESSORS,SUBJ_SET=initialize()
    subjList = format_subj(SUBJ_SET)
    
    if request.method == "POST":
	print request.form
	form_status = request.form["status"]
	CRN = request.form["CRN"]
	active_dep = request.form["activedep"]
	active_prof = request.form["activeprof"]
	course = Course.query.filter_by(acad_period=semester).filter_by(CRN=CRN).all()
	print course
	stat_dictionary = {
	    "not_submitted" : "Not submitted",
	    "not_viewed" : "Not viewed",
	    "needs_edits" : "Viewed, needs edits",
	    "approved" : "Approved"    
	    }
	for c in course:
	    setattr(c, 'lo_status', stat_dictionary[form_status])
	 
    percent_syl = (float(count_mis_syll(active_prof))/
			           Course.query.filter(Course.subject.like(
	                               active_dep)).filter_by(acad_period=semester).count())*100  
    subject_btn_on = "True"
    prof_btn_on = "True"
    	    
    courses = Course.query.filter_by(acad_period=semester).all()
    #get all professors
    profsSet = set()
    for c in courses:
        profsSet.add(c.instructor1.strip())
    #get all departments
    subjList = format_subj(SUBJ_SET)
    profs_no_syl = find_recip(PROFESSORS)
    subject_courses = Course.query.filter_by(subject=active_dep).\
	                filter_by(acad_period=semester).\
	                order_by(Course.course_num)
    prof_inDep = set()		
    for dc in subject_courses:
	prof_inDep.add(dc.instructor1.strip())
	
    profs_courses = subject_courses.filter_by(instructor1=active_prof).all()
    profList = format_prof(prof_inDep,active_dep)
    num_prof_is_missing = syllabi_prof(active_prof, semester, active_dep)
    
    db.session.commit()
    return render_template("syllabi_manager.html", deps=subjList,
                           depsSorted=sorted(subjList.keys()),
                           depBtnOn=subject_btn_on, profBtnOn=prof_btn_on,
                           profs=profList, profsSorted=sorted(profList.keys()),
                           profs_courses=profs_courses, 
                           miss_syl=num_prof_is_missing,
                           miss_prof=binary_prof(num_prof_is_missing),
                           active_dep=active_dep,
                           active_prof=active_prof,
                           recipients=profs_no_syl,
                           syl_percent=str(percent_syl),
                           semester=semester)


@app.route('/syllabi/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



'''
Add this snippet to enable downloading for the dropbox.
You can download the syllabus for a course,c, where the correct path to the 
syllabus is stored in "c.syllabus_link". 

The link to follow to download the syllabus can be generated by:

url_for('download',file_path=c.syllabus_link)

'''

ACCESS_TOKEN_FILE = "access_token.txt"
DROPBOX_ACCESS_TOKEN = open(ACCESS_TOKEN_FILE,'r').read()

@app.route('/<path:file_path>')
def download(file_path):
    file_name = (file_path.split("/")[-1])
    client = dropbox.client.DropboxClient(DROPBOX_ACCESS_TOKEN)
    f = client.get_file(file_path)
    return send_file(f,attachment_filename=file_name)


if __name__ =="__main__":
    
    db.create_all()
    
    app.run(debug=True)
