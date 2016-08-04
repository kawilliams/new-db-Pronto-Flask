from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, relationship, scoped_session,mapper
from sqlalchemy.ext.declarative import declarative_base
from local_model import *


CONNECTION_STR="oracle+cx_oracle://zzprontoproject:takearun0nthewildside@xoapp1"

#connect to database
engine = create_engine(CONNECTION_STR,convert_unicode=True)
meta = MetaData(bind=engine)
db_session = scoped_session(sessionmaker(autocommit=False,
                                      autoflush=False,
                                      bind=engine))


#create the tables by reflection
faculty_view = Table('FACULTY',
                     meta,
                     # set primary_key
                     Column('instr_id',primary_key=True),
                     
                     oracle_resolve_synonyms=True,
                     autoload=True)

course_view = Table('COURSE_SCHEDULE_DC_EXT',
                    meta,
                    
                    # set how to uniquely identify courses
                    Column('academic_period',primary_key=True),
                    Column('major_code',primary_key=True),
                    Column('seq_number',primary_key=True),
                    Column('crn',primary_key=True),
                    Column('course_title',primary_key=True),
                    Column('subject',primary_key=True),
                    Column('class_time',primary_key=True),
                    Column('bldg_code',primary_key=True),
                    Column('room_code',primary_key=True),

                    
                    oracle_resolve_synonyms=True,
                    autoload=True)




# create object models for our course table
class Course(object):
    query = db_session.query_property()
    def __init__(self,acad_period,major_code,sub,crs_num,seq_num,crn,
                 crs_title,credit_hrs,crs_crd_range,crd_hr_ses,meet_days,
                 begin_time,end_time,class_time,bldg_code,room_code,instructor1,
                 instructor2,instructor3,instructor1_id,instructor2_id,
                 instructor3_id,course_notes,crs_attrib,max_enroll,cur_enroll,
                 seat_rem):
        
        self.acad_period = str(acad_period)
	self.major_code = str(major_code)
	self.subject = str(sub)
	self.course_num = str(crs_num)
	self.seq_num = str(seq_num)
	self.CRN = str(crn)
	self.course_title = str(crs_title)
	self.credit_hrs = str(credit_hrs)
	self.crs_cred_range = str(crs_crd_range)
	self.cred_hr_session = str(crd_hr_ses) 
	self.meet_days = str(meet_days)
	self.begin_time = str(begin_time)
	self.end_time = str(end_time )
	self.class_time = str(class_time )
	self.bldg_code = str(bldg_code )
	self.room_code = str(room_code)
	self.instructor1 = str(instructor1 )
	self.instructor2 = str(instructor2 )
	self.instructor3 = str(instructor3)
	self.instructor1_id = str(instructor1_id )
	self.instructor2_id = str(instructor2_id)
	self.instructor3_id = str(instructor3_id)
	self.course_notes = str(course_notes )
	self.course_attrib = str(crs_attrib )
	self.max_enroll = str(max_enroll )
	self.curr_enroll = str(cur_enroll )
	self.seats_remain = str(seat_rem)
        
    #generate setting id
    def get_room_code(self):
	room = self.room_code
	bldg = self.bldg_code
	if not room:
	    room = ""
	if not bldg:
	    bldg = ""
	return bldg + " " + room
    
    def get_sett_id(self):
        title = str(self.course_title).lower()
        if ("crn" in title):
            
            crn = title[-5:]

                   
        else:
            crn = str(self.CRN)
            
        
        return str(self.acad_period)+str(crn)   
    
    def get_email(self):
	"""
	returns the email address of the primary instructor
	"""
	
	return Faculty.query.get(self.instructor1_id).email
	
	    
    
    
    # define dynamic properties 
    # these properties are fetched from a different database
    
    @property
    def privacy(self):
        setting_id = self.get_sett_id()

	try:
	    setting = Settings.query.filter(Settings.id==setting_id).first()
	    return setting.privacy
	except:
	    os.system("python /var/www/html/FindACourse/updateSettings.py")
	    setting = Settings.query.filter(Settings.id==setting_id).first()
	    return setting.privacy
    

    
    @property
    def syllabus_link(self):
        setting_id = self.get_sett_id()
	
	try:
	    setting = Settings.query.filter(Settings.id==setting_id).first()
	    return setting.syllabus_link
	except:
	    os.system("python /var/www/html/FindACourse/updateSettings.py")
	    setting = Settings.query.filter(Settings.id==setting_id).first()
	    return setting.syllabus_link	    

    
    @property
    def visitable(self):
        setting_id = self.get_sett_id()

	try:
	    setting = Settings.query.filter(Settings.id==setting_id).first()
	    return setting.visitable
	except:
	    os.system("python /var/www/html/FindACourse/updateSettings.py")
	    setting = Settings.query.filter(Settings.id==setting_id).first()
	    return setting.visitable
	


    
    @property
    def lo_status(self):
        setting_id = self.get_sett_id()

	try:
	    setting = Settings.query.filter(Settings.id==setting_id).first()
	    return setting.lo_status
	except:
	    os.system("python /var/www/html/FindACourse/updateSettings.py")
	    setting = Settings.query.filter(Settings.id==setting_id).first()
	    return setting.lo_status
    

    
    @property
    def learning_outcomes(self):
        setting_id = self.get_sett_id()

	setting = Settings.query.filter(Settings.id==setting_id).first()
	"""
	(setting.learning_outcomes.replace("<","&lt;").
	        replace(">","&gt;").replace("&","&amp;").replace('"',"&quot;").
	        replace("'","&#039;").replace("\r"," ").
	        replace("\t","&nbsp;&nbsp;&nbsp;&nbsp;").strip())
	"""
	
	try:
	    setting = Settings.query.filter(Settings.id==setting_id).first()
	    return setting.learning_outcomes
	except:
	    os.system("python /var/www/html/FindACourse/updateSettings.py")
	    setting = Settings.query.filter(Settings.id==setting_id).first()
	    return setting.learning_outcomes	
	

        
        
 
    
    
    def __repr__(self):
        
        return ("<"+" ".join([self.acad_period,self.CRN,self.subject,
                self.course_num,self.major_code,self.seq_num,
                self.course_title,self.instructor1])+">")
    
