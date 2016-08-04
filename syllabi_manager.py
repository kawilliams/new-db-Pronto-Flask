import os

from flask import (Flask, render_template, redirect, url_for,
                   request, send_from_directory, send_file)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import distinct,func
from flask_mail import Mail,Message
from check import *
import dropbox

from model import *
from local_model import *

import logging
import datetime


PASSWORD_INPUT = "password"

app = Flask(__name__)
app.debug=True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# need to replace the hardcoded user info by a file to be read from somewhere
# other than /var/www/html (so random people can't access it) 
SENDER_ACC = "findacourse.davidson@gmail.com"
ACC_PASSWORD = "sy11abus"

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = SENDER_ACC
app.config["MAIL_PASSWORD"] = ACC_PASSWORD
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_DEFAULT_SENDER"] = SENDER_ACC
mail = Mail(app)

s = db_session()
ls = localdb_session()


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



def initialize(semester):
    

    courses = (Course.query.filter_by(acad_period=semester)).all()
    
    
    syl_man_dict={}
    
    count_syl = set()
    count_profs = set()
    for c in courses:
	if c.major_code not in syl_man_dict:
	    syl_man_dict[c.major_code]=[{c.instructor1:[[],True]},True]  
	    
	  
	if c.instructor1 in syl_man_dict[c.major_code][0].keys():
	    syl_man_dict[c.major_code][0][c.instructor1][0].append(c)
	    
	else:
	    syl_man_dict[c.major_code][0][c.instructor1] = [[c],True]

	if c.syllabus_link == "":
	    count_syl.add(c.acad_period + c.CRN)
	    count_profs.add(c.instructor1)
	    syl_man_dict[c.major_code][0][c.instructor1][1] = False
	    syl_man_dict[c.major_code][1] = False
	
	
    return syl_man_dict, len(count_syl), len(count_profs)


def dep_count_missing(syl_man_dict, sub):
    count_profs = 0
    count_syl = 0
    prof_list = syl_man_dict[sub][0]
    for prof in prof_list:
	
	if prof_list[prof][1] == False:
	    
	    count_profs += 1
	    # prof_list[prof][0] is the list of courses for a prof
	    for c in prof_list[prof][0]: 
		if c.syllabus_link == "":
		    count_syl += 1		
    
    return count_syl, count_profs


def prof_count_missing(syl_man_dict, sub, prof):
    count_profs = 0
    count_syl = 0
    course_list = syl_man_dict[sub][0][prof][0]
    for c in course_list:
	if c.syllabus_link == "":
	    count_syl += 1
	    count_profs = 1
	    
    return count_syl, count_profs


def sort_dep(syl_man_dict):
    
    dep_dict={}

    for deps in syl_man_dict:
	dep_dict[deps] = syl_man_dict[deps][1]
	
    
    return dep_dict,sorted(dep_dict.keys())
	
		
		    
#def syllabi_prof(prof, semester, subject):
    #prof_courses = Course.query.filter_by(instructor1=prof).\
        #filter_by(acad_period=semester).\
        #filter_by(major_code=subject).all()
    
    #missing_syll = []
    #for i in prof_courses:
	#if i.syllabus_link == "":
	    #missing_syll.append(i)
    
    #unique_courses = determine_unique(missing_syll)

    #return len(unique_courses)

#def determine_unique(primary):
    #unique = []
    #for course in primary:
        #if "REG" not in course.course_title:
            #if not (course.CRN in build_CRN_string(unique)):
                #unique.append(course)
    #return unique

#def build_CRN_string(unique):
    #""" Helper function for determine_unique """
    #CRN_string =""
    #for i in unique:
        #CRN_string += i.CRN+" "
    #return CRN_string
    


#def format_prof(profSet,subj):
    #"""
    #Given a set of professors, this function returns a dictionary whose keys
    #are the professors and the value is either the string 'True' or 'False'.
    #It is 'True' if the professor submitted syllabus for all his courses under
    #the given department. Otherwise its 'False'
    #"""
    #semester=determine_semester()
           
    #prof_dict ={}
    
    #for i in profSet:
        #prof_dict[i] = "True"
	
        #pro_crs = (Course.query.filter_by(instructor1=i).
	           #filter_by(major_code=subj).
	           #filter_by(acad_period = semester)).all()
	
	
        #for j in pro_crs:
            #if j.syllabus_link == "":
                #prof_dict[i] = "False"
		#break
   
    #return prof_dict

