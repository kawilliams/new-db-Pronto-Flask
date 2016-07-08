#!/usr/bin/python
import os
import logging
from flask import (Flask, request, flash, url_for, 
                   redirect, render_template,
                   send_from_directory, send_file)
from werkzeug import secure_filename
from flask_sqlalchemy import SQLAlchemy
from make_database import Course
from make_database import db
import dropbox

""" 
For the faculty to upload their syllabi. Queries the database once the
faculty member enters their name ('firstname', 'lastname') and returns
a condensed list of their courses. When the fac mem submits the form,
the full list of their courses is updated with the correct syllabus
for each class. 
"""

UPLOAD_FOLDER = 'all_syllabi/'

app = Flask(__name__, template_folder = 'templates')
app.config['SECRET_KEY'] = 'secret'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

######## start Hermon upload.py #########
ACCESS_TOKEN_FILE = "access_token.txt"
app = Flask(__name__, template_folder = 'templates')

def dropbox_accesstoken():
    """
    Read in the access token from access_token.txt. 
    """
    access_token =""
    with open(ACCESS_TOKEN_FILE,"r") as infile:
        #counter = 0 Hermon?
        for i in infile:
            access_token += i

    return access_token.strip()

def all_prof():
    """ Constructs an unalphabetized list of all professors. """
    courses = Course.query.all()

    profset=set()
    for i in courses:
        profset.add(i.instructor.strip())
    return list(profset)

""" List of professors and dropbox access token are global. """
PROFLIST = all_prof()
DROPBOX_ACCESS_TOKEN = dropbox_accesstoken()

######## end Hermon #########

@app.route('/')        
def index():
    return render_template('Prof_Login.html', most_recent=["201601","201602"])


        
@app.route('/mycourses', methods=["GET", "POST"]) 
def get_courses():
    """
    The functions on the submit syllabi page. When 'submit' = 
    'Find My Courses', the function queries the database for the 
    """
    logging.warning("Got courses!")
    if request.method == 'POST':
        username = request.form['username']
        if username == "":
            flash('Please enter your username')
            return render_template('Prof_Login.html', username='', 
                                  most_recent=["201601","201602"])  
        
        elif len(username) > 4:            
            first = username[0].upper()
            last = username[2].upper() + username[3:].lower()
            db_name = last + " " + first
            semester = request.form['semester']
           
            if db_name in PROFLIST:                
                acad_period = request.form['semester'] 
                both_found, two_found =current_course(db_name, first,last, semester)                
                return render_template('my_courses.html', courses=both_found, 
                                       db_name=db_name, semester=semester)
            else:
                flash('Username not found. Please check the spelling and try again.')
                return render_template('Prof_Login.html', username=username, 
                      most_recent=["201601","201602"])  
            
    return render_template('Prof_Login.html', username="", 
                          most_recent=["201601","201602"])     
     

def current_course(db_name, first, last, semester):

        found = (Course.query.filter(Course.instructor.like(db_name))
                 .filter_by(acad_period=semester).all())          
        found_a = (Course.query.filter(Course.instructor.like(db_name+", %"))
                   .filter_by(acad_period=semester).all())         
        #BUG: trying to retrieve courses where professor is listed second
        #found_b = Course.query.filter(Course.instructor.like("%"+last_name))
        #.filter_by(acad_period=semester).all() 
        
        found_titles = []
        found_a_titles = []
        #found_b_titles = []  
        count = 0
        prof_courses = []
        prof_titles = []
        sections = {}        
        
        for c in found:
            
            found_titles.append(c.title + ' ' + c.class_section)
            
            if c.title not in sections: 
                prof_courses.append(c)
                if c.title in sections:
                    sections[c.title].append(c.class_section)
                else:
                    sections[c.title] = []
                    sections[c.title].append(c.class_section)
                prof_titles.append(c.class_section)
                prof_titles.append(c.instructor)
                count += 1  
            if c.title in sections: 
                if c.title in sections:
                    sections[c.title].append(c.class_section)
                else:
                    sections[c.title] = []
                    sections[c.title].append(c.class_section)   
                    
        for a in found_a:
            found_a_titles.append(a.title + ' ' + a.class_section) 
            if a.title in sections:
                sections[a.title].append(a.class_section)
            else:
                sections[a.title] = []
                sections[a.title].append(a.class_section)            

        two_found = found       
        for a in found_a:
            two_found.append(a)
        
        both_found = []  
        titles = []
        for i in range(len(two_found)):
            has_multiples = False
            for j in range(i+1, len(two_found)):
                if (two_found[i].title == two_found[j].title and 
                    two_found[i].CRN == two_found[j].CRN):
                    has_multiples = True
                    if "CRN" not in two_found[j].title:
                        both_found.append(two_found[j])
                        titles.append(two_found[j].title)
                    
            if not has_multiples and two_found[i].title not in titles:

                if "CRN" not in two_found[i].title:                    
                    both_found.append(two_found[i])
                    
        both_found = sorted(both_found, key=lambda course: course.course_num)
        return both_found, two_found
    
    