# map our course table to the Course class
mapper(Course,course_view,
       properties={
                   # override attribute names
                   'acad_period':course_view.c.academic_period,
                   'CRN':course_view.c.crn,
                   'seats_remain':course_view.c.seats_remaining,
                   'seq_num':course_view.c.seq_number,
                   'course_attrib':course_view.c.course_attributes,
                   'course_num':course_view.c.course_number
                   })
    

# create object models for our faculty table
class Faculty(object):
    query = db_session.query_property()
    def __repr__(self):
        
        return "<"+self.fullname + " " + self.email+">"
    
    
    def primary_classes(self,acd):
        
        prof_id = self.id
        
        classes = (Course.query.filter(Course.instructor1_id==prof_id).
                   filter(Course.acad_period==acd))
        return classes
    
    def secondary_classes(self,acd):
        prof_id = self.id
        
        classes = (Course.query.filter(Course.instructor2_id==prof_id).
                   filter(Course.acad_period==acd))
        return classes
    
    def tertiary_classes(self,acd):
        
        prof_id = self.id
        
        classes = (Course.query.filter(Course.instructor3_id==prof_id).
                   filter(Course.acad_period==acd))
        return classes 
        
# map our faculty table to the Faculty class
mapper(Faculty,faculty_view,
       properties={
                   'id':faculty_view.c.instr_id,
                   'fullname':faculty_view.c.name,
                   'email':faculty_view.c.campus_email
                   })



def print_all(iterable_obj):
    count = 0
    for i in iterable_obj:
        print i
        count += 1
        
    print count
    
    


#testing 
#if __name__ == "__main__":
    #heyer = Faculty.query.filter(Faculty.fullname.ilike("%heyer%")).first()
    #print_all(heyer.primary_classes(201601))
