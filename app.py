import traceback, warnings
warnings.filterwarnings("ignore")
import requests

from flask import Flask, render_template, redirect, json, request, session
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

captcha_secret_key = '6Lf0jTEUAAAAAJKBTt9hO48cOOBX0dI1jWa-5x0a'

@app.route('/home')
def main():
    return render_template('home.html')

@app.route('/')
@app.route('/login')
def showSignUp():
    return render_template('login.html', signinCheck="checked", signupCheck="")

@app.route('/signup')
def showSignIn():
    return render_template('login.html', signinCheck="", signupCheck="checked")    

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/rules')
def rules():
    if(session.get('user_id')):
        return render_template('rules.html')
    else:
        return redirect('/signup')

@app.route('/dashboard')
def dashboard():
    if(session.get('user_id')):
        return render_template('dashboard.html', name=session['name'].split(' ')[0])
    else:
        return redirect('/signup')

@app.route('/signup',methods=['POST'])
def signUp():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        _name = request.form['inputName'].decode()
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']
        _reg = request.form['inputRegno']
        _college = request.form['inputCollege']
        _phone = request.form['inputPhone']
        captcha_response = request.form['g-recaptcha-response']

        # validate the received values
        if _name and _email and _password and _reg and _college and _phone and captcha_response:
            # All Good, let's call MySQL
            #validate captcha from api
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data = {'secret':captcha_secret_key ,'response':captcha_response})
            is_success_captcha = r.json()['success']
            
            # if not is_success_captcha:
            #     return render_template("404.html",error = 'The captcha couldnt be verified')
            try:
                cursor.callproc('insert_player',(_name, _reg, _email, _phone, _password, _college))
                data = cursor.fetchall()
                if len(data) is 0:
                    conn.commit()
                    return render_template('login.html',signinCheck="checked", signupCheck="")

                else:
                    return render_template('404.html', error="not unique")            
            except Exception as e:
                return json.dumps({'errory':str(e)})
        else:
            return render_template('404.html',error = "Enter all the values. Please :(")

    except Exception as e:
        return json.dumps({'errory':str(e)})
    finally:
        cursor.close()
        conn.close()


@app.route('/login',methods=['POST'])
def validateLogin():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']
       # captcha_response = request.form['g-recaptcha-response']

        # validate the received values
        if _email and _password:

            
            # All Good, let's call MySQL
            #validate captcha from api
            #r = requests.post('https://www.google.com/recaptcha/api/siteverify', data = {'secret':captcha_secret_key ,'response':captcha_response})
            #is_success_captcha = r.json()['success']
            
            #if not is_success_captcha:
            #    return render_template("404.html",error = 'The captcha couldnt be verified')
            try:
                data = cursor.callproc('validate_login',(_email, _password))
                data = cursor.fetchall()
                if len(data) > 0:
                    conn.commit()
                    session['user_id'] = str(data[0][0])
                    session['name'] = str(data[0][1])
                    session['email'] = str(data[0][3])
                    session['curr_ques_id'] = str(data[0][8])
                    return redirect('/dashboard')
                else:
                    print 'not validated'
                    return render_template('404.html', msg="not validated")            
            except Exception as e:
                return json.dumps({'errory':str(e)})
        else:
            return render_template('404.html',error = "Enter all the values. Please :(")

    except Exception as e:
        return json.dumps({'errory':str(e)})
    finally:
        cursor.close()
        conn.close()

def updateScore():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM scores WHERE id = %s", (session['user_id']))
        data = cursor.fetchall()
        score = '0'
        money = '0'
        for player in data:
            score = int(session['point_wt']) + int(player[1])
            money = int(session['money_wt']) + int(player[2])
            session['correctly_answered'] = str(int(player[3])+1)
            print 'error here'
        cursor.execute("UPDATE scores SET points = %s, money = %s, correctly_answered = %s WHERE id = %s", (str(score), str(money), session['correctly_answered'], session['user_id']))
        conn.commit()
    except Exception as e:
        print str(e)
    return update()

def update():
    if(session.get('user_id')):
        go_to_dash  = True
        # if(session['curr_ques_id'] == session['curr_ques_id']):
        ro = session['curr_ques_id'].split('_')[0]
        ques = session['curr_ques_id'].split('_')[1]
        if(ro == '01' and ques == '25'):
            ro = '02'
            ques = 01
        elif(ro=='02' and ques == '20'):
            ro = '03'
            ques = 01
        elif(ro=='03' and ques == '20'):
            ro = '04'
            ques = 01
        elif(ro=='04' and ques == '20'):
            ro = '05'
            ques = 01
        elif(ro=='05' and ques == '20'):
            ro = '06'
            ques = 01
        else:
            go_to_dash  = False
        ques = int(ques) + 1
        ques = '%02d' % ques
        
        session['curr_ques_id'] = str(ro) + '_' + str(ques)
        conn = mysql.connect()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE players SET curr_ques_id= %s WHERE id = %s", (session['curr_ques_id'], session['user_id']))
            conn.commit()
        except:
            pass
        return go_to_dash

def getQuestion():
    if(session.get('user_id')):
        conn=mysql.connect()
        try:
            cursor=conn.cursor()
            # cursor.execute("SELECT * FROM questions WHERE ques_id = (SELECT ques_id FROM players WHERE id = %s)", (session['user_id']))
            cursor.execute("SELECT * FROM questions WHERE ques_id = %s", (session['curr_ques_id']))
        except Exception as e:
            print str(e)
        data = cursor.fetchall()
        for value in data:
            # session['curr_ques_id'] = value[0]
            que = value[1]
            q_img = value[2]
            if(q_img == ''):
                q_img = 'NULL'
            op1 = value[3]
            op2 = value[4]
            op3 = value[5]
            op4 = value[6]
            session['curr_ans'] = value[7]
            flag = value[8]
            session['point_wt'] = value[9]
            session['money_wt'] = value[10]
        params = {'que':que, 'op1':op1, 'op2':op2, 'op3':op3, 'op4':op4}
        return params

@app.route('/question')
def question():
    if(session.get('user_id')):
        params = getQuestion()
    #params = {'que':'Who is the President of Unites States of Americal', 'op1':'Rahul', 'op2':'Bhawesh', 'op3':'Ishaan', 'op4':'Dheemahi'}
        return render_template('myque.html', params = params)
    else:
        redirect ('/signup')

@app.route('/question', methods=['POST'])
def validate():
    if(session.get('user_id')):
        _answer = request.form['choice']
        if(_answer == session['curr_ans']):
            go_to_dash = updateScore()
            if(go_to_dash):
                return redirect ('/dashboard')
            else:
                return redirect ('/question')
        else:
            go_to_dash = update()
            if(go_to_dash):
                return redirect ('/dashboard')
            else:
                return redirect ('/question')
    else:
        return redirect('/signup')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(debug=True,port=5005,use_evalex=False)
    # app.run(debug=True,host='139.59.17.132',port=80,use_evalex=False)