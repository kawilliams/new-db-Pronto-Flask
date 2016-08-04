from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.ext.declarative import declarative_base


local_engine = create_engine('sqlite:////var/www/html/FindACourse/course_settings.db', echo=False)
localdb_session = scoped_session(sessionmaker(bind=local_engine))
Base = declarative_base()

class Settings(Base):
    __tablename__ = 'settings'
    query = localdb_session.query_property()
    
    id = Column(String,primary_key=True)
    visitable = Column(String, default="Can visit")
    privacy = Column (String, default= "All")
    learning_outcome = Column (String, 
                               default= "Cut learning outcomes from syllabus and paste them here")
    lo_status = Column(String, default="Not submitted")
    syllabus_link = Column(String, default = "")
    
    @property 
    def learning_outcomes(self):
        return self.learning_outcome
    
    def __init__(self,set_id):
        self.id = set_id
        
        
    def get_prof(self):
        return self.id.split(",")[2]
        
    
Base.metadata.create_all(local_engine)
