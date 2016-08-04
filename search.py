from flask import (Flask, render_template, redirect, url_for, request, url_for,
                   send_from_directory, send_file)
from flask_sqlalchemy import SQLAlchemy
from model import *
from course_filters import *

import dropbox
from operator import attrgetter
import datetime
import logging
import csv

"""
This file is the search script for all of the courses and their 
syllabi. It is used to run the filter sidebar interface on the
search.html page. 
"""

app = Flask(__name__, template_folder='templates')

s = db_session() # connect to oracle db

ALL_DEPS_FULL = {"AFR":"Africana Studies",
                 "ANT":"Anthropology",
                 "ARB":"Arab Studies",
                 "ART":"Art",
                 "BIO":"Biology",
                 "CHE":"Chemistry",
                 "CHI":"Chinese Studies",
                 "CIS":"Center for Interdisciplinary Studies", 
                 "CLA":"Classical Civilization",
                 "COM":"Communication Studies",
                 "CSC":"Computer Science", 
                 "DAN":"Dance",
                 "DIG":"Digital Studies",
                 "EAS":"East Asian Studies",
                 "ECO":"Economics", 
                 "EDU":"Educational Studies", 
                 "ENG":"English", 
                 "ENV":"Environmental Studies",
                 "ETH":"Ethics", 
                 "FMS":"Film & Media Studies", 
                 "FRE":"French & Francophone Studies",
                 "GER":"German Studies", 
                 "GRE":"Greek", 
                 "GSS":"Gender & Sexuality Studies", 
                 "HIS":"History",
                 "HUM":"Humanities",
                 "LAS":"Latin American Studies", 
                 "LAT":"Latin",
                 "LIT":"??",
                 "MAT":"Mathematics",
                 "MHU":"Health and Human Values (Medical Humanities)",
                 "MIL":"Military Studies", 
                 "MUS":"Music", 
                 "PED":"Physical Education", 
                 "PHI":"Philosophy",
                 "PHY":"Physics", 
                 "POL":"Political Science", 
                 "PSY":"Psychology", 
                 "REL":"Religion", 
                 "RUS":"Russian Studies",
                 "SIL":"Self-Instructional Languages", 
                 "SOC":"Sociology", 
                 "SOU":"South Asian Studies",
                 "SPA":"Spanish", 
                 "THE":"Theatre", 
                 "WRI":"Writing",
                 "HHV":"Health and Human Values (Medical Humanities)"}




def determine_semester():
	"""
	Used to determine the current semester based on today's date.
	Returns a string representation of the academic period ("201601" for 
	fall of 2016, "201602" for spring of 2017).
	"""
	current = datetime.date.today()
	first_sem = current.replace(month=5, day=20), current.replace(month=12, day=20)
	if first_sem[0] <= current <= first_sem[1]:
		# first semester
		return str(current.year) + "01"
	else:
		# second semester
		previous_yr = current.replace(month=1, day=1) - datetime.timedelta(days=1)
		return str(previous_yr.year) + "02"

def format_year(period):
	year = period[:4]
	acad_period = period[-2:]
	
	if acad_period == "01":
		acad_period = "Fall"
	else:
		acad_period = "Spring"
		year = str(int(float(year)) + 1	)
		
	return acad_period +" "+year

def dep_list(current_semester):
	"""
	A function to get all the departments that have courses being
	taught during current_semester.
	"""
	courses = s.query(Course.major_code).filter_by(acad_period=current_semester).distinct(Course.major_code).order_by(Course.major_code).all()
	
	deps = []
	for i in courses:
		if str(i[0]) != "":
			deps.append(str(i[0]))

	return deps


def prof_list(current_semester):
	"""
	A function to get a list of all Professors that are teaching
	during current_semester.
	"""
	prof = (s.query(Course.instructor1,Course.instructor2,Course.instructor3).filter_by(acad_period=current_semester).
	         distinct(Course.instructor1,Course.instructor2,Course.instructor3).all())
	
	#prof2 = s.query(Course.instructor2).filter_by(acad_period=current_semester).distinct(Course.instructor2).order_by(Course.instructor2).all()
	#prof3 = s.query(Course.instructor3).filter_by(acad_period=current_semester).distinct(Course.instructor3).order_by(Course.instructor3).all()
	
	
	profs = set()
	for i in (prof):
		if "" != i[0] and i[0]:
			profs.add(str(i[0]))
		if "" != i[1] and i[1]:
			profs.add(str(i[1]))		

		if "" != i[2] and i[2]:
			profs.add(str(i[2]))				

	profs=sorted(list(profs))

	return profs

