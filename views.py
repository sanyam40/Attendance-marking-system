from flask import flash,Blueprint,render_template,request,jsonify,redirect,url_for
import mysql.connector
import os
from werkzeug.utils import secure_filename 
import pandas as pd  
import csv   

views=Blueprint(__name__,"attendence")
global rollno
          
# DATABASE CONNECTION
global mydb
mydb=mysql.connector.connect(host="localhost",user="root",passwd="0721",database="project")

# HANDLER METHODS FOR HOME PAGE
@views.route('/home')
def home():
    read_attendence()
    return render_template('home.html')

@views.route('/')
def home2():
    read_attendence()
    return render_template('home.html')

# METHOD TO SHOW THE STUDENT LOGIN PAGE
@views.route('/student-login')
def student_login():
    return render_template('student-login.html')

# HANDLER METHOD FOR LOGIN REQUEST OF STUDENT
@views.route('/student-login-request',methods=['GET','POST'])
def student_login_request():

    if request.method == 'POST' and 'rollno' in request.form and 'password' in request.form:
        # Create variables for easy access
        rollno = request.form['rollno']
        password = request.form['password']

        print(rollno)
        print(password)
        
        cursor=mydb.cursor()
        
        # RETRIVING DATA FROM DATABASE ONLY IF THE USERNAME AND PASSWORD MATCHES
        stmt=('select * from student where rollno=%s AND password=%s',(rollno,password,))
        cursor.execute(*stmt)

        results=cursor.fetchone()
        print(results)

        # CHECKING IF THERE IS RECORD IN THE DATABASE OR NOT
        if results:
            #CHECKING THE USER TYPE AND REDIRECTING TO THE RESPECTIVE PAGE
            print("login successful for student")
            return render_template('student-attendence.html')
        else:
            # IF THE USERNAME AND PASSWORD DOES NOT MATCHES RETURN TO HOME PAGE
            print("incorrect")
            return render_template('index.html')
    
    else:
        return render_template('index.html')
    
# METHOD TO SHOW THE STUDENT REGISRATION PAGE
@views.route('/student-register')
def student_register():
    return render_template('register-form.html')

#HANDLER METHOD FOR STUDENT REGISTRATION REQUEST
@views.route('/student-register-request',methods=['GET','POST'])
def register_student():

    if request.method == 'POST':
        name = request.form['name'] 
        rollno = request.form['rollno'] 
        section=request.form['section']
        email = request.form['email']
        password = request.form['password']
        phnno = request.form['phnno']
        
        left = request.files['input-file-1']
        filename_left = secure_filename(left.filename)
        left.save(os.path.join('S:\ProjectD\static\images', rollno+"-left.jpg"))
        left = os.path.join('S:\ProjectD\static\images', rollno+"-left.jpg")

        front = request.files['input-file-2']
        filename_front = secure_filename(front.filename)
        front.save(os.path.join('S:\ProjectD\static\images', rollno+"-front.jpg"))
        front = os.path.join('S:\ProjectD\static\images', rollno+"-front.jpg")

        right = request.files['input-file-3'] 
        filename_right = secure_filename(right.filename)
        right.save(os.path.join('S:\ProjectD\static\images', rollno+"-right.jpg"))
        right = os.path.join('S:\ProjectD\static\images', rollno+"-right.jpg")
        
        print(name)
        cursor=mydb.cursor()
        stmt=('insert into student(name,rollno,section,email,password,phnno) values(%s,%s,%s,%s,%s,%s)',(name,rollno,section,email,password,phnno,))
        cursor.execute(*stmt)
        mydb.commit()

        return render_template('student-login.html')
    
    return render_template('student-login.html')

# METHOD TO SHOW THE TEACHER LOGIN PAGE
@views.route('/teacher-login')
def teacher_login():
    return render_template('teacher-login.html')

# HANDLER METHOD FOR LOGIN REQUEST OF TEACHER
@views.route('/teacher-login-request',methods=['GET','POST'])
def teacher_login_request():

    if request.method == 'POST' and 't_id' in request.form and 'password' in request.form:
        # Create variables for easy access
        t_id = request.form['t_id']
        password = request.form['password']

        print(t_id)
        print(password)
        
        cursor=mydb.cursor()
        
        # RETRIVING DATA FROM DATABASE ONLY IF THE USERNAME AND PASSWORD MATCHES
        stmt=('select * from teacher where t_id=%s AND password=%s',(t_id,password,))
        cursor.execute(*stmt)

        results=cursor.fetchone()
        print(results)

        # CHECKING IF THERE IS RECORD IN THE DATABASE OR NOT
        if results:
            #CHECKING THE USER TYPE AND REDIRECTING TO THE RESPECTIVE PAGE
            print("login successful for student")
            return render_template('teacher-attendence.html')
        else:
            # IF THE USERNAME AND PASSWORD DOES NOT MATCHES RETURN TO HOME PAGE
            print("incorrect")
            return render_template('home.html')
    
    else:
        return render_template('home.html')

# METHOD TO READ THE CSV FILE AND MARK THE ATTENDENCE
def read_attendence():
    # opening the CSV file
    with open('attendence.csv', mode ='r')as file:
        # reading the CSV file
        csvFile = csv.reader(file)
        cursor=mydb.cursor()
        # displaying the contents of the CSV file
        for lines in csvFile:
            command="insert into student_attendence(rollno) values(%s)"
            cursor.execute(command,tuple(lines))
            mydb.commit();
            print(lines)

# STUDENT ATTENDENCE PANEL 
@views.route('/student-panel',methods=['GET','POST'])
def student_panel_details():
   cursor=mydb.cursor()
   
   stmt=("select * from student where rollno=%s" ,(rollno,))
   result1=cursor.fetchone()
   print(result1)

   stmt2=("select count(absent) from student_attendence where rollno=%s",(rollno,))
   no_of_absent=cursor.fetchall()
   print(no_of_absent)

   stmt3=("select count(present) from student_attendence where rollno=%s",(rollno,))
   no_of_present=cursor.fetchall()
   print(no_of_present)

   return render_template("index.html", user_image = 'S:\ProjectD\static\images', rollno +"-front.jpg")
 
