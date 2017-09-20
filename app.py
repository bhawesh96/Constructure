import traceback, warnings
warnings.filterwarnings("ignore")
import requests

from flask import Flask, render_template, redirect, json, request
from flaskext.mysql import MySQL

mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'user2'
app.config['MYSQL_DATABASE_PASSWORD'] = 'passw'
app.config['MYSQL_DATABASE_DB'] = 'civicq'
app.config['MYSQL_DATABASE_HOST'] = '139.59.17.132'

mysql.init_app(app)

app.secret_key = '8bf9547569cd5a638931a8639cf9f86237931e92'

captcha_secret_key = '6LfLUDEUAAAAAF91iylHkkzPrztgbb_dKWExtw6n'

@app.route('/home')
@app.route('/')
def main():
    return render_template('home.html')

@app.route('/login')
def showSignUp():
    return render_template('login.html')

@app.route('/signin')
def showSignIn():
	return render_template('signin.html')

@app.route('/logout')
def logout():
    return redirect('/')


@app.route('/signup',methods=['POST'])
def signUp():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']
        _reg = request.form['inputRegno']
        _college = request.form['inputCollege']
        #captcha_response = request.form['g-recaptcha-response']

        # validate the received values
        #if _name and _email and _password and _reg and _college and captcha_response:
        if _name and _email and _password and _reg and _college:

            
            # All Good, let's call MySQL
            #validate captcha from api
            #r = requests.post('https://www.google.com/recaptcha/api/siteverify', data = {'secret':captcha_secret_key ,'response':captcha_response})
            #is_success_captcha = r.json()['success']
            
            #if not is_success_captcha:
            #    return render_template("404.html",error = 'The captcha couldnt be verified')

            cursor.callproc('insert_player',( _name, _reg, _email, _password, _college ))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                print 'all good'
                return render_template('signin.html')            
            else:
                return json.dumps({'errorx':str(data[0])})
        else:
            return render_template('404.html',error = "Enter all the values. Please :(")

    except Exception as e:
        return json.dumps({'errory':str(e)})
    finally:
        cursor.close()
        conn.close()



@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(debug=True,port=5005,use_evalex=False)
