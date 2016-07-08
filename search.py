from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from make_new_database import *
import dropbox

app = Flask(__name__)
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
                 "MHU":"??",
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
	accepts a list of lists and return a single list that is the 
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
	accepts a list of lists and return a single list that is the 
	union of all the lists - (no repeating elements). 
	"""
	union_set=set(a_list[0])
	for i in a_list:
		union_set = (set(i) |union_set)
		
	return list(union_set)

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
	the same time. (data from the web form will be in 12hr format)
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

def prof_list():
	"""
	A function to get a list of all Professors
	"""
	courses = Course.query.all()
	profs = set()
	for i in courses:
		profs.add(str(i.instructor1))
		profs.add(str(i.instructor2))
		profs.add(str(i.instructor3))
		
				
	profs=sorted(list(profs))

	return profs


def dep_list():
	"""
	A function to get all the departments
	"""
	courses = Course.query.all()
	deps = set()
	for i in courses:
		if str(i.subject) != "":
			deps.add(str(i.subject))

	deps=sorted(list(deps))

	return deps


ALL_DEPS = dep_list()
ALL_PROFESSORS = prof_list()


	
def general_search(query):
	query= query.split(" ")
	all_courses= Course.query.all()
	searches = []
	
	for i in query:
		searchterm =  "%"+str(i).strip()+"%"
		searches.append(Course.query.
		                filter(Course.all_data.like(searchterm)).all())
		                
	return intersection_of(searches)

def filter_subject(searchterms):
	if (len(searchterms)==1 and str(searchterms[0])==""):
		return Course.query.all()
	
	searches = []
	for i in searchterms:
		searches.append(Course.query.filter(Course.subject.
		                                    like(i)).all())
		
	return union_of(searches)


def filter_major(searchterms):
	if (len(searchterms)==1 and str(searchterms[0])==""):
		return Course.query.all()	
	
	searches = []
	for i in searchterms:
		searches.append(Course.query.filter(Course.major_code.
		                                    like(i)).all())
		
	return union_of(searches)
	

def filter_distr(searchterms):
	all_db = Course.query.all()
	if (len(searchterms)==1 and str(searchterms[0])==""):
		return all_db

	searches = []

	for i in searchterms:
		st =  "%" + str(i).strip() + "%"
		searches.append(Course.query.
		                filter(Course.course_attrib.like(st)).all())

	return union_of(searches)


def filter_time(searchterms):
	time_map = start_time_map()
	searches=[]
	for i in searchterms:
		if i in time_map:
			s_time = time_map[i]
		else:
			s_time = i
		searches.append(Course.query.
		                filter(Course.begin_time.like(s_time)).all())
		
		if i == "":
			searches.append(Course.query.all())
		
	
	return union_of(searches)



def filter_acadPeriod(searchterm):

	return  Course.query.filter(Course.acad_period.like(searchterm)).all()

                
def filter_prof(searchterms):
	if (len(searchterms)==1 and str(searchterms[0])==""):
		return Course.query.all()
	
	searches = []
	for i in searchterms:
		searches.append(Course.query.
		                filter(Course.instructor1.like(i)).all())
		searches.append(Course.query.
		                filter(Course.instructor2.like(i)).all())
		searches.append(Course.query.
		                filter(Course.instructor3.like(i)).all())		
	
	return union_of(searches)

def filter_days(searchterm):

	searchterm = "%".join(list(searchterm))
	searchterm =  "%" + searchterm.strip() + "%"
	return Course.query.filter(Course.meet_days.
	                                       like(searchterm)).all()



def filter_class_size(searchterms):
	if (len(searchterms)==1 and str(searchterms[0])==""):
		return Course.query.all()
	
	full_searchterms = []
	for i in searchterms:
		if (i == "0 - 6"):
			for n in range(6):
				full_searchterms.append(str(n))
		if (i == "6 - 12"):
			for n in range(6,13):
				full_searchterms.append(str(n))
		if (i == "12 - 20"):
			for n in range(12,20):
				full_searchterms.append(str(n))
		if (i == "20 +"):
			for n in range(20,40):
				full_searchterms.append(str(n))			
	
	return  Course.query.filter(Course.max_enroll.
		in_(full_searchterms)).all()	


def filter_classroom(searchterms):
	# need an agreement on how to get this data. might need to manuplate
	# the query term to enable searching 2 field of the database
	pass



def find_full_deps(dep_list):
	
	full_dep_list = []
	for dep in dep_list:
		full_dep_list.append(ALL_DEPS_FULL[dep])
	
	return full_dep_list

	
@app.route("/")
def home():
	full_dep = find_full_deps(ALL_DEPS)
	return render_template("search.html",profs=ALL_PROFESSORS, 
	                       deps=ALL_DEPS, deps_full=full_dep)

@app.route("/search",methods=["POST","GET"])
def process_form():

	if request.method == "POST":
		query_ob = db.session.query(Course)

		full_query=[]

		dep = request.form["dep"].split(" or ")
		if dep != [u'']:
			full_query += dep
		
		full_dep = find_full_deps(ALL_DEPS)
		
		acd_prd = request.form["period"]

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
			#for i in dist:
				#full_query.append(str(i))
		
		class_size = request.form['class_size'].split(" or ")
		if class_size != [u'']:
			full_query += class_size
		
		q1 = filter_acadPeriod(acd_prd)
		q2 = filter_subject(dep)
		q3 = filter_prof(prof)
		q4 = filter_days(day)
		q5 = filter_time(time)
		q6 = filter_distr(dist)
		q7 = filter_class_size(class_size)

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
		
		print len(final_query)
		
		results=final_query
		msg = ""
		
		if (final_query_len == 0):
			msg = "Sorry, no courses found. Try again."

		return render_template("search.html",search_results=results,
		message = msg,profs=ALL_PROFESSORS, deps=ALL_DEPS,
		deps_full=full_dep,
		kept_values=full_query,
		kept_values_len=len(full_query),
		semester=acd_prd,
		chosen_year=formatted_yr, result_count=final_query_len)

	else:
		return redirect(url_for("home"))

@app.route("/searchany",methods=["POST","GET"])

def process_search():
	if request.method == "POST":

		query_term = str(request.form["gen_search"])
		print query_term
		raw_result = general_search(query_term)
		results = format_query(raw_result)
		msg = ""
		if (len(raw_result) == 0):
			msg = "Sorry, no courses found. Try again."
		return render_template("search.html",search_results=results,
		                       message = msg,profs=ALL_PROFESSORS,
		                       deps=ALL_DEPS, deps_full=ALL_DEPS_FULL)

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