def range_list(current_semester):
	"""
	A function to get the smallest and largest sizes of courses offered
	during current_semester.
	"""
	size = s.query(Course.max_enroll).filter_by(acad_period=current_semester).distinct(Course.max_enroll).order_by(Course.max_enroll).first()
	size2 = s.query(Course.max_enroll).filter_by(acad_period=current_semester).distinct(Course.max_enroll).order_by(Course.max_enroll.desc()).first()
	smallest = size[0]
	largest = size2[0]

	range_size_small = range(smallest, largest+1)
	range_size_large = range(smallest+1, largest+1)
	
	return range_size_small, range_size_large


def sem_list():
	"""
	A function to get all the semesters we have course information for.
	"""
	courses = s.query(Course.acad_period).distinct(Course.acad_period).order_by(Course.acad_period.desc()).all()
	sems = []
	for i in courses:
		if i[0]:
			sems.append(str(i[0]))
		
	return sems

current_semester = determine_semester()
ALL_DEPS = dep_list(current_semester)
ALL_PROFESSORS = prof_list(current_semester)
RANGE_SIZES_SMALL, RANGE_SIZES_LARGE = range_list(current_semester)
ALL_SEMESTERS = sem_list()


def find_full_deps(dep_list):
	"""
	A function to match an abbreviation for a department to the full 
	department name.
	
	This will need to be changed when we use 'MAJOR_CODE' instead.
	"""
	full_dep_list = []
	for dep in dep_list:
		if dep in ALL_DEPS_FULL:
			full_dep_list.append(ALL_DEPS_FULL[dep])
		else:
			full_dep_list.append(dep)
	
	return full_dep_list


	
def read_notes_file():
	"""Reads in 'static/ScheduleNotes.csv', writes contents to nested list"""
	CODE = 0
	EXPLANATION = 1
	sched_notes = {}
    
	with open('/var/www/html/FindACourse/static/ScheduleNotes.csv', 'rU') as f:
		fReader = csv.reader(f, quotechar = '"', delimiter = ',')	    
		for line in fReader:
			sched_notes[line[CODE]] = line[EXPLANATION]   	
	
	return sched_notes

	
@app.route("/")
def home():
	"""
	Renders search.html on initial load. Calls find_full_deps to add the 
	tooltips for the department checkboxes in search.html.
	"""
	
	full_dep = find_full_deps(ALL_DEPS)	
	sched_notes = read_notes_file()
	return render_template("search.html",semesters=ALL_SEMESTERS, 
	                       profs=ALL_PROFESSORS, sizes_small=RANGE_SIZES_SMALL, 
	                       sizes_large=RANGE_SIZES_LARGE, deps=ALL_DEPS, 
	                       deps_full=full_dep, sched_notes=sched_notes,
	                       chosen_year=format_year(current_semester),
	                       selected_sem=current_semester)


@app.route("/semester",methods=["POST","GET"])
def process_semester():
	"""
	Determines what semester of information to load for the search 
	parameters. If no semester is chosen, determines the current
	semester and uses that as the chosen semester.
	"""	
	if request.method == "POST":
		semester = request.form["years"] 
		ALL_DEPS = dep_list(semester)
		ALL_PROFESSORS = prof_list(semester)
		full_dep = find_full_deps(ALL_DEPS)
		sched_notes = read_notes_file()
		results = Course.query.filter_by(acad_period=semester).all()
		query_len = len(results)
		msg = ""
		if query_len == 0:
			msg = "Sorry, no courses found. Try a different semester."
			
		year = (str(semester))[0:4]
		acad_period = (str(semester))[4:]
		if year != "Choo":
			if acad_period == "01":
				acad_period = "Fall"
			else:
				acad_period = "Spring"
				year = int(float(year)) + 1
	
			formatted_yr = acad_period + " " + str(year)
			
			return render_template("search.html", semesters=ALL_SEMESTERS, 
				               profs=ALL_PROFESSORS, deps=ALL_DEPS, deps_full=full_dep,
			                       sizes_small=RANGE_SIZES_SMALL,
			                       sizes_large=RANGE_SIZES_LARGE,
			                       sched_notes=sched_notes,
			                       selected_sem=semester, 
			                       chosen_year=formatted_yr)
		else:
			return redirect(url_for("home"))			

	else:
		return redirect(url_for("home"))



