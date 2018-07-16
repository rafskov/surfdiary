from flask import Flask, request,render_template

app = Flask(__name__)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send',methods=['GET','POST'])

def send():
    if request.method =='POST':
        session_rank = request.form['overall']

        return render_template('session.html',session_rank=session_rank)

    return render_template('index.html')



if __name__=="__main__":
    app.run(debug=True)
