from model import *

def search_condition(term):
    '''
    Define what columns to search in our course table and the condition of
    how it will be searched
    
    In this case we have selected 12 columns to search by and it will be 
    joined by logical or 
    (logical or is defined under the 'or_' clause statement in SQLAlchemy)
    
    '''
    term = term.strip()
    
    conditions = or_(Course.acad_period.ilike("%"+term+"%"),
                     Course.instructor1.ilike("%"+term+"%"),
                     Course.instructor2.ilike("%"+term+"%"),
                     Course.major_code.ilike("%"+term+"%"),
                     Course.subject.ilike("%"+term+"%"),
                     Course.course_num.ilike("%"+term+"%"),
                     Course.CRN.ilike("%"+term+"%"),
                     Course.course_attrib.ilike("%"+term+"%"),
                     Course.course_title.ilike("%"+term+"%"),
                     Course.meet_days.ilike("%"+term+"%"),
                     Course.class_time.ilike("%"+term+"%"),
                     Course.bldg_code.ilike("%"+term+"%"))
       
    return conditions


#def hr12_mode(time_string):
    #"""
    #Given a string that represents time, changes it to 12-Hr mode if it is not.
    
    #Example inputs and outputs:
    
              #'0230'  => '0230'
	      #'1330'  => '0130'
	      #'hello' => 'hello'
	      #'230'   => '230'
    #"""

    #if len(time_string)==4 and time_string.isdigit():
	
	#hr= int(time_string[:2])
	#if hr>12:
	    #hr = hr-12
	#time = str(hr)+ time_string[2:]
	#if len(time)==3:
	    #time = "0"+time
	#return time
    
    #return time_string


# filter functions


def general_search(terms):
    """
    Given a space separated query terms, looks for a course that can fulfill
    all the query terms in the any of the columns specified by the 
    "search_condition" function
    """
    terms = terms.split(" ")
    final = []
    for i in terms:
        final.append(search_condition(i))
        
    return Course.query.filter(and_(*final)).order_by(Course.acad_period.desc(),
                                                      Course.subject,
                                                      Course.course_num,
                                                      Course.seq_num)



def filter_major(searchterms):
    
    """
    Given a list of majors, returns 'all the courses' that satisfy atleast 
    one of the the majors.
    
    For example: the input ["mat","psy"] will return the expression for getting
    courses that count for math major or psy major (or both)
    
    
    It doesn't return all the classes - just return a list of expressions that
    will be used to generate a query which will be used to actualy get the 
    data.
    This will avoid multiple requests from the database, and we will be able to 
    to combine our expressions to make a single database request. 
    """    
    conditions = []
    for i in searchterms:
        conditions.append(Course.major_code.ilike("%"+i+"%"))
        
    return or_(*conditions)

def filter_distr(searchterms):
    """
    Given a list of distribution req, returns expressions to get the
    courses that can fulfill any of the distribution requirements
    (Just like filter_major but for distribution)
    Input should be like ["HQRT", "SSRQ"]
    """    
    conditions = []
    for i in searchterms:
        conditions.append(Course.course_attrib.ilike("%"+i+"%"))
        
    # include recodes with None entry only if searchterms is [""]
    # This matters since about 1/4 of the 
    # total recordes actually have a 'None' dist. req. entry
    
    if len(searchterms) == 1 and len(searchterms[0])==0:
	conditions.append(Course.course_attrib==None)
    return or_(*conditions)    
    
    
    
def filter_time(searchterms):
    '''
    Given a list of appropriate begin times, return an expression for getting
    all the courses that START at any of the given times.
    
    appropriate time look like: 0815, 1340, 0930
                               
    
    '''
    conditions = []
    for i in searchterms:
        conditions.append(Course.begin_time.ilike("%"+i+"%"))
        
    # include recodes with None entry
    if len(searchterms) == 1 and len(searchterms[0])==0:
	conditions.append(Course.begin_time==None) 
    return or_(*conditions)    
    
def filter_acadPeriod(searchterm):
    
    """
    Returns the expression for getting all courses available at a given 
    acadamic period.
    The input should be a single string - like "201601" for fall, 2016 
    """
    return  Course.acad_period.like(searchterm)
    
    
def filter_prof(searchterms):
    """
    Returns the expression for getting all courses thought by any of the given 
    professors.
    The input should be a list of string of professors
    Example input: ["Smith J","Doe S"]
    """    
    conditions = []
    for i in searchterms:
        conditions.append(Course.instructor1.ilike("%"+i+"%"))
	conditions.append(Course.instructor2.ilike("%"+i+"%"))
	conditions.append(Course.instructor3.ilike("%"+i+"%"))
        
    return or_(*conditions) 

def filter_days(searchterm):
    """
    Given a single string returns an expression for getting 
    classes whose meeting days matches the searchterm.
    
    For example if the input is "MWF", the result is all the courses that
    are held during MWF, or just M or W or F
    """ 
    searchterms = list(searchterm)
    conditions = []
    for i in searchterms:
        conditions.append(Course.meet_days.ilike("%"+i+"%"))
    return or_(*conditions)      

def filter_class_size(search_list):
    min_size = int(search_list[0])
    max_size = int(search_list[1])
    return or_(between(Course.max_enroll,min_size,max_size),
               Course.max_enroll==None)

def query_for(expressions_list):
    return (Course.query.filter(and_(*expressions_list)).
            order_by(Course.acad_period.desc(), # show most recent first
                     Course.subject,
                     Course.course_num,
                     Course.seq_num))
    
    
# testing    
#if __name__ == "__main__":
    
    #exp1 = filter_acadPeriod("201601")
    #exp2 = filter_days("MWFT")
    #exp3 = filter_class_size([0, 30])
    #exp4 = filter_time('1505'.split())
    

    #r = query_for([exp1,exp2,exp3,exp4]).all()
    #print_all(r)