#def format_subj(subjset,semester):
    #"""
    #Given a set of department, this function returns a dictionary whose keys
    #are the department and the value is either the string 'True' or 'False'.
    #It is 'True' if all the courses under the department have a corresponding
    #syllabus submitted. Otherwise its 'False'
    #"""
           
    #subj_dict = {}
    #for i in subjset:
        #subj_dict[i] = "True"
        #subj_cour = Course.query.filter_by(major_code=i).\
	    #filter_by(acad_period=semester).all()
	
	
        #for j in subj_cour: 
            #if j.syllabus_link == "":
                #subj_dict[i] = "False"
		#break
    
    #return subj_dict

#def find_recip(PROFESSORS):
    #semester=determine_semester()

    
    #profList=[]
    
    ##for i in PROFESSORS:
	
	##prof = Faculty.query.filter_by(fullname=i).all()[0] #bad style 
	##pro_courses = prof.primary_classes(semester).all()
	
	##for j in pro_courses:
	    ##if j.syllabus_link == "":
		##profList.append(i)


    #return profList
    
    
@app.route("/", methods=["GET", "POST"])
def manage_form():
    semester=determine_semester()
           
    SYL_MAN_DICT, SYL_MISS, PROF_MISS =initialize(semester)
    DEPT_BOOL,DEPT_SORTED = sort_dep(SYL_MAN_DICT)
    
  
    #subjList = format_subj(SUBJ_SET)
    profs_no_syl = []    
       
    if request.method == 'POST':

    	active_pro = request.form["active_prof"]
    	active_subj = request.form["active_dep"]
	
	if active_subj != "":
	    PROFESSORS = sorted(SYL_MAN_DICT[active_subj][0].keys())
		
	#find button values
    	subject_btn_on = request.form["dep_btn_submit"]
    	prof_btn_on = request.form["prof_btn_submit"]

    	sub = request.form['submit']    	
	 
        # A department has been selected.
    	if sub in DEPT_SORTED:
	    
	    #subject_courses = Course.query.filter_by(major_code=sub).\
			#filter_by(acad_period=semester).\
	                #order_by(Course.instructor1)
	    
    	    active_subj = sub
	    
	    # compute percentage
	    percent_syl = 0 #(float(count_mis_syll(active_subj))/
			     #      subject_courses.count())*100
		        
    	    prof_inDep = sorted(SYL_MAN_DICT[active_subj][0].keys())
	
	    
	    #profList = format_prof(prof_inDep,active_subj)
	    
	    #get number of missing syllabi in department
	    dep_syl, dep_prof = dep_count_missing(SYL_MAN_DICT, sub)
	 
	    
    	    return render_template("syllabi_manager.html", deps=DEPT_BOOL,
	                               depsSorted=DEPT_SORTED,
	                               depBtnOn=subject_btn_on,profBtnOn="",
	                               profsSorted=prof_inDep,
	                               profs_courses="",
	                               miss_syl=dep_syl, #might be added if its not slow
	                               miss_prof=dep_prof,#might be added if its not slow
	                               active_dep=active_subj,
	                               active_prof = "",
	                               recipients=profs_no_syl, 
	                               syll_percent="",#might be added if its not slow
	                               semester=semester)

        # A professor in a department has been selected
    	if sub in PROFESSORS:
	    
	    active_pro = sub
	    active_subj = request.form["active_dep"]
	    # compute percentage
	    #percent_syl = (float(count_mis_syll(active_pro))/
			           #Course.query.filter(Course.subject.like(
	                               #active_subj)).filter_by(acad_period=semester).count())*100

	    subject_btn_on = request.form["dep_btn_submit"]
	    prof_btn_on = request.form["prof_btn_submit"]	    
		
	    
    	    profs_courses = SYL_MAN_DICT[active_subj][0][active_pro][0]
	    
	    prof_syl, prof_prof = prof_count_missing(SYL_MAN_DICT, active_subj, active_pro)
	    
	    
	    
    	    return render_template("syllabi_manager.html", deps=DEPT_BOOL,
	                            depsSorted=DEPT_SORTED,
	                            depBtnOn=subject_btn_on,
	                            profBtnOn=prof_btn_on,
	                            profsSorted=PROFESSORS,
	                            profs_courses=profs_courses,
	                            miss_syl=prof_syl,
	                            miss_prof=prof_prof,
	                            active_dep=active_subj,
	                            active_prof=active_pro,
	                            recipients=profs_no_syl,
	                            syll_percent="",
	                            semester=semester)

    
    return render_template("syllabi_manager.html", deps=DEPT_BOOL,
                           depsSorted=DEPT_SORTED,
                           depBtnOn="False", profBtnOn="False",
                           profs='',profs_courses='',
                           miss_syl=SYL_MISS,
                           miss_prof=PROF_MISS,active_dep="",
                           active_prof="",
                           recipients=profs_no_syl,
                           syll_percent="",
                           semester=semester)