def build_course_dictionary(db_name, first, last, semester):
    
    """ Makes a dictionary with 'title|CRN' as the key (generated from 
            both_found) and a list of the duplicate courses as the value 
            (generated from two_found). To view, the next few lines are for 
            printing. """
    both_found, two_found = current_course(db_name, first, last, semester)
    both_found_dict = {}
    for boo in both_found:
        both_found_dict[boo.title+"|"+boo.CRN] = []
        for tic in two_found:
            if tic.CRN == boo.CRN:
                both_found_dict[boo.title+"|"+boo.CRN].append(tic)
    #for ea in both_found_dict:
        #hug = []
        #for np in both_found_dict[ea]:
            #hug.append(np.title + ' '+np.class_section)
        #print ea, hug     
    return both_found_dict, both_found, two_found


@app.route('/upload/', methods=["GET","POST"])    
def make_updates(): # was upload_todropbox()
    #both_found, two_found = current_course(db_name, first, last, semester)
    if request.method == "POST":
        #print "SumbMitiNG!"   
        #print DROPBOX_ACCESS_TOKEN
        client = dropbox.client.DropboxClient(DROPBOX_ACCESS_TOKEN)
        
        db_name = request.form["db_name"]
        semester = request.form["semester"]
        #print "YO katy"
        #print request.form
        first = db_name[0].upper()
        last = db_name[2].upper()+db_name[3:]        
        both_found_dict, both_found, two_found = build_course_dictionary(
            db_name, first, last, semester)

        changed_syl_list = []
        changed_vis_list = []
        changed_prv_list = []  
        changed_lo_txt_list = []                    

        for i in range(len(both_found)):
            dept = both_found[i].dep
            crs_num = both_found[i].course_num
            section = both_found[i].class_section
            semester = both_found[i].acad_period 
            Lastprof = db_name.split(" ")[0]
            
            course_name = (dept + ' ' + str(crs_num) + ': ' + 
                           both_found[i].title + " Section " + 
                           both_found[i].class_section)
            
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
                
                setattr(both_found[i], 'syllabus_link', response['path']) 
                
                for course in both_found_dict[both_found[i].title + 
                                              '|'+ both_found[i].CRN]:
                    setattr(course, 'syllabus_link', file_path)
            if new_visitable != both_found[i].visitable:
                changed_vis_list.append(course_name)
            if new_privacy != both_found[i].privacy:
                changed_prv_list.append(course_name) 
            if new_lo_txt != both_found[i].learning_outcomes:
                changed_lo_txt_list.append(course_name) 
                
            setattr(both_found[i], 'privacy', new_privacy)
            setattr(both_found[i], 'visitable', new_visitable)
            setattr(both_found[i], 'learning_outcomes', new_lo_txt) 
            
            for course in both_found_dict[both_found[i].title + 
                                          '|'+ both_found[i].CRN]:
                setattr(course, 'privacy', new_privacy)
                setattr(course, 'visitable', new_visitable)
                setattr(course, 'learning_outcomes', new_lo_txt)                
        #print "CRN COURSES"
        update_CRN_courses(semester, db_name, both_found)   
        db.session.commit()
        
        return render_template('thankyou.html', syl_list=changed_syl_list, 
                                   vis_list=changed_vis_list, 
                                   prv_list=changed_prv_list, 
                                   lo_txt_list=changed_lo_txt_list)

   
    return render_template('Prof_Login.html', most_recent=["201601", "201602"])


def update_CRN_courses(acad_period, instructor, both_found):
    """
    Update the course information for the cross-listed courses. 
    """
    CRN_courses = ((Course.query.filter(Course.title.like("%CRN%"))
                    .filter_by(acad_period=acad_period)
                    .filter_by(instructor=instructor).all()))
    for course in CRN_courses:
        #print "The crn of the real course", course.title[course.title.find("CRN")+4:]
        #print "The 'REGISTER FOR' course crn", course.CRN
        
        for ea in both_found:
            if ea.CRN == course.title[course.title.find("CRN")+4:]:
                #print "ea", ea.title, ea.syllabus_link
                #print "course", course.title, course.syllabus_link
                if course.privacy != ea.privacy:
                    setattr(course, 'privacy', ea.privacy)
                if course.visitable != ea.visitable:
                    setattr(course, 'visitable', ea.visitable)      
                if course.learning_outcomes != ea.learning_outcomes:
                    setattr(course, 'learning_outcomes', ea.learning_outcomes)   
                if course.syllabus_link != ea.syllabus_link:
                    setattr(course, 'syllabus_link', ea.syllabus_link)          
    return 


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
