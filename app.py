from flask import Flask, request,render_template,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from buoyant import Buoy
import sqlite3
import datetime
from pytz import timezone,utc
import pytz

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite://///Users/rafael.skovron/Downloads/PycharmProjects/surfdiary/session.db' #config file should be separate, tells sqlal how to connect
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)

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
    rank = db.Column(db.String(100))
    tide = db.Column(db.String(50))
    stime = db.Column(db.String(20))
    etime = db.Column(db.String(20))
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

    return render_template('index.html',result=result)

@app.route('/send',methods=['POST','GET'])
def send():
    if request.method =='POST':
        session_rank = request.form['overall']
        session_beach= request.form['spots']
        stime =request.form['stimepicker']
        etime = request.form['etimepicker']
        #get today's date in UTC....causes issues if function is run after 6pm PST (causes next day to be grabbed)
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




        session_update = Sessions(beach=session_beach,rank=session_rank,stime=stime,etime=utc_etime)


        db.session.add(session_update)
        db.session.commit()

        #return redirect(url_for('session_log')) #dont return view or template
        result = Sessions.query.all()
        result.reverse()

        getsession_weather()

        return render_template('session.html',result=result)

def getsession_weather():
    #pick the etime
    if request.method =='POST':
        etime = request.form['etimepicker']
        rank_sesh = request.form['overall']

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


        utc_etime_offset = utc_etime - datetime.timedelta(days=1)

        print('offset',utc_etime_offset)
        print('utcetime',utc_etime)

        session_beach= request.form['spots']

        conn = sqlite3.connect('/Users/rafael.skovron/Downloads/PycharmProjects/surfdiary/session.db')


        #create a query based on etime
        #pass the query to the weather table for the buoy
        #store results in session variables
        #write sessions variables to session db

        session_beach= request.form['spots']
        if session_beach not in ['4mile','PleasurePoint']:
            key = "oceanbeach"
        else:
            key ="santacruz"

        c = conn.cursor()



        print(utc_etime_offset.strftime("%Y-%m-%d %H:%M"),key)

        # need to fix this query

        c.execute("select * from weather where dtbuoy < (?) AND dtbuoy >= (?) AND key = (?)", (utc_etime.strftime("%Y-%m-%d %H:%M"),utc_etime_offset.strftime("%Y-%m-%d %H:%M"),key,))

        weather_update = c.fetchall()

        weather_update = weather_update[-1:]

        print('printing length of weather update', len(weather_update), type(weather_update))

        print (list(weather_update))


        import pdb; pdb.set_trace()


        c.execute('''INSERT INTO sessions(rank,swell_direction,swell_height,swell_period,wind,tide,beachregion) VALUES (?,?,?,?,?,?,?)''',[rank_sesh,weather_update[0][4],weather_update[0][3],weather_update[0][5],weather_update[0][0],weather_update[0][2],weather_update[0][6]])

        conn.commit()

        conn.close()











if __name__=="__main__":
    app.run(debug=True)
