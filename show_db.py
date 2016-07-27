#!/usr/bin/python
"""
Creates the course/syllabi database from a Banner dump csv.
"""

import os


import logging
from flask import *



from make_new_database import *

from operator import attrgetter
import datetime
import logging

#from model import Course as C

app = Flask(__name__, template_folder = 'templates')

app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


@app.route('/')
def index():
    '''
    Index for displaying our database. 
    '''
    courses = Course.query.all()
    #return "<h2>Search home to be put here. </h2>"
    return render_template('show_all.html', courses=courses)


    
@app.route('/search_home', methods=['GET', 'POST'])
def home():
	return "<h1>Search home to be put here. Hi Ashley! </h1>"

if __name__ == "__main__":
    app.run(debug=True)