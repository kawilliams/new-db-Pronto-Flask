from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from make_database import *
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


def general_search(query):
	query= query.split(" ")
	search_results= db.session.query(Course)
	for i in query:
		searchterm =  "%" + str(i).strip() + "%"
		search_results = search_results.filter(Course.all_data.
		                                       like(searchterm))

	return search_results

def filter_dep(searchterms):
	if (len(searchterms)==1 and str(searchterms[0])==""):
		return db.session.query(Course)
	return  db.session.query(Course).filter(Course.dep.in_(searchterms))

def filter_distr(searchterms):
	all_db = db.session.query(Course)
	if (len(searchterms)==1 and str(searchterms[0])==""):
		return all_db

	search_results = all_db.filter(Course.dist.like(searchterms[0]))

	for i in searchterms:
		searchterm =  "%" + str(i).strip() + "%"
		search_results = search_results.union(all_db.filter(Course.
		dist.like(searchterm)))


	return search_results

def filter_time(searchterms):
	searchterms = format_time(searchterms)

	if ((len(searchterms)==1 and str(searchterms[0])=="") or
	(len(searchterms)==0)):
		return db.session.query(Course)
	
	print "filtering"
	return  db.session.query(Course).filter(Course.class_time.
	in_(searchterms))

def filter_prof(searchterms):
	if (len(searchterms)==1 and str(searchterms[0])==""):
		return db.session.query(Course)
	return  db.session.query(Course).filter(Course.instructor.
	in_(searchterms))

def filter_days(searchterm):

	searchterm = searchterm.replace(" ","")
	searchterm =  "%" + searchterm.strip() + "%"
	return db.session.query(Course).filter(Course.class_days.like(searchterm))

def filter_acadPeriod(searchterm,query_ob=db.session.query(Course),show=True):

	return  db.session.query(Course).filter(Course.acad_period.
	like(searchterm))

def filter_class_size(searchterms):
	if (len(searchterms)==1 and str(searchterms[0])==""):
		return db.session.query(Course)
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
	print full_searchterms
	return  db.session.query(Course).filter(Course.max_enroll.
		in_(full_searchterms))	
	
def times():
	courses = db.session.query(Course)
	poss_times = []

	for i in courses:
		if str(i.class_time) != "":
			poss_times.append(str(i.class_time))
	poss_times=sorted(list(set(poss_times)))

	time_map={}
	for i in poss_times:
		curr_key = (i.split("-"))[0]
		time_map[curr_key]=[]

	for i in poss_times:
		curr_key = (i.split("-"))[0]
		time_map[curr_key].append(i)

	return time_map

def prof_list():
		courses = db.session.query(Course)
		profs = []
		for i in courses:
			profs.append(str(i.instructor))

		profs=sorted(list(set(profs)))

		return profs

ALL_PROFESSORS = prof_list()

def dep_list():
		courses = db.session.query(Course)
		deps = []
		for i in courses:
			if str(i.dep) != "":
				deps.append(str(i.dep))

		deps=sorted(list(set(deps)))

		return deps

ALL_DEPS = dep_list()

def format_time(time_query):
	time_map = times()
	
	new=[]
	for i in time_query:
		a_key= str(i).strip()
		if a_key in time_map:
			new += time_map[a_key]

	return new

def format_query(a_query):
	results = []
	for i in a_query:

		#record = [str(i.dep)+" "+str(i.course_num),i.title,
		          #i.instructor,i.class_time,i.class_days,
		          #i.dist,i.max_enroll,i.class_place,i.CRN,i.visitable
				  #,i.syllabus_link]
		record = [str(i.dep), str(i.course_num), i.class_section, i.title,
				i.instructor,i.class_time,i.class_days,
				i.dist,i.max_enroll,i.building,i.room,i.CRN,i.visitable
					,i.syllabus_link, "NOTES"]		
		results.append(record)
	return results

def print_query(a_query):
        for i in a_query:
                print i.all_data


def find_full_deps(dep_list):
	
	full_dep_list = []
	for dep in dep_list:
		full_dep_list.append(ALL_DEPS_FULL[dep])
	
	return full_dep_list
	
@app.route("/")
def home():
	full_dep = find_full_deps(ALL_DEPS)
	return render_template("search.html",profs=ALL_PROFESSORS, deps=ALL_DEPS, deps_full=full_dep)

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
		q2 = filter_dep(dep)
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

		final_query = (q1.intersect(q2).intersect(q3).intersect(q4).
		               intersect(q5).intersect(q6).intersect(q7))
		
		final_query_len = final_query.count()
		print final_query_len
		
		results=format_query(final_query)
		msg = ""
		if (final_query.count() == 0):
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
		if (raw_result.count() == 0):
			msg = "Sorry, no courses found. Try again."
		return render_template("search.html",search_results=results,
		message = msg,profs=ALL_PROFESSORS, deps=ALL_DEPS, deps_full=ALL_DEPS_FULL)

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
