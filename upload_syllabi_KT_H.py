import os
import logging
from flask import (Flask, request, flash, url_for, 
                   redirect, render_template,
                   send_from_directory, send_file)
from werkzeug import secure_filename
from flask_sqlalchemy import SQLAlchemy
from make_new_database import *
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



ACCESS_TOKEN_FILE = "access_token.txt"

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
        #profset.add(i.instructor2.strip())
        #profset.add(i.instructor3.strip())
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
        
        username = request.form['username']
        
        # if user doesn't enter a username
        if username == "":
            flash('Please enter your username')
            return render_template('Prof_Login.html', username='', 
                                  most_recent=["201601","201602"])  
        
        # if user enters a username
        elif len(username) > 4:       
            first = username[0].upper()
            last = username[2].upper() + username[3:].lower()
            db_name = last + " " + first
            semester = request.form['semester']
           
            if db_name in PROFLIST: 
                acad_period = request.form['semester'] 
                # find user's courses
                unique, two_found = current_course(db_name,semester)   
                unique = determine_unique(unique)
                return render_template('my_courses.html', courses=unique, 
                                       db_name=db_name, semester=semester)
            else:
                flash('Username not found. Please check the spelling and try again.')
                return render_template('Prof_Login.html', username=username, 
                      most_recent=["201601","201602"])  
            
    return render_template('Prof_Login.html', username="", 
                          most_recent=["201601","201602"])     
     

def current_course(db_name, semester):

        primary = Course.query.filter_by(instructor1=db_name).\
            filter_by(acad_period=semester).all()
        secondary = Course.query.filter_by(instructor2=db_name).\
            filter_by(acad_period=semester).all()  
        tertiary = Course.query.filter_by(instructor3=db_name).\
                    filter_by(acad_period=semester).all()        
        secondary = secondary + tertiary
        
        primary_titles = []
        secondary_titles = []      
        
        for c in primary:            
            primary_titles.append(c.course_title + ' ' + c.seq_num)
        
        
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
def make_updates(): # was upload_todropbox()
    
    if request.method == "POST":
        
        client = dropbox.client.DropboxClient(DROPBOX_ACCESS_TOKEN)
        
        db_name = request.form["db_name"]
        semester = request.form["semester"]
        
        print request.form           
        print request.files
        primary, secondary = current_course(db_name, semester)
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
            Lastprof = db_name.split(" ")[0]
            
            course_name = (dept + ' ' + str(crs_num) + ': ' + 
                           unique[i].course_title + " Section " + 
                           unique[i].seq_num)
            
            syl = "syllabus_link"+str(i)
            vis = "visitable"+str(i)
            prv = "privacy"+str(i)
            lo_txt = "learning_outcomes_txt"+str(i)
            #filename = ""
            
            new_syllabus = request.files[syl]                
            
            if new_syllabus.filename.replace(" ","") != '':
                #filename = secure_filename(new_syllabus.filename)         
                extension = (new_syllabus.filename.split(".")[-1]).strip()
                file_name = dept+"_"+crs_num+"_"+section+"_"+Lastprof+'.'+extension
                file_path = semester+"/"+dept+"/"+file_name
                #print file_path
                
                
            new_visitable = request.form[vis]
            new_privacy = request.form[prv]
            new_lo_txt = request.form[lo_txt]   
            #print "filename =",new_syllabus.filename
            if len(new_syllabus.filename) > 0:
                changed_syl_list.append(course_name)
                
                #new_syllabus.save(os.path.join(app.config['UPLOAD_FOLDER'], 
                #                               filename))
                
                #print "uploading to dropbox"
                response = client.put_file(file_path, new_syllabus.read(), 
                                           overwrite=True)
                
                setattr(unique[i], 'syllabus_link', response['path']) 
                
                #for course in unique_dict[unique[i].course_title + 
                                              #'|'+ unique[i].CRN]:
                    #setattr(course, 'syllabus_link', file_path)
            if new_visitable != unique[i].visitable:
                changed_vis_list.append(course_name)
            if new_privacy != unique[i].privacy:
                changed_prv_list.append(course_name) 
            if new_lo_txt != unique[i].learning_outcomes:
                changed_lo_txt_list.append(course_name) 
                
            setattr(unique[i], 'privacy', new_privacy)
            setattr(unique[i], 'visitable', new_visitable)
            setattr(unique[i], 'learning_outcomes', new_lo_txt) 
            
            #for course in unique_dict[unique[i].course_title + 
                                          #'|'+ unique[i].CRN]:
                #setattr(course, 'privacy', new_privacy)
                #setattr(course, 'visitable', new_visitable)
                #setattr(course, 'learning_outcomes', new_lo_txt)                
        #print "CRN COURSES"
        #update_CRN_courses(semester, db_name, unique)   
        db.session.commit()
        
        return render_template('thankyou.html', syl_list=changed_syl_list, 
                                   vis_list=changed_vis_list, 
                                   prv_list=changed_prv_list, 
                                   lo_txt_list=changed_lo_txt_list)

   
    return render_template('Prof_Login.html', most_recent=["201601", "201602"])


#def update_CRN_courses(acad_period, instructor1, unique):
    #"""
    #Update the course information for the cross-listed courses. 
    #"""
    #CRN_courses = ((Course.query.filter(Course.title.like("%CRN%"))
                    #.filter_by(acad_period=acad_period)
                    #.filter_by(instructor1=instructor1).all()))
    #for course in CRN_courses:
        ##print "The crn of the real course", course.title[course.title.find("CRN")+4:]
        ##print "The 'REGISTER FOR' course crn", course.CRN
        
        #for ea in unique:
            #if ea.CRN == course.title[course.title.find("CRN")+4:]:
                ##print "ea", ea.title, ea.syllabus_link
                ##print "course", course.title, course.syllabus_link
                #if course.privacy != ea.privacy:
                    #setattr(course, 'privacy', ea.privacy)
                #if course.visitable != ea.visitable:
                    #setattr(course, 'visitable', ea.visitable)      
                #if course.learning_outcomes != ea.learning_outcomes:
                    #setattr(course, 'learning_outcomes', ea.learning_outcomes)   
                #if course.syllabus_link != ea.syllabus_link:
                    #setattr(course, 'syllabus_link', ea.syllabus_link)          
    #return 



@app.route('/<path:file_path>')
def download(file_path):
    """ Downloads a file from Dropbox, given the file's path """
    file_name = (file_path.split("/")[-1])
    client = dropbox.client.DropboxClient(DROPBOX_ACCESS_TOKEN)
    f = client.get_file(file_path)
    return send_file(f,attachment_filename=file_name)



if __name__ == "__main__":    
    db.create_all()   
    app.secret_key = 'potato'
    app.run(debug=True)
