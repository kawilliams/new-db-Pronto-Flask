from model import *
from local_model import *
from sqlalchemy.exc import IntegrityError
import datetime

def add_aSetting(crs,local_sess):
    
    

    settting_id = crs.get_sett_id()
    
    # try adding a setting for a course 
    all_set = Settings.query.filter(Settings.id==settting_id).all()
    if len(all_set) == 0:
        local_sess.add(Settings(settting_id))
        local_sess.commit()
        
    
    
def add_settings(crs_ls):
    local_sess = localdb_session()
    for i in crs_ls:
        add_aSetting(i,local_sess)
    local_sess.close()
        
 
def current_sem():
    y=datetime.datetime.now().year
    m=datetime.datetime.now().month
    if m>=6 and m <=12:
        return str(y)+"01"
    else:
        return str(y-1)+"02"
    
if __name__ == '__main__':
    '''
    for a scheduled run
    '''
    
    crs_ls = Course.query.filter(Course.acad_period==current_sem()).all()
    add_settings(crs_ls)