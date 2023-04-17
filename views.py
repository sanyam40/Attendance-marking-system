from flask import Flask,flash,Blueprint,render_template,request,jsonify,redirect
import mysql.connector
import os
from werkzeug.utils import secure_filename 
import pandas as pd   
import re

views=Blueprint(__name__,"attendence")
global rollno
          
# DATABASE CONNECTION
global mydb
mydb=mysql.connector.connect(host="localhost",user="root",passwd="0721",database="project")

# HANDLER METHODS FOR HOME PAGE
@views.route('/home')
def home():
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
            stmt=("select * from student where rollno=%s" ,(rollno,))
            cursor.execute(*stmt)
            result1=cursor.fetchone()
            name=result1[0]
            section=result1[2]
            email=result1[3]

            stmt2=("select count(absent) from student_attendence where rollno=%s",(rollno,))
            cursor.execute(*stmt2)
            no_of_absent=cursor.fetchall()
            absentt=no_of_absent[0]
            absent=int(re.sub(r'\D', '', ''.join(map(str, absentt)) ))

            stmt3=("select count(present) from student_attendence where rollno=%s",(rollno,))
            cursor.execute(*stmt3)
            no_of_present=cursor.fetchone()
            present=no_of_present[0]
       
            #cursor.execute("select c_id from course")
            ###courses=cursor.fetchmany()
            #c_id=list(courses)
            #for i in c_id:
             #   print(i)
        
            filename=("\static\images\\"+rollno+"front.jpg")
            
            return render_template('student-panel.html',rollno=request.form['rollno'],name=name,section=section,email=email,absent=absent,present=present,filename=filename)
        else:
            # IF THE USERNAME AND PASSWORD DOES NOT MATCHES RETURN TO HOME PAGE
            print("incorrect")
            return render_template('home.html')
    
    else:
        return render_template('home.html')
    
#HANDLER METHOD FOR LOGOUT REQUEST    
@views.route("/logout")
def logout():
    return redirect("/home")

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
        left.save(os.path.join('S:\ProjectD\static\images', rollno+"left.jpg"))
        left = os.path.join('S:\ProjectD\static\images', rollno+"left.jpg")

        front = request.files['input-file-2']
        filename_front = secure_filename(front.filename)
        front.save(os.path.join('S:\ProjectD\static\images', rollno+"front.jpg"))
        front = os.path.join('S:\ProjectD\static\images', rollno+"front.jpg")

        right = request.files['input-file-3'] 
        filename_right = secure_filename(right.filename)
        right.save(os.path.join('S:\ProjectD\static\images', rollno+"right.jpg"))
        right = os.path.join('S:\ProjectD\static\images', rollno+"right.jpg")
        
        print(name)
        cursor=mydb.cursor()
        stmt=('insert into student(name,rollno,section,email,password,phnno) values(%s,%s,%s,%s,%s,%s)',(name,rollno,section,email,password,phnno,))
        cursor.execute(*stmt)
        mydb.commit()

        return redirect('student-panels')
    
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

        stmt2=("select name,sta.rollno,sta.section,present,absent,c_id,date,time from student as st JOIN student_attendence as sta on st.rollno=sta.rollno;")
        table=cursor.execute(stmt2)
        data=cursor.fetchall()
        print(data)

        # CHECKING IF THERE IS RECORD IN THE DATABASE OR NOT
        if results:
            #CHECKING THE USER TYPE AND REDIRECTING TO THE RESPECTIVE PAGE
            print("login successful for TEACHER")
            return render_template('teacher-panel.html',data=data)
        else:
            # IF THE USERNAME AND PASSWORD DOES NOT MATCHES RETURN TO HOME PAGE
            print("incorrect")
            return render_template('home.html')
    
    else:
        return render_template('home.html')

# METHOD TO READ THE CSV FILE AND MARK THE ATTENDENCE
def read_attendence():
    cursor=mydb.cursor()
    # opening the CSV file
    df=pd.read_csv("attendence.csv")

    rollnos=df['RollNo']
    section=df['Section']
    date=df['DATE']
    time=df['TIME']
    present=df['PRESENT']
    absent=df['ABSENT']
    course=df['Course']

    database=('TRUNCATE TABLE student_attendence')
    cursor.execute(database)
    mydb.commit()

    i=0

    while i<rollnos.size and i<section.size:
        roll=rollnos[i].astype(str)
        sec=section[i]
        datee=date[i]
        timee=time[i].astype(str)
        presentt=present[i].astype(str)
        absentt=absent[i].astype(str)
        c_id=course[i]

        stmt=('insert into student_attendence(absent,present,Date,rollno,time,section,c_id) values(%s,%s,%s,%s,%s,%s,%s)',(absentt,presentt,datee,roll,timee,sec,c_id))

        cursor.execute(*stmt)
        mydb.commit()
        i+=1