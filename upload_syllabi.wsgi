import sys
import os
sys.path.insert(0, '/var/www/html/FindACourse')

os.environ["ORACLE_HOME"] = "/opt/oracle/product/12.1.0/client_1"
os.environ["LD_LIBRARY_PATH"]="/opt/oracle/product/12.1.0/client_1/lib:/opt/oracle/product/12.1.0/client_1/rdbms/public/:/opt/rh/python27/root/usr/lib64:/opt/rh/devtoolset-2/root/usr/lib64:/opt/rh/devtoolset-2/root/usr/lib"

from upload_syllabi import app as application