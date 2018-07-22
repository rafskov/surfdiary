from flask import Flask, request,render_template,redirect,url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:////Users/rws/Documents/Creative/surfdiary-project/session.db' #config file should be separate, tells sqlal how to connect
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)

#create a table in database so that python classes can be mapped to table
#to record each session

class Sessions(db.Model):
    #create columns
    id = db.Column(db.Integer,primary_key=True)
    beach = db.Column(db.String(100))
    swell = db.Column(db.String(3))
    wind = db.Column(db.String(3))
    rank = db.Column(db.String(100))
    tide = db.Column(db.String(50))
    #translates table


@app.route('/')
def index():

    result = Sessions.query.all() #return results in sessions table in a list of sqlacl objects

    return render_template('index.html',result=result)

@app.route('/send',methods=['POST','GET'])

def send():
    if request.method =='POST':
        session_rank = request.form['overall']
        session_beach= request.form['spots']
        session_swell= request.form['swell']
        session_wind= request.form['wind']
        session_tide=request.form['tide']

        session_update = Sessions(beach=session_beach,swell=session_swell,wind=session_wind,tide=session_tide,rank=session_rank)
        db.session.add(session_update)
        db.session.commit()

        #return redirect(url_for('session_log')) #dont return view or template
        result = Sessions.query.all() 
        result.reverse()
        return render_template('session.html',result=result)




if __name__=="__main__":
    app.run(debug=True)