@app.route("/search",methods=["POST","GET"])
def process_form():
	"""
	Requests the form from the filter side bar in search.html and processes
	the parameters.	Returns the results of the query.
	"""
	if request.method == "POST":
		
		full_query=[]
		
		dep = request.form["dep"].split(" or ")
		if dep != [u'']:
			full_query += dep
		
		full_dep = find_full_deps(ALL_DEPS)
		sched_notes = read_notes_file()
		
		acd_prd = request.form["period"]
		 
		if acd_prd == "Choose one":
			acd_prd = determine_semester()
				
		prof = request.form["prof_form"].split(" or ")
		if prof != [u'']:
			full_query += prof

		day = "".join(request.form["days"].split(" or "))#single string

		if len(day.split(" or ")) == 2:
			full_query += day.split(" or ")
			day = ""
		else:
			full_query += day.split(" or ")

		time = request.form["times"].split(" or ")
		print time
		if time != [u'']:
			full_query += time

		dist = request.form["distri"].split(" or ")
		if dist != [u'']:
			full_query += set(dist)
		
		class_size = request.form['class_size'].split("-")
		if class_size != [u'']:
			full_query += class_size
		
		q1 = filter_acadPeriod(acd_prd)
		q2 = filter_major(dep)
		q3 = filter_prof(prof)
		q4 = filter_days(day)
		q5 = filter_time(time)
		q6 = filter_distr(dist)
		q7 = filter_class_size(class_size)

		year = (str(acd_prd))[0:4]
		semes = (str(acd_prd))[4:]			
		if semes == "01":
			semes = "Fall"
		else:
			semes = "Spring"
			year = int(float(year)) + 1

		formatted_yr = semes + " " + str(year)
		
			
		results = query_for([q1,q2,q3,q4,q5,q6,q7]).all()
		
		print (len(results))
		print results[0]
		
	
		msg = ""
		
		if (len(results) == 0):
			msg = "Sorry, no courses found. Try again."

		return render_template("search.html",search_results=results,
	        message = msg,profs=ALL_PROFESSORS, deps=ALL_DEPS, deps_full=full_dep,
	        semesters=ALL_SEMESTERS, sizes_small=RANGE_SIZES_SMALL,
			sizes_large=RANGE_SIZES_LARGE, sched_notes=sched_notes,
	        kept_values=full_query,
	        kept_values_len=len(full_query),
	        semester=acd_prd, selected_sem=semes,
	        chosen_year=formatted_yr)
		
	else:
		return redirect(url_for("home"))

@app.route("/searchany",methods=["POST","GET"])
def process_search():
	"""
	Processes the 'Search By Keyword' entry on search.html. 
	This does not involve any sidebar filter parameters.
	Returns the results of the query.
	"""
	if request.method == "POST":

		query_term = str(request.form["gen_search"])
		
		
		results = general_search(query_term).all() 
		
		
		msg = ""
		if (len(results) == 0):
			msg = "Sorry, no courses found. Try again."
		 
		if (len(query_term) == 6) and (query_term[-2:] == '01'):
			formatted_yr = "Fall "+query_term[:4]
		if (len(query_term) == 6) and (query_term[-2:] == '02'):
			formatted_yr = "Spring "+str(int(query_term[:4])+1)
		else:
			formatted_yr = 'All semesters'
		
		full_dep = find_full_deps(ALL_DEPS)
		sched_notes = read_notes_file()
		return render_template("search.html",search_results=results,
		                       message = msg,profs=ALL_PROFESSORS,
		                       deps=ALL_DEPS, deps_full=full_dep,
		                       semesters=ALL_SEMESTERS,
		                       sizes_small=RANGE_SIZES_SMALL,
		                       sizes_large=RANGE_SIZES_LARGE,
		                       sched_notes=sched_notes,
		                       #semester=determine_semester(),
		                       selected_sem="Choose one",
		                       chosen_year=formatted_yr)

	else:
		return redirect(url_for("home"))
	
	
ACCESS_TOKEN_FILE = "/var/www/html/FindACourse/access_token.txt"
DROPBOX_ACCESS_TOKEN = open(ACCESS_TOKEN_FILE,'r').read()


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
    
if __name__=="__main__":
	
	try:
		app.run(debug=True)
	except:
		db_session.remove()
		localdb_session.remove()		