def get_professor(db_name,dep,semester):
    # get a professor object given dep and db_name(and semester)
    courses = (Course.query.filter_by(major_code=dep).
         filter_by(instructor1 = db_name).
         filter_by(acad_period = semester).all())
    
    if len(courses)==0:
	return None
    
    # The final list should just have only one id - It should but it may not
    prof_id = list(set([c.instructor1_id for c in courses]))[0]

    return Faculty.query.filter(Faculty.id==prof_id).first()

    
    
@app.route("/email",methods=["GET","POST"])
def email():
    """
    This might need editing.
    """
    
    semester=determine_semester()
    SYL_MAN_DICT, SYL_MISS, PROF_MISS = initialize(semester)
    DEPT_BOOL,DEPT_SORTED = sort_dep(SYL_MAN_DICT)    
    
    
    if request.method == "POST":
	
	message = request.form["message"]
	title = request.form["title"]
	password = request.form["password"]
	
	subject_btn_on = "True"
	prof_btn_on = "True" 
	
	
	active_dep = request.form["activedep_email"]
	active_prof = request.form["recipient"]  # active_prof is the recipient
	
	prof_inDep = sorted(SYL_MAN_DICT[active_dep][0].keys())
	profs_courses = SYL_MAN_DICT[active_dep][0][active_prof][0]    
	
	prof_syl, prof_prof=prof_count_missing(SYL_MAN_DICT,active_dep,active_prof)
	
	for i in request.form:
	    print i.center(25," "),"  ---> ",request.form[i]
	    
	# could use flash to confirm that an email has been sent (or not)
	if check_password(password):
	    
	    prof = get_professor(active_prof,active_dep,semester)
	    # for testing purposes Katy will have to deal with random emails 
	    # and clutter.
	    # To actually make this work, change Katy's email to the variable
	    # prof.email
	    
	    if prof:
		msg = Message(recipients=["kawilliams@davidson.edu"],
		              html=message,subject=title)	    
		mail.send(msg)
		
		info = "Email sent!"
	    else:
		info = "Something went wrong. Email not sent!"
	
	
	else:
	    
	    info = " Incorrect Password. Email not sent!"
	    
	    
	return render_template("syllabi_manager.html", deps=DEPT_BOOL,
                               depsSorted=DEPT_SORTED,
                               depBtnOn=subject_btn_on, profBtnOn=prof_btn_on,
                               profsSorted=prof_inDep,
                               profs_courses=profs_courses, 
                               miss_syl=prof_syl,
                               miss_prof=prof_prof,
                               active_dep=active_dep,
                               active_prof=active_prof,
                               recipients=[],
                               syl_percent="",
                               semester=semester,msg=info)
    return redirect(url_for('manage_form'))
	


def syll_miss_profs(semester):
    pass

def lo_miss_profs(semester):
    pass


