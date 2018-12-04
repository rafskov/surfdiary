from flask import Flask, request,render_template,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from buoyant import Buoy
from flask_bootstrap import Bootstrap
import sqlite3
import datetime
from pytz import timezone,utc
import pytz
from flask_wtf import FlaskForm #convert forms to flask wtf
from wtforms import StringField,PasswordField,BooleanField #BooleanField is for the checkbox
from wtforms.validators import InputRequired,Email,Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required,logout_user,current_user
#need to put routes, database, and forms in sep. files

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:////home/leenux/Projects/surfdiary/session.db' #config file should be separate, tells sqlal how to connect
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY']="Thisissupposedtobesecret"
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' #set the login view


class User(UserMixin, db.Model): #create user table; Mixin adds stuff to User class. how flask login works with user class ClassName(object):

    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(15),unique=True)
    email = db.Column(db.String(50),unique=True)
    password= db.Column(db.String(80))

@login_manager.user_loader #connects flask login to data in db
def load_user(user_id):
    return User.query.get(int(user_id)) #query from User class using user_id



class LoginForm(FlaskForm): #create login form
    username = StringField('username',validators=[InputRequired(),Length(min=4,max=15)])
    password = PasswordField('password',validators=[InputRequired(),Length(min=8,max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email',validators=[InputRequired(),Email(message='Invalid email'),Length(max=50)])
    username = StringField('username',validators=[InputRequired(),Length(min=4,max=15)])
    password = PasswordField('password',validators=[InputRequired(),Length(min=8,max=80)])




utc = pytz.utc



pacific = timezone('US/Pacific')

#create a table in database so that python classes can be mapped to table
#to record each session

class Sessions(db.Model):
    #create columns
    id = db.Column(db.Integer,primary_key=True)
    beach = db.Column(db.String(100))
    swell_direction = db.Column(db.Integer())
    swell_height = db.Column(db.Integer())
    swell_period = db.Column(db.Integer())
    wind = db.Column(db.String(3))
    rank_sesh = db.Column(db.String(100))
    tide = db.Column(db.String(50))
    stime = db.Column(db.String(20))
    etime = db.Column(db.String(20))
    username = db.Column(db.String(20))
    #translates table

class Weather(db.Model):
    #create columns
    windspeed = db.Column(db.Integer,primary_key=True)
    windirection = db.Column(db.Integer())
    tide = db.Column(db.Integer())
    swell = db.Column(db.Integer())
    swelldirection = db.Column(db.Integer())
    swellperiod = db.Column(db.Integer())
    key = db.Column(db.String(100))
    dtwind= db.Column(db.String(50))
    dtbuoy= db.Column(db.String(20))


@app.route('/')
def index():

    result = Sessions.query.all() #return results in sessions table in a list of sqlacl objects

    return render_template('track2.html',result=result)

@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm() #instat. login so you can pass class to the form in the template

    if form.validate_on_submit(): #sees if form has been submitted
        #return '<h1>'+form.username.data + ' '+form.password.data+'</h1>'

        user = User.query.filter_by(username=form.username.data).first() #query user table for a user. you want to check is they are in the table first
        if user: #if they exist
            if check_password_hash(user.password,form.password.data): #compare hash in table to what was passed in from the form
                login_user(user,remember=form.remember.data)#login the user
                return redirect(url_for('dashboard'))
        return '<h1> invalid user name or password </h1>'

    return render_template('login.html', form=form)

@app.route('/signup',methods=['GET','POST'])
def signup():
    form = RegisterForm() #init. form

    if form.validate_on_submit(): #test the post
        hashed_password = generate_password_hash(form.password.data,method='sha256')
        new_user = User(username=form.username.data,email=form.username.data,password=hashed_password) #this instat. the user and passes in the form data
        db.session.add(new_user)
        db.session.commit()
        return "<h1> new user has been created </h1>"
        #return '<h1>'+form.username.data+ ' '+form.email.data+ ' ' +form.password.data+ '</h1>'

    return render_template('signup.html',form=form) #pass initialized form to template

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html',name=current_user.username)


@app.route('/logout')
@login_required #require loggged in status
def logout():
    logout_user() #log them out
    return redirect(url_for('index'))

@login_required
@app.route('/send',methods=['POST','GET'])
def send():
    if request.method =='POST':
        rank_sesh = request.form['output']
        session_beach= request.form['surfspots']
        stime =request.form['stimepicker']
        etime = request.form['etimepicker']
        #get today's date in UTC....causes issues if function is run after 6pm PST (causes next day to be grabbed)
        day = datetime.date.today()
        #split out the hour and minutes in the session end time
        #import pdb; pdb.set_trace()

        etime = etime.split(':')
        #destructure list
        a,b= etime
        #convert list items hour and minute to int
        hour,minute = map(int,(a,b))
        #construct enddate for session
        etime = datetime.datetime(day.year,day.month,day.day,hour,minute)
        #need to change code to reflect querying from cached db



        #change from naive to timeaware
        lcl_etime = pacific.localize(etime)
        #change to utc
        utc_etime = lcl_etime.astimezone(utc)


        getsession_weather()

        #import pdb; pdb.set_trace()

        #session_update = Sessions(beach=session_beach,rank_sesh=session_rank,stime=stime,etime=utc_etime,)


        #db.session.add(session_update)
        #db.session.commit()

        #return redirect(url_for('session_log')) #dont return view or template
        result = Sessions.query.all()
        result.reverse()

        print(result)

        return render_template('session.html',result=result[0])

def getsession_weather():
    #pick the etime
    if request.method =='POST':
        
        rank_sesh = request.form['output']
        session_beach= request.form['surfspots']
        stime =request.form['stimepicker']
        etime = request.form['etimepicker']



        day = datetime.date.today()
        #split out the hour and minutes in the session end time
        etime = etime.split(':')
        #destructure list
        a,b= etime
        #convert list items hour and minute to int
        hour,minute = map(int,(a,b))
        #construct enddate for session
        etime = datetime.datetime(day.year,day.month,day.day,hour,minute)
        #need to change code to reflect querying from cached db

        #change from naive to timeaware
        lcl_etime = pacific.localize(etime)
        #change to utc
        utc_etime = lcl_etime.astimezone(utc)


        utc_etime_offset = utc_etime - datetime.timedelta(hours=1)

        print('offset',utc_etime_offset)
        print('utcetime',utc_etime)

        session_beach= request.form['surfspots']

        conn = sqlite3.connect('/home/leenux/Projects/surfdiary/session.db')


        #create a query based on etime
        #pass the query to the weather table for the buoy
        #store results in session variables
        #write sessions variables to session db

        session_beach= request.form['surfspots']
        if session_beach not in ['4mile','PleasurePoint']:
            key = "oceanbeach"
        else:
            key ="santacruz"

        c = conn.cursor()



        print("key",utc_etime_offset.strftime("%Y-%m-%d %H:%M"),key)

        #import pdb; pdb.set_trace()

        # need to fix this query

        c.execute("select * from weather where dtbuoy < (?) AND dtbuoy >= (?) AND key = (?)", (utc_etime.strftime("%Y-%m-%d %H:%M"),utc_etime_offset.strftime("%Y-%m-%d %H:%M"),key,))

        weather_update = c.fetchall()

        #handle exception logic if there's no buoy data recorded

        conn.close()

        #import pdb; pdb.set_trace()

        conn = sqlite3.connect('/home/leenux/Projects/surfdiary/session.db')


        c = conn.cursor()            

        counter=0
        while len(weather_update) == 0 and counter<72:
            utc_etime_offset = utc_etime - datetime.timedelta(hours=counter) 
            c.execute("select * from weather where dtbuoy < (?) AND dtbuoy >= (?) AND key = (?)", (utc_etime.strftime("%Y-%m-%d %H:%M"),utc_etime_offset.strftime("%Y-%m-%d %H:%M"),key,))
            weather_update = c.fetchall()
            #import pdb; pdb.set_trace()
            print(counter,utc_etime_offset)
            counter+=1  


        if len(weather_update)!=0:
           c.execute("select * from weather")  
        #import pdb;pdb.set_trace()
        
        print("printing fetchal")

        weather_update = c.fetchall()

        print("weather update",weather_update)

        print(len(weather_update))

        print("printing weather UPDATE")
        print(weather_update)
        #import pdb; pdb.set_trace()
        weather_update = weather_update[-1]
        print("printing last ITEM IN WEATHER UPDATE")
        print(weather_update)

        print('printing length of weather update', len(weather_update), type(weather_update))

        print (list(weather_update))


        #import pdb; pdb.set_trace()
        print("we're debugging")
        print(rank_sesh)
        print(weather_update[4])
        print(weather_update[3])
        print(weather_update[5])
        print(weather_update[0])
        print(weather_update[2])
        print(weather_update[6])


        c.execute('''INSERT INTO Sessions(beach,rank_sesh,swell_direction,swell_height,swell_period,wind,tide,etime,username) VALUES (?,?,?,?,?,?,?,?,?)''',[session_beach,rank_sesh,weather_update[4],weather_update[3],weather_update[5],weather_update[0],weather_update[2],weather_update[8],current_user.username ])

        conn.commit()

        conn.close()


def get_MTD_surfstats():
        conn = sqlite3.connect('/home/leenux/Projects/surfdiary/session.db')
        c = conn.cursor()
        c.execute("SELECT COUNT(*) from Sessions where user= %s AND dtbuoy > %s",[str(current_user.username),needtoxiffffff])
        number_of_rows =c.fetchone() 








if __name__=="__main__":
    app.run(debug=True)
