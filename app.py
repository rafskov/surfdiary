from flask import Flask, request,render_template

app = Flask(__name__)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send',methods=['POST','GET'])

def send():
    if request.method =='POST':
        session_rank = request.form['overall']
        session_beach= request.form['spots']
        session_swell= request.form['swell']
        session_wind= request.form['wind']
        session_tide=request.form['tide']
        return render_template('session.html',session_rank=session_rank,session_tide=session_tide,
        session_beach=session_beach,session_swell=session_swell,session_wind=session_wind)

    return render_template('session.html')



if __name__=="__main__":
    app.run(debug=True)