@app.route("/emailall",methods=["GET","POST"])
def email_all():
    """
    This might need editing.
    """
    
    semester=determine_semester()
    SYL_MAN_DICT, SYL_MISS, PROF_MISS = initialize(semester)
    DEPT_BOOL,DEPT_SORTED = sort_dep(SYL_MAN_DICT)    
    
    
    if request.method == "POST":
	
	message = request.form["message"]
	title = request.form["title"]
	password = request.form["password"]
	
	email_type = request.form["email_type"]

	if check_password(password):
	    
	    # determine whether to send to prof missing syllabus or lo
	    if email_type == "syllabus_missing":
		profs = syll_miss_profs(semester)
	    else:
		profs = lo_miss_profs(semester)
	    
	    
	    if len(profs)!=0:
		
		info = ""
		
		# this is a prefered way of sending bulk emails. 
		# for testing purposes Katy will have to deal with random  
		# emails and clutter - sorry katy.
		# To actually make this work, change Katy's email to the 
		# variable prof.email	
		
		with mail.connect() as conn:
		    for prof in profs:
			msg = Message(recipients=["kawilliams@davidson.edu"],
				      html=message,subject=title)
			try:
			    conn.send(msg)
			except:
			    info += "Email not sent for "+ prof.fullname +"\n"
			
		if info == "":
		    info = "All emails sent!"
		
	    else:
		if email_type == "syllabus_missing":
		    info = "All professors have submitted their syllabus!"
		else:
		    info = "All professors have proper learning outcomes!"
	    
	
	else:
	    info = "Incorrect P@s5w0rd"
	
	
	return render_template("syllabi_manager.html", deps=DEPT_BOOL,
                               depsSorted=DEPT_SORTED,
                               depBtnOn="False", profBtnOn="False",
                               profs='',profs_courses='',
                               miss_syl=SYL_MISS,
                               miss_prof=PROF_MISS,active_dep="",
                               active_prof="",
                               recipients=[],
                               syll_percent="",
                               semester=semester,
                               msg=info)
	
    return redirect(url_for('manage_form'))

@app.route('/update_status', methods=["GET", "POST"])
def update_status():
    
    semester=determine_semester()
    SYL_MAN_DICT, SYL_MISS, PROF_MISS = initialize(semester)
    DEPT_BOOL,DEPT_SORTED = sort_dep(SYL_MAN_DICT)
    
    if request.method == "POST":
	#print request.form
	form_status = request.form["status"]
	setting_id = request.form["setting_id"]
	active_dep = request.form["activedep"]
	active_prof = request.form["activeprof"]
    
	
	percent_syl = ""#(float(count_mis_syll(active_prof))/
		                           #Course.query.filter(Course.subject.like(
		                               #active_dep)).filter_by(acad_period=semester).count())*100  
	subject_btn_on = "True"
	prof_btn_on = "True"
		
	prof_inDep = sorted(SYL_MAN_DICT[active_dep][0].keys())
	profs_courses = SYL_MAN_DICT[active_dep][0][active_prof][0]

	
	prof_syl, prof_prof = prof_count_missing(SYL_MAN_DICT, active_dep, active_prof)    
	
	
	stat_dictionary = {
	    "not_submitted" : "Not submitted",
	    "not_viewed" : "Not viewed",
	    "needs_edits" : "Viewed, needs edits",
	    "approved" : "Approved"    
	    }
	
	if check_password(request.form["password"]):
	    
	    #print ("getting the setting").center(80,"*")
	    setting = ls.query(Settings).filter_by(id=setting_id).all()[0]
	    #print ("got it").center(80,"*")
	    setting.lo_status = stat_dictionary[form_status]		
	    ls.commit()
	else:
	    return render_template("syllabi_manager.html", deps=DEPT_BOOL,
                           depsSorted=DEPT_SORTED,
                           depBtnOn=subject_btn_on, profBtnOn=prof_btn_on,
	                   profsSorted=prof_inDep,
                           profs_courses=profs_courses, 
                           miss_syl=prof_syl,
                           miss_prof=prof_prof,
                           active_dep=active_dep,
                           active_prof=active_prof,
                           recipients=[],
                           syl_percent="",
                           semester=semester, msg="Incorrect password")	    
    
    
    return render_template("syllabi_manager.html", deps=DEPT_BOOL,
                           depsSorted=DEPT_SORTED,
                           depBtnOn=subject_btn_on, profBtnOn=prof_btn_on,
                           profsSorted=prof_inDep,
                           profs_courses=profs_courses, 
                           miss_syl=prof_syl,
                           miss_prof=prof_prof,
                           active_dep=active_dep,
                           active_prof=active_prof,
                           recipients=[],
                           syl_percent="",
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

ACCESS_TOKEN_FILE = "/var/www/html/FindACourse/access_token.txt"
DROPBOX_ACCESS_TOKEN = open(ACCESS_TOKEN_FILE,'r').read()

@app.route('/<path:file_path>')
def download(file_path):
    file_name = (file_path.split("/")[-1])
    client = dropbox.client.DropboxClient(DROPBOX_ACCESS_TOKEN)
    f = client.get_file(file_path)
    return send_file(f,attachment_filename=file_name)

@app.teardown_appcontext
def shutdown_session(exception=None):
	db_session.remove()
	localdb_session.remove()
	
if __name__ =="__main__":

    app.run(debug=True)
