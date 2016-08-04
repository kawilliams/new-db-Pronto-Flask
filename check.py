"""
A python module that will handle checking or changing the password.
Because this handles password checking, changing the password is as easy
as running python in the terminal with the previous password and 
the new one. An example is as follows:
      sudo python check.py Old_Password new_password
or you could run the change_password() function for a more interactive session.

This also means that adding extra security measures won't be hard. 
As long as the 'check_password' function returns a boolean, we can 
add as many things as posssible. 
"""
from sys import argv
import hashlib
PASSWORD_FILE = "/var/www/html/FindACourse/.password"

def change_password():
    prev_pass=raw_input("Please enter current password: ")
    if check_password(prev_pass):
        new_pass = raw_input("Enter the new password: ")
        with open(PASSWORD_FILE,"w") as f:
            hashed = hashlib.sha512(new_pass).digest()
            f.write(hashed)
            print "Password changed!"
            
        
def check_password(some_str):
    with open(PASSWORD_FILE,"r") as f:
                hashed_pas = f.read()
                
    return hashed_pas == hashlib.sha512(some_str).digest()

def main():
    
    old,new = argv[1:]
    if check_password(old):
        with open(PASSWORD_FILE,"w") as f:
                    hashed = hashlib.sha512(new).digest()
                    f.write(hashed)
                    print "Password changed!" 
    else:
        print "Wrong Password"
                    
if __name__ == "__main__":
    main()