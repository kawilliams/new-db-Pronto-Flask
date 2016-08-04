import os
import logging
from flask import (Flask, request, flash, url_for, 
                   redirect, render_template,
                   send_from_directory, send_file)
from werkzeug import secure_filename
from flask_sqlalchemy import SQLAlchemy
from model import *
from local_model import *
import dropbox

""" 
For the faculty to upload their syllabi. Queries the database once the
faculty member enters their name ('firstname', 'lastname') and returns
a condensed list of their courses. When the fac mem submits the form,
the full list of their courses is updated with the correct syllabus
for each class. 
"""


app = Flask(__name__, template_folder = 'templates')
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True



ACCESS_TOKEN_FILE = "/var/www/html/FindACourse/access_token.txt"
ls = localdb_session()

def dropbox_accesstoken():
    """
    Read in the access token from access_token.txt. 
    Returns the stripped access token.
    """
    access_token =""
    with open(ACCESS_TOKEN_FILE,"r") as infile:
        for i in infile:
            access_token += i
    return access_token.strip()



def all_prof():
    """ 
    Constructs an unalphabetized list of all instructor1's.
    """
    courses = Course.query.all()

    profset=set()
    for i in courses:
        profset.add(i.instructor1.strip())
    if '' in profset:
        profset.remove('')
    return list(profset)



""" List of professors and dropbox access token are global. """
PROFLIST = all_prof()
DROPBOX_ACCESS_TOKEN = dropbox_accesstoken()



@app.route('/')        
def index():
    return render_template('Prof_Login.html', most_recent=["201601","201602"])


        
@app.route('/mycourses', methods=["GET", "POST"]) 
def get_courses():
    """
    The functions on the submit syllabi page. When 'submit' = 
    'Find My Courses', the function queries the database for the 
    courses taught by the professor.
    """
     
    if request.method == 'POST':
        
        username = request.form['username'].lower()
        
        # if user doesn't enter a username
        if username == "":
            flash('Please enter your username')
            return render_template('Prof_Login.html', username='', 
                                  most_recent=["201601","201602"])  
        
        # if user enters a username
        elif len(username) > 3:       
	    
	    prof = Faculty.query.filter(Faculty.email.ilike("%"+username+"%")).all()
	    if prof == []:
		flash('Username does not exist. Please check your spelling and try again')
	    #print "90 Prof:", prof
            semester = request.form['semester']
           
	    # there exists exactly one professor with that username
            if len(prof)==1: 
            	prof = prof[0]
                acad_period = request.form['semester'] 
                # find user's courses
                primary, secondary = current_course(prof,semester) 
		if primary == []:
		    if str(semester)[-1] == "1":
			flash('No courses found for '+prof.fullname+' for Fall '+semester[:4])
		    else:
			flash('No courses found for '+prof.fullname+' for Spring '+str(int(semester[:4])+1))
			#flash('No courses found for '+prof.fullname+' for semester '+semester)
		    return render_template('Prof_Login.html', username='', 
                                  most_recent=["201601","201602"])
		
                unique = determine_unique(primary)
		unique2 = determine_unique(secondary)
                return render_template('my_courses.html', courses=unique, 
                                       db_name=prof.fullname, semester=semester,
		                       inst2_courses=unique2)
            
	               
    return render_template('Prof_Login.html', username="", 
                          most_recent=["201601","201602"])     
     

def current_course(prof, semester):
   
    primary = prof.primary_classes(semester).all()
    secondary = prof.secondary_classes(semester).all()
    tertiary = prof.tertiary_classes(semester).all()      
    secondary = secondary + tertiary  

    	        
    
    return primary, secondary
    
    
def determine_unique(primary):
    unique = []
    for course in primary:
        if "REG" not in course.course_title:
            if not (course.CRN in build_CRN_string(unique)):
                unique.append(course)
    return unique
    
    
def build_CRN_string(unique):
    CRN_string =""
    for i in unique:
        CRN_string += i.CRN+" "
    return CRN_string



@app.route('/upload/', methods=["GET","POST"])    
def make_updates(): # 
    
    if request.method == "POST":
        
        client = dropbox.client.DropboxClient(DROPBOX_ACCESS_TOKEN)
        
        db_name = request.form["db_name"]
        semester = request.form["semester"]
    
	prof = Faculty.query.filter_by(fullname=db_name).first()
	
        primary, secondary = current_course(prof, semester)
        unique = determine_unique(primary)
        
        changed_syl_list = []
        changed_vis_list = []
        changed_prv_list = []  
        changed_lo_txt_list = []                    

        for i in range(len(unique)):
            dept = unique[i].subject
            crs_num = unique[i].course_num
            section = unique[i].seq_num
            semester = unique[i].acad_period 
            Lastprof = db_name.split(",")[0]
            
            course_name = (dept + ' ' + str(crs_num) + ': ' + 
                           unique[i].course_title + " Section " + 
                           unique[i].seq_num)
            
            syl = "syllabus_link"+str(i)
            vis = "visitable"+str(i)
            prv = "privacy"+str(i)
            lo_txt = "learning_outcomes_txt"+str(i)
            
	    
	    setting_id = unique[i].get_sett_id()
	    
	    
            new_syllabus = request.files[syl]                
            
            if new_syllabus.filename.replace(" ","") != '':
                      
                extension = (new_syllabus.filename.split(".")[-1]).strip()
                file_name = dept+"_"+crs_num+"_"+section+"_"+Lastprof+'.'+extension
                file_path = semester+"/"+dept+"/"+file_name

                
            new_visitable = request.form[vis]
            new_privacy = request.form[prv]
            new_lo_txt = request.form[lo_txt] 
	    
	    setting_object = ls.query(Settings).filter_by(id=setting_id).first()
	    
	    # for unique[i].course_title and unique[i].section and CRN match, update
            if len(new_syllabus.filename) > 0:
                changed_syl_list.append(course_name)
                

                response = client.put_file(file_path, new_syllabus.read(), 
                                           overwrite=True)
		
		setting_object.syllabus_link = response['path']
                
                
            if new_visitable != unique[i].visitable:
                changed_vis_list.append(course_name)
            if new_privacy != unique[i].privacy:
                changed_prv_list.append(course_name) 
            if new_lo_txt != unique[i].learning_outcomes:
                changed_lo_txt_list.append(course_name) 
                
	    setting_object.privacy = new_privacy
	    setting_object.visitable = new_visitable
	    setting_object.learning_outcome = new_lo_txt
	    setting_object.lo_status = "Not viewed"
	    
	    ls.commit()

        
        return render_template('thankyou.html', syl_list=changed_syl_list, 
                                   vis_list=changed_vis_list, 
                                   prv_list=changed_prv_list, 
                                   lo_txt_list=changed_lo_txt_list)

   
    return render_template('Prof_Login.html', most_recent=["201601", "201602"])



@app.route('/<path:file_path>')
def download(file_path):
    """ Downloads a file from Dropbox, given the file's path """
    file_name = (file_path.split("/")[-1])
    client = dropbox.client.DropboxClient(DROPBOX_ACCESS_TOKEN)
    f = client.get_file(file_path)
    return send_file(f,attachment_filename=file_name)

@app.teardown_appcontext
def shutdown_session(exception=None):
	db_session.remove()
	localdb_session.remove()

if __name__ == "__main__":    
    db.create_all()   
    app.secret_key = 'potato'
    app.run(debug=True)
