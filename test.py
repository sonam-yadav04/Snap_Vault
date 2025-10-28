from datetime import timezone

import MySQLdb
from flask import Flask,request, render_template,session,redirect,url_for,jsonify
from flask_mysqldb import MySQL
from functools import wraps
from datetime import  datetime , timezone, timedelta
import jwt
import re

app = Flask(__name__)

app.config['SECRET_KEY'] ='i am sonam'
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config['MYSQL_PASSWORD'] = "Sonam123"
app.config["MYSQL_DB"] = "userlogin"

mysql = MySQL(app)

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs ):
         token = request.args.get('token')
         if not token:
            return jsonify({'token':'token is missing'})
         else:
            return jsonify({'Alert':'invailid token'})



@app.route("/login",methods=['GET','POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form.get('username')
        password = request.form.get('password')
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("select * from account where username = %s and password = %s ",(username,password))
        account =  cur.fetchone()
        if account:
            session['loggedIn'] = True
            session['username'] = account['username']
            session['id']  = account['id']
            msg = " login successful"
            token = jwt.encode({
                'user': request.form['username'],
                'exp' :str(datetime.now(timezone.utc)+timedelta(seconds =160))
                      },
                    app.config(['SECRET_KEY'])

                     )
            return render_template('index.html',msg = msg)
        else:
            msg = 'username/password is not correct'

    return render_template("login.html", msg = msg)

@app.route("/logout")
def logout():
    session.pop('loggedIn', None)
    session.pop('username', None)
    session.pop('id', None)
    return redirect(url_for('login'))

@app.route("/register",methods = ['POST','GET'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'address' in request.form and 'pincode' in request.form and 'country' in request.form and 'phoneNo' in request.form:
        username = request.form.get('username')
        password = request.form.get('password')
        email =  request.form .get('email')
        address= request.form.get('address')
        pincode = request.form.get('pincode')
        country = request.form.get('country')
        phoneNo = request.form.get('phoneNo')

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM account WHERE username = %s', (username,))
        account = cur.fetchone()
        if account:
            msg = 'user already exists'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
             return "email is not correct!"
        elif not re.match(r'[A-Za-z0-9]+',username):
            return " incorrect username!"

        else:
            cur.execute(
                "INSERT INTO account VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)",
                (username, password, email, address, pincode, country, phoneNo)
            )
            mysql.connection.commit()
            msg = f"{username}! registered successfully!"
            return render_template("login.html")

    elif request.method == 'POST':
         msg = ' please fill the form'
    return render_template("register.html",msg = msg)

@app.route("/")
@app.route("/index")
def index():
    if 'loggedIn' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route("/display")
def display():
    if "loggedIn" in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("select * from account where id = %s",(session['id'],))
        account = cur.fetchone()
        return render_template("display.html", account = account)
    return redirect(url_for('login'))

@app.route("/update",methods=['GET','POST'])
def update():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'address' in request.form and 'pincode' in request.form and 'country' in request.form and 'phoneNo'in request.form:
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        country = request.form.get('country')
        phoneNo = request.form.get('phoneNo')

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("select * from account where username = %s and id = %s" ,(username,session['id'],))
        account = cur.fetchone()
        if account:
            msg = 'account already exist'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+',email):
            msg = "incorrect email!"
        elif not re.match(r'[A-Za-z0-9]',username):
            msg = " user name is not valid"
        else:
            cur.execute('UPDATE account SET username=%s, password=%s, email=%s, \
                         address=%s, pincode=%s, country=%s, phoneNo=%s WHERE id=%s',
                        (username, password, email, address, pincode, country, phoneNo, session['id']))
            mysql.connection.commit()
            msg = 'You have successfully updated !'
    elif request.method == 'POST':
        msg = "please fill this form"
    return render_template("update.html",msg =msg)



if __name__=='__main__':
    app.run(debug=True)

