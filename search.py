from flask import (Flask, render_template, redirect, url_for, request, url_for,
                   send_from_directory, send_file)
from flask_sqlalchemy import SQLAlchemy
from make_new_database import *
import dropbox
from operator import attrgetter
import datetime
import logging


"""
This file is the search script for all of the courses and their 
syllabi. It is used to run the filter sidebar interface on the
search.html page. 
"""

app = Flask(__name__, template_folder='templates')
app.debug=True


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
                 "MHU":"Health and Human Values (Medial Humanities)",
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
                 "WRI":"Writing"}

def intersection_of(a_list):
	"""
	Accepts a list of lists and return a single list that is the 
	intersection of all the lists.
	If an element is in the returned list then it was in all the 
	individual lists.
	"""
	intesection_set=set(a_list[0])
	for i in a_list:
		intesection_set = (set(i) & intesection_set)
	
	return list(intesection_set)

def union_of(a_list):
	"""
	Accepts a list of lists and return a single list that is the 
	union of all the lists with no repeating elements. 
	"""
	union_set=set(a_list[0])
	for i in a_list:
		union_set = (set(i) |union_set)
		
	return list(union_set)


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


def start_times():
	"""
	A function that gets all the possible start times of our courses
	"""
	
	all_courses = Course.query.all()
	start_time= set()
	for i in all_courses:
		start_time.add(str(i.begin_time))
		
	return start_time

def start_time_map():
	"""
	A function that returns a map, where the keys are the 12hr versions of
	the same 24hr time. (data from the web form will be in 12hr format)
	"""
	start_time = start_times()
	time_map = {}
	for i in start_time:
		if i.replace(" ","") != "":
			time = int(i[:-2])
			
			# change times like 22** to 10**
			if time > 12:
				time = str(time-12)
			else:
				time = i[:-2]
				
			# change times like 1** to 01**
			if len(time) == 1:
				time = "0"+time
				
			time_map[time+i[-2:]] = i
		
	return time_map

def dep_list(current_semester):
	"""
	A function to get all the departments that have courses being
	taught during current_semester.
	"""
	courses = Course.query.filter_by(acad_period=current_semester).all()
	deps = set()
	for i in courses:
		if str(i.subject) != "":
			deps.add(str(i.subject))

	deps=sorted(list(deps))

	return deps


def prof_list(current_semester):
	"""
	A function to get a list of all Professors that are teaching
	during current_semester.
	"""
	courses = Course.query.filter_by(acad_period=current_semester).all()
	profs = set()
	for i in courses:
		profs.add(str(i.instructor1))
		profs.add(str(i.instructor2))
		profs.add(str(i.instructor3))
		
	if "" in profs:
		profs.remove("")
	profs=sorted(list(profs))

	return profs

def range_list(current_semester):
	"""
	A function to get the smallest and largest sizes of courses offered
	during current_semester.
	"""
	courses = Course.query.filter_by(acad_period=current_semester).all()
	smallest = 100
	largest = 0
	for i in courses:
		
		size = int(i.max_enroll)
		
		if size < smallest:
			smallest = size
		if size > largest:
			largest = size

	range_size_small = range(smallest, largest+1)
	range_size_large = range(smallest+1, largest+1)
	print smallest, largest
	return range_size_small, range_size_large


def sem_list():
	"""
	A function to get all the semesters we have course information for.
	"""
	courses = Course.query.all()
	sems = set()
	for i in courses:
		sems.add(str(i.acad_period))
		
	sems = sorted(list(sems))

	return sems

current_semester = determine_semester()
ALL_DEPS = dep_list(current_semester)
ALL_PROFESSORS = prof_list(current_semester)
RANGE_SIZES_SMALL, RANGE_SIZES_LARGE = range_list(current_semester)
ALL_SEMESTERS = sem_list()

	
def general_search(query):
	"""
	Returns all the courses that satisfy a given query.
	The query should be a string with keywords separated
	by space.The results will fulfill all specifications
	of space separated keywords - so this is like an 
	"and" search
	"""
	query= query.split(" ")
	all_courses= Course.query.all()
	searches = []
	
	for i in query:
		searchterm =  "%"+str(i).strip()+"%"
		searches.append(Course.query.
		                filter(Course.all_data.like(searchterm)).all())
		                
	return intersection_of(searches)


def filter_subject(searchterms, acd_prd):
	"""
	Given a list of subjects, returns all the courses that satisfy at least 
	one of the the subjects
	"""
	if (len(searchterms)==1 and str(searchterms[0])==""):
		return Course.query.all()
	
	searches = []
	for i in searchterms:
		searches.append(Course.query.filter_by(acad_period=acd_prd).
		                filter(Course.subject.like(i)).all())
		
	return union_of(searches)


def filter_major(searchterms, acd_prd):
	"""
	Given a list of majors, returns all the courses that count towards 
	atleast one of the listed majors
	For example if the input is ["MAT","PSY"] the results will be a list
	of courses that count for math major or psy major (or both).
	
	We will need to change this to INTERDISCIPLINARY_COURSE1 or whatnot...
	except this no longer exists. Whoops.
	"""	
	if (len(searchterms)==1 and str(searchterms[0])==""):
		return Course.query.all()	
	
	searches = []
	for i in searchterms:
		searches.append(Course.query.filter_by(acad_period=acd_prd).
		                filter(Course.major_code.like(i)).all())
		
	return union_of(searches)
	

def filter_distr(searchterms, acd_prd):
	"""
	Given a list of distribution req, returns all the courses that can 
	fulfill any of the distribution requirements
	(Just like filter_major but for distribution)
	Input should be like ["HQRT", "SSRQ"]
	"""
	all_db = Course.query.all()
	if (len(searchterms)==1 and str(searchterms[0])==""):
		return all_db

	searches = []

	for i in searchterms:
		st =  "%" + str(i).strip() + "%"
		searches.append(Course.query.filter_by(acad_period=acd_prd).
		                filter(Course.course_attrib.like(st)).all())

	return union_of(searches)


def filter_time(searchterms, acd_prd):
	"""
	Given a list of start times, returns a list of courses that start at 
	any of the given times. Changes non 12hr formats to 12hr format
	(1330 is changed to 130) via start_time_map().
	Calling this function with the input ["0930","1330"] will give us a
	list of all classes that start at 9:30 or 1:30
	"""
	time_map = start_time_map()
	searches=[]
	for i in searchterms:
		if i in time_map:
			s_time = time_map[i]
		else:
			s_time = i
		searches.append(Course.query.filter_by(acad_period=acd_prd).
		                filter(Course.begin_time.like(s_time)).all())
		
		if i == "":
			searches.append(Course.query.all())
		
	
	return union_of(searches)



def filter_acadPeriod(searchterm):
	"""
	Returns all courses available at a given acadamic period.
	The input should be a single string - like "201601" for fall, 2016 
	"""
	return  Course.query.filter(Course.acad_period.like(searchterm)).all()

                
def filter_prof(searchterms, acd_prd):
	"""
	Given a list of professors, returns all the courses taught by any of
	the given professors (they could be listed as a seconday instructor)
	"""
	if (len(searchterms)==1 and str(searchterms[0])==""):
		return Course.query.all()
	
	searches = []
	for i in searchterms:
		searches.append(Course.query.filter_by(acad_period=acd_prd).
		                filter(Course.instructor1.like(i)).all())
		searches.append(Course.query.filter_by(acad_period=acd_prd).
		                filter(Course.instructor2.like(i)).all())
		searches.append(Course.query.filter_by(acad_period=acd_prd).
		                filter(Course.instructor3.like(i)).all())		
	
	return union_of(searches)

def filter_days(searchterm, acd_prd):
	"""
	Given a single string,searchterm, (is either MWF or TR), returns 
	classes whoes meeting days matches the searchterm.
	
	For example if the input is "MWF", the result is all the courses that
	are held during MWF
	"""
	searchterm = "%".join(list(searchterm))
	searchterm =  "%" + searchterm.strip() + "%"
	return Course.query.filter(Course.meet_days.
	                                       like(searchterm)).filter_by(acad_period=acd_prd).all()



def filter_class_size(searchterms, acd_prd):
	"""
	Input - a list of strings, where each string is an integer 0 - ~ 56
	        (taken from the least max_enroll and greatest max_enroll of Courses)
		
	Returns - all courses whose max class size is in the given range
	"""
	if searchterms[0] == "":
		searchterms[0] = 0
	if searchterms[1] == "":
			searchterms[1] = 0	
	small = int(searchterms[0])
	large = int(searchterms[1])

	if small > large:
		return Course.query.all()
	if (small == 0) and (large == 1):
		return Course.query.all()
	
	greater = Course.query.filter(Course.max_enroll >= small).all()
	smaller = Course.query.filter(Course.max_enroll <= large).all() 
	
	return intersection_of([greater, smaller])

def find_full_deps(dep_list):
	"""
	A function to match an abbreviation for a department to the full 
	department name.
	
	This will need to be changed when we use 'MAJOR_CODE' instead.
	"""
	full_dep_list = []
	for dep in dep_list:
		full_dep_list.append(ALL_DEPS_FULL[dep])
	
	return full_dep_list


	
def read_notes_file():
	"""Reads in 'static/ScheduleNotes.csv', writes contents to nested list"""
	CODE = 0
	EXPLANATION = 1
	sched_notes = {}
	
	with open('static/ScheduleNotes.csv', 'rU') as f:
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
	                       deps_full=full_dep, sched_notes=sched_notes)


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
			                       selected_sem=semester)
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
		
		query_ob = db.session.query(Course)
		
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

		day = request.form["days"]

		if len(day.split(" or ")) == 2:
			full_query += day.split(" or ")
			day = ""
		else:
			full_query += day.split(" or ")

		time = request.form["times"].split(" or ")
	 
		if time != [u'']:
			full_query += time

		dist = request.form["distri"].split(" or ")
		if dist != [u'']:
			full_query += set(dist)
		
		class_size = request.form['class_size'].split("-")
		if class_size != [u'']:
			full_query += class_size
		
		q1 = filter_acadPeriod(acd_prd)
		q2 = filter_subject(dep, acd_prd)
		q3 = filter_prof(prof, acd_prd)
		q4 = filter_days(day, acd_prd)
		q5 = filter_time(time, acd_prd)
		q6 = filter_distr(dist, acd_prd)
		q7 = filter_class_size(class_size, acd_prd)


		year = (str(acd_prd))[0:4]
		semester = (str(acd_prd))[4:]			
		if semester == "01":
			semester = "Fall"
		else:
			semester = "Spring"
			year = int(float(year)) + 1

		formatted_yr = semester + " " + str(year)
		
			
		final_query = intersection_of([q1,q2,q3,q4,q5,q6,q7])		
		final_query_len = len(final_query)

		results=sorted(final_query, key=attrgetter('all_data'))
	
		msg = ""
		
		if (final_query_len == 0):
			msg = "Sorry, no courses found. Try again."

		return render_template("search.html",search_results=results,
	        message = msg,profs=ALL_PROFESSORS, deps=ALL_DEPS, deps_full=full_dep,
	        semesters=ALL_SEMESTERS, sizes_small=RANGE_SIZES_SMALL,
			sizes_large=RANGE_SIZES_LARGE, sched_notes=sched_notes,
	        kept_values=full_query,
	        kept_values_len=len(full_query),
	        semester=acd_prd, selected_sem=semester,
	        chosen_year=formatted_yr, result_count=final_query_len)
		
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
		
		results = general_search(query_term) 
		
		results = sorted(results, key=attrgetter('all_data'))
		
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
		final_query_len = len(results)
		sched_notes = read_notes_file()
		return render_template("search.html",search_results=results,
		                       message = msg,profs=ALL_PROFESSORS,
		                       semesters=ALL_SEMESTERS,
		                       deps=ALL_DEPS, deps_full=full_dep,
		                       chosen_year=formatted_yr,
		                       result_count=final_query_len,
		                       sched_notes=sched_notes)

	else:
		return redirect(url_for("home"))
	
	
ACCESS_TOKEN_FILE = "access_token.txt"
DROPBOX_ACCESS_TOKEN = open(ACCESS_TOKEN_FILE,'r').read()	


@app.route('/<path:file_path>')
def download(file_path):
	""" Downloads a file from Dropbox, given the file's path """
	file_name = (file_path.split("/")[-1])
	
	client = dropbox.client.DropboxClient(DROPBOX_ACCESS_TOKEN)
	f = client.get_file(file_path)
	return send_file(f,attachment_filename=file_name)

if __name__=="__main__":
	print "All ok"
	db.create_all()
	app.run()