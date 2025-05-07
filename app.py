from flask import *
import os
import sqlite3
import random
import string
import smtplib
from email.message import EmailMessage
 
def send_email(from_email_addr, from_email_pass, to_email_addr, subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['From'] = from_email_addr
    msg['To'] = to_email_addr
    msg['Subject'] = subject

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email_addr, from_email_pass)
    server.send_message(msg)
    server.quit()

connection = sqlite3.connect('databse.db')
cursor = connection.cursor()

cursor.execute("create table if not exists students(name TEXT, email TEXT, studentid TEXT, phone TEXT, password TEXT)")

cursor.close()
connection.close()

app = Flask(__name__)
app.secret_key = 'abcdefghijklmnopqrstuvwxyz'

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/addstudent", methods = ['POST', 'GET'])
def addstudent():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        studentid = request.form['studentid']
        phone = request.form['phone']

        upper = random.choice(string.ascii_uppercase)
        lower = random.choice(string.ascii_lowercase)
        digit = random.choice(string.digits)
        special = random.choice(string.punctuation)
        remaining = random.choices(string.ascii_letters + string.digits + string.punctuation, k=4)
        password_list = [upper, lower, digit, special] + remaining
        random.shuffle(password_list)
        password = ''.join(password_list)

        data = [fname+' '+lname, email, studentid, phone, password]
        print(data)
        connection = sqlite3.connect('databse.db')
        cursor = connection.cursor()

        cursor.execute("insert into students values (?,?,?,?,?)", data)
        connection.commit()

        cursor.close()
        connection.close()
        send_email('placifya@gmail.com', 'eboc pggz yoca bfuy', email, 'Student Registration', f'Hi {fname} {lname}, Username: {email} and password: {password}. These are your login credantials for student portal')
        return render_template('addstudent.html', msg = 'Student added successfully')
    return render_template('addstudent.html')

@app.route("/studentlogin", methods = ['POST', 'GET'])
def studentlogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        data = [email, password]
        print(data)
        connection = sqlite3.connect('databse.db')
        cursor = connection.cursor()

        cursor.execute("select * from students where email = ? and password = ?", data)
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()

        if result:
            import random
            otp = str(random.randint(1111, 9999))
            session['otp'] = otp
            session['user'] = result
            print(otp)
            send_email('placifya@gmail.com', 'eboc pggz yoca bfuy', email, 'Student Registration', f'Hi, {otp} is your one time password for login into student portal')
            return render_template('verify.html')
        else:
            return render_template('student.html', msg = 'Entered wrong credentials')
    return render_template('student.html')

@app.route("/adminlogin", methods = ['POST', 'GET'])
def adminlogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email == 'admin@gmail.com' and password == 'admin123':
            return render_template('addstudent.html')
        else:
            return render_template('admin.html')
    return render_template('admin.html')

@app.route("/verify", methods = ['POST', 'GET'])
def verify():
    if request.method == 'POST':
        otp = str(request.form['otp'])

        if session['otp'] == otp:
            return render_template('studentpage.html', name = session['user'][0], email = session['user'][1])
        else:
            return render_template('student.html', msg="Entered wrong OTP")
    return render_template('student.html')

if __name__ == "__main__":
    app.run(debug=True)