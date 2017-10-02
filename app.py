import traceback, warnings
warnings.filterwarnings("ignore")
import requests
import time

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

@app.route('/')
@app.route('/home')
def main():
    return render_template('home.html')

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
        updateDashboardStyle()

        return render_template('dashboard.html', name=session['name'].split(' ')[0],round = session['round_style'])
    else:
        return redirect('/signup')

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
        return json.dumps({'errorz':str(e)})
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
                    session['r1_res'] = str(data[0][9])
                    session['r2_res'] = str(data[0][10])
                    session['r31_res'] = str(data[0][11])
                    session['r32_res'] = str(data[0][12])

                    session['r4_res'] = str(data[0][13])
                    session['r5_res'] = str(data[0][14])
                    session['r61_res'] = str(data[0][15])
                    session['r62_res'] = str(data[0][16])
                    session['r63_res'] = str(data[0][17])
                    session['r64_res'] = str(data[0][18])
                    session['r65_res'] = str(data[0][19])

                    session['curr_trail'] = int(data[0][20])
                    session['curr_round'] = int(data[0][21])
                    session['round_style'] = ""

                    # ro = session['curr_ques_id'].split('_')[0]
                    # # session['curr_round'] = float(ro) -1
                    # if(session['curr_round'] == 1):
                    #     if(session['r1_res'] != '0'):
                    #         session['curr_round'] =0
                    # elif(session['curr_round'] == 2):
                    #     if(session['r2_res'] != '0'):
                    #         session['curr_round'] =0
                    # elif(session['curr_round'] == 31):
                    #     if(session['r31_res'] != '0'):
                    #         session['curr_round'] =0
                    # elif(session['curr_round'] == 32):
                    #     if(session['r32_res'] != '0'):
                    #         session['curr_round'] =0
                    # elif(session['curr_round'] == 4):
                    #     if(session['r4_res'] != '0'):
                    #         session['curr_round'] =0
                    # elif(session['curr_round'] == 5):
                    #     if(session['r5_res'] != '0'):
                    #         session['curr_round'] =0


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

def updateDashboardStyle():
    if(session['r5_res']!='0'):
        session['round_style'] = "-round6"
    elif(session['r4_res']!='0'):
        session['round_style'] = "-round5"             
    elif(session['r32_res']!='0'):
        session['round_style'] = "-round4"
    elif(session['r2_res']!='0'):
        session['round_style'] = "-round3"
    elif(session['r1_res']!='0'):
        session['round_style'] = "-round2"
                    

def updateScore():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM scores WHERE id = %s", (session['user_id']))
        data = cursor.fetchall()
        print data,session['point_wt'],session['money_wt']
        score = '0'
        money = '0'
        for player in data:
            print player[0],player[1],player[2],player[3]
            score = float(session['point_wt']) + float(player[1])
            money = float(session['money_wt']) + float(player[2])
            session['correctly_answered'] = str(float(player[3])+1)
            print 'error here'
        cursor.execute("UPDATE scores SET points = %s, money = %s, correctly_answered = %s WHERE id = %s", (str(score), str(money), session['correctly_answered'], session['user_id']))
        conn.commit()
    except Exception as e:
        print str(e)
    return update()

def update():
    if(session.get('user_id')):
        go_to_new_round  = True
        # if(session['curr_ques_id'] == session['curr_ques_id']):
        ro = session['curr_ques_id'].split('_')[0]
        ques = session['curr_ques_id'].split('_')[1]
        if(ro == '01' and ques == '25'):
            ro = '02'
            ques = 00
            session["curr_round"] = 1
        elif(ro=='02' and ques == '20'):
            ro = '02'
            ques = 00
            session["curr_round"] = 20
        elif(ro=='03' and ques == '20'):
            ro = '03'
            ques = 00
            session["curr_round"] = 30
        elif(ro=='04' and ques == '20'):
            ro = '04'
            ques = 00
            session["curr_round"] = 40

        elif(ro=='05' and ques == '20'):
            ro = '05'
            ques = 00
            session["curr_round"] = 50
        elif(ro=='06' and ques == '25'):
            ro = '06'
            ques = 00
            session['curr_round'] = 60
        else:
            go_to_new_round  = False
        ques = float(ques) + 1
        ques = '%02d' % ques
        
        session['curr_ques_id'] = str(ro) + '_' + str(ques)
        conn = mysql.connect()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE players SET curr_ques_id= %s,curr_round = %s WHERE id = %s", (session['curr_ques_id'],str(session['curr_round']), session['user_id']))
            conn.commit()
        except Exception as e:
            print str(e)
        return go_to_new_round

    

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
            image = False
            if(flag == '0'):
                image = False
            else:
                image=True
            session['point_wt'] = value[9]
            session['money_wt'] = value[10]
        params = {'que':que, 'op1':op1, 'op2':op2, 'op3':op3, 'op4':op4,'flag':image,'id':session['curr_ques_id']}
        conn.close()
        return params

def getRapidFireParams():
    if(session.get('user_id')):
        conn = mysql.connect()
    try:
            cursor=conn.cursor()
            # cursor.execute("SELECT * FROM questions WHERE ques_id = (SELECT ques_id FROM players WHERE id = %s)", (session['user_id']))
            cursor.execute("SELECT * FROM rapidFire WHERE ques_id = %s", (session['curr_ques_id']))
    except Exception as e:
        print str(e)
    data = cursor.fetchall()
    for value in data:
        que = value[1]
        q_img = value[2]
        session['curr_ans'] = value[3]
        session['money_per'] = float(value[4])
        flag = value[5]

        image = False
        if(flag == '0' or q_img == 'null'):
            image = False
        else:
            image=True
    params = {'que':que, 'flag':image,'id':session['curr_ques_id']}
    conn.close()
    return params

@app.route('/question')
def question():
    print session['curr_round']
    if(session.get('user_id')):
        if(session['curr_round'] == 0):
            params = getQuestion()
            print params
        #params = {'que':'Who is the President of Unites States of Americal', 'op1':'Rahul', 'op2':'Bhawesh', 'op3':'Ishaan', 'op4':'Dheemahi'}
            return render_template('myque.html', params = params)
        elif(session['curr_round'] == 20 or  session['curr_round'] == 30 or session['curr_round'] == 40 or session['curr_round'] == 50 or session['curr_round'] == 60 ):
            session['rapid'] = 0
            session['startTime'] = time.time()
            return redirect('/rapidfire')
        else:    
            return redirect ('/choice')
    else:
        return redirect ('/signup')

@app.route('/question', methods=['POST'])
def validate():
    if(session.get('user_id')):
        _answer = request.form['choice']
        if(_answer == session['curr_ans']):
            go_to_new_round = updateScore()
            if(go_to_new_round):
                if(session['curr_round'] == 20 or  session['curr_round'] == 30 or session['curr_round'] == 40 or session['curr_round'] == 50 or session['curr_round'] == 60 ):
                    session['rapid'] = 0
                    session['startTime'] = time.time()
                    return redirect('/rapidfire')
                else:
                    return redirect ('/choice')
            else:
                return redirect ('/question')
        else:
            go_to_new_round = update()
            if(go_to_new_round):
                if(session['curr_round'] == 20 or  session['curr_round'] == 30 or session['curr_round'] == 40 or session['curr_round'] == 50 or session['curr_round'] == 60 ):
                    session['rapid'] = 0
                    session['startTime'] = time.time()
                    return redirect('/rapidfire')
                else:
                    return redirect ('/choice')
            else:
                return redirect ('/question')
    else:
        return redirect('/signup')


def updateRapid():
    if(session.get('user_id')):
        go_to_new_round  = True
        # if(session['curr_ques_id'] == session['curr_ques_id']):
        ro = session['curr_ques_id'].split('_')[0]
        ques = session['curr_ques_id'].split('_')[1]
        if(ro=='02' and ques >= '12'):
            rapidfireDone()
        elif(ro=='03' and ques >= '12'):
            rapidfireDone()
        elif(ro=='04' and ques >= '12'):
            rapidfireDone()
        elif(ro=='05' and ques >= '12'):
            rapidfireDone()
        elif(ro=='06' and ques >= '12'):
            rapidfireDone()
        else:
            go_to_new_round  = False
        ques = float(ques) + 1
        ques = '%02d' % ques
        
        session['curr_ques_id'] = str(ro) + '_' + str(ques)
        print "ques_id:",session['curr_ques_id']
        conn = mysql.connect()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE players SET curr_ques_id= %s,curr_round = %s WHERE id = %s", (session['curr_ques_id'],str(session['curr_round']), session['user_id']))
            conn.commit()
        except Exception as e:
            print str(e)
        return go_to_new_round

@app.route('/rapidfire')
def rapidfire():
    diff = float(time.time() - session['startTime'])
    print "diff:",diff
    if(diff >= 180.0):
        if(not updateRapid()):
            rapidfireDone()
            return redirect('/choice')
    else:
        params = getRapidFireParams()
        print params
        print "rapid",session["rapid"]
        return render_template('rapidfire.html',params = params)


@app.route('/rapidfire', methods = ['POST'])
def rapidfireValidate():
    if(session.get('user_id')):
        diff = float(time.time() - session['startTime'])
        if(diff >= 180.0):
            if(not updateRapid()):
                rapidfireDone()
            return redirect('/choice')
        else:
            _answer = request.form['ans']
            print _answer
            if(_answer == session['curr_ans']):
                session['rapid'] += session['money_per']
            if(not updateRapid()):
                return redirect('/rapidfire')
            else:
                return redirect('/choice')
    else:
        return redirect('/signup')

def rapidfireDone():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM scores WHERE id = %s", (session['user_id']))
        data = cursor.fetchall()
        print data,session['point_wt'],session['money_wt']
        score = '0'
        money = '0'
        for player in data:
            print player[0],player[1],player[2],player[3]
            score =float(player[1])
            money = float(player[2]) + ((float(session['rapid']) / 10.0) * float(player[2]))
            # session['correctly_answered'] = str(float(player[3])+1)
            print 'error here'
        cursor.execute("UPDATE scores SET money = %s WHERE id = %s", (str(money),session['user_id']))
        conn.commit()
    except Exception as e:
        print str(e)
    ro = session['curr_ques_id'].split('_')[0]
    ques = session['curr_ques_id'].split('_')[1]
    if(ro=='02'):
        ro = '03'
        ques = 00
        session["curr_round"] = 2
    elif(ro=='03'):
        ro = '04'
        ques = 00
        session["curr_round"] = 31
    elif(ro=='04'):
        ro = '05'
        ques = 00
        session["curr_round"] = 4
    elif(ro=='05'):
        ro = '06'
        ques = 00
        session["curr_round"] = 5
    elif(ro=='06'):
        ro = '088'
        ques = 00
        session['curr_round'] = 61
    ques = float(ques) + 1
    ques = '%02d' % ques
    session['curr_ques_id'] = str(ro) + '_' + str(ques)
    conn = mysql.connect()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE players SET curr_ques_id= %s,curr_round = %s WHERE id = %s", (session['curr_ques_id'],str(session['curr_round']), session['user_id']))
        conn.commit()
    except Exception as e:
        print str(e)
    return

@app.route('/retry/<ques>')
def retry(ques):
    reInitializeScore()
    session['curr_trail'] = int(session['curr_trail']) + 1
    session['curr_round'] = 0
    ro = session['curr_ques_id'].split('_')[0]
    ques = 00
    print "ascvadfv:",session['curr_trail'],session['curr_round']
    ques = float(ques) + 1
    ques = '%02d' % ques 
    session['curr_ques_id'] = str(ro) + '_' + str(ques)
    conn = mysql.connect()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE players SET curr_round = %s,curr_ques_id= %s,curr_trial=%s WHERE id = %s", (session['curr_round'],session['curr_ques_id'],int(session['curr_trail']), session['user_id']))
        conn.commit()
    except Exception as e:
        print str(e)
    return redirect('/dashboard')

@app.route('/choice')
def choice():
    conn=mysql.connect()
    try:
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM scores WHERE id = %s", (session['user_id']))

    except Exception as e:

        print str(e)
    data = cursor.fetchall()
    print data
    for value in data:
        _money = float(value[2])
        ansd_ques = float(value[3])
    available_options = 0

    if(session['curr_round'] == 1):
        if(ansd_ques >= 21):
            available_options = 4
        elif(ansd_ques >= 14):
            available_options =3
        elif(ansd_ques >= 7):
            available_options =2
        else:
            available_options =1
        return render_template('choice_R1.html',  options = available_options)

    elif(session['curr_round'] == 2 or session['curr_round'] == 20):
        if(session['curr_round'] == 20):
            session['curr_round'] = 2
            updateRound(session['curr_round'])

        if(_money >= 40):
            available_options = 3
        elif(_money >=30):
            available_options = 2
        elif(_money >= 22):
            available_options = 1
        else:
            if(int(session['curr_trail']) <3):
                print "abcd1"
                return ("<script> alert('you dont have enough money to proceed'); window.location.href ='retry/" + session['curr_ques_id'] + "';</script>")
            else:
                print "abcd2"

                return("<script> alert('you dont have enough money to proceed'); window.location.href ='dashboard';</script>")
        return render_template('choice_R2.html',options = available_options,money = _money)
    elif(session['curr_round'] == 31 or session['curr_round'] == 30 ):
        if(session['curr_round'] == 30):
            session['curr_round'] = 31
            updateRound(session['curr_round'])

        
        if(_money >=12.0):
            available_options = 3
        elif(_money >=8.0):
            available_options = 2
        elif(_money >=6.0):
            available_options = 1
        else:
            if(int(session['curr_trail']) <3):
                return ("<script> alert('you dont have enough money to proceed'); window.location.href ='retry/" + session['curr_ques_id'] + "';</script>")
            else:
                return("<script> alert('you dont have enough money to proceed'); window.location.href ='dashboard';</script>")
        
        return render_template('choice_R3_1.html',options = available_options,money = _money)
    elif(session['curr_round'] == 32):
        if(_money >=10):
            available_options = 3
        elif(_money >=7):
            available_options = 2
        elif(_money >=4):
            available_options = 1
        else:
            if(int(session['curr_trail']) <3):
                return ("<script> alert('you dont have enough money to proceed'); window.location.href ='retry/" + session['curr_ques_id'] + "';</script>")
            else:
                return("<script> alert('you dont have enough money to proceed'); window.location.href ='dashboard';</script>")
        
        return render_template('choice_R3_2.html',options = available_options,money = _money)
    elif(session['curr_round'] == 33):
        if(_money >= 4):
            available_options = 4
        elif(_money >=1.3):
            available_options = 3
        elif(_money >= .5):
            available_options = 2
        else:
            available_options =1
        return render_template('scenario_3.html',options = available_options,money = _money)
    elif(session['curr_round'] == 4 or session['curr_round'] == 40 ):
        if(session['curr_round'] == 40):
            session['curr_round'] = 4
            updateRound(session['curr_round'])

        if(_money >=25):
            available_options = 4
        elif(_money >= 15):
            available_options = 3
        elif(_money >= 10):
            available_options = 2
        elif(_money >= 7):
            available_options = 1
        else:
            if(int(session['curr_trail']) <3):
                return ("<script> alert('you dont have enough money to proceed'); window.location.href ='retry/" + session['curr_ques_id'] + "';</script>")
            else:
                return("<script> alert('you dont have enough money to proceed'); window.location.href ='dashboard';</script>")
        return render_template('choice_R4.html',options = available_options,money = _money)
    elif(session['curr_round'] == 5 or session['curr_round'] == 50 ):
        if(session['curr_round'] == 50):
            session['curr_round'] = 5
            updateRound(session['curr_round'])

        
        if(_money >=84):
            available_options =4
        elif(_money >=80):
            available_options =3
        elif(_money >=75):
            available_options =2
        elif(_money >=70):
            available_options =1
        else:
            if(int(session['curr_trail']) <3):
                return ("<script> alert('you dont have enough money to proceed'); window.location.href ='retry/" + session['curr_ques_id'] + "';</script>")
            else:
                return("<script> alert('you dont have enough money to proceed'); window.location.href ='dashboard';</script>")
        
        return render_template('choice_R5.html',options = available_options,money = _money)
    elif(session['curr_round'] == 51):
        if(_money >=3):
            available_options = 2
        else:
            available_options = 1
        return render_template('scenario_5.html',options = available_options,money = _money)

    elif(session['curr_round'] == 61 or session['curr_round'] == 60 ):
        if(session['curr_round'] == 60):
            session['curr_round'] = 61
            updateRound(session['curr_round'])
        _money = _money * 3
        if(_money >=412.72):
            available_options = 3
        elif(_money>=350.10):
            available_options = 2
        elif(_money>=276.35):
            available_options = 1
        else:
            if(int(session['curr_trail']) <3):
                return ("<script> alert('you dont have enough money to proceed'); window.location.href ='retry/" + session['curr_ques_id'] + "';</script>")
            else:
                return("<script> alert('you dont have enough money to proceed'); window.location.href ='dashboard';</script>")
        
        return render_template('choice_R6_1.html',options = available_options,money = _money)
    elif(session['curr_round'] == 62):
        if(_money >=179.70):
            available_options = 3
        elif(_money>=147.90):
            available_options = 2
        elif(_money>=119.32):
            available_options = 1
        else:
            if(int(session['curr_trail']) <3):
                return ("<script> alert('you dont have enough money to proceed'); window.location.href ='retry/" + session['curr_ques_id'] + "';</script>")
            else:
                return("<script> alert('you dont have enough money to proceed'); window.location.href ='dashboard';</script>")
        
        return render_template('choice_R6_2.html',options = available_options,money = _money)
    elif(session['curr_round'] == 63):
        if(_money >=310.98):
            available_options = 3
        elif(_money>=262.28):
            available_options = 2
        elif(_money>=201.22):
            available_options = 1
        else:
            if(int(session['curr_trail']) <3):
                return ("<script> alert('you dont have enough money to proceed'); window.location.href ='retry/" + session['curr_ques_id'] + "';</script>")
            else:
                return("<script> alert('you dont have enough money to proceed'); window.location.href ='dashboard';</script>")
        
        return render_template('choice_R6_3.html',options = available_options,money = _money)
    elif(session['curr_round'] == 64):
        if(_money >=39.52):
            available_options = 3
        elif(_money>=35.27):
            available_options = 2
        elif(_money>=32.32):
            available_options = 1
        else:
            if(int(session['curr_trail']) <3):
                return ("<script> alert('you dont have enough money to proceed'); window.location.href ='retry/" + session['curr_ques_id'] + "';</script>")
            else:
                return("<script> alert('you dont have enough money to proceed'); window.location.href ='dashboard';</script>")
        
        return render_template('choice_R6_4.html',options = available_options,money = _money)
    elif(session['curr_round'] == 65):
        if(_money >=75.3025):
            available_options = 3
        elif(_money>=63.7):
            available_options = 2
        elif(_money>=56.42):
            available_options = 1
        else:
            if(int(session['curr_trail']) <3):
                return ("<script> alert('you dont have enough money to proceed'); window.location.href ='retry/" + session['curr_ques_id'] + "';</script>")
            else:
                return("<script> alert('you dont have enough money to proceed'); window.location.href ='dashboard';</script>")
        
        return render_template('choice_R6_5.html',options = available_options,money = _money)
    elif(session['curr_round'] == 66):
        if(_money >=412.7248):
            available_options = 3
        elif(_money>=350.1048):
            available_options = 2
        elif(_money>=276.348):
            available_options = 1
        else:
            if(int(session['curr_trail']) <3):
                return ("<script> alert('you dont have enough money to proceed'); window.location.href ='retry/" + session['curr_ques_id'] + "';</script>")
            else:
                return("<script> alert('you dont have enough money to proceed'); window.location.href ='dashboard';</script>")
        
        return render_template('scenario_6_1.html',options = available_options,money = _money)
    elif(session['curr_round'] == 67):
        if(_money >=412.7248):
            available_options = 3
        elif(_money>=350.1048):
            available_options = 2
        elif(_money>=276.348):
            available_options = 1
        else:
            if(int(session['curr_trail']) <3):
                return ("<script> alert('you dont have enough money to proceed'); window.location.href ='retry/" + session['curr_ques_id'] + "';</script>")
            else:
                return("<script> alert('you dont have enough money to proceed'); window.location.href ='dashboard';</script>")
        
        return render_template('scenario_6_2.html',options = available_options,money = _money)
    elif(session['curr_round'] == 68):
        if(_money >=412.7248):
            available_options = 3
        elif(_money>=350.1048):
            available_options = 2
        elif(_money>=276.348):
            available_options = 1
        return render_template('scenario_6_3.html',options = available_options,money = _money)        
    else:
        return render_template('404.html',error = "some problem with round choice")

@app.route('/choice',methods = ['POST'])
def updateChoice():
    if(session['curr_round'] == 1):
        _answer = request.form['soil']
        conn=mysql.connect()
        try:
            cursor=conn.cursor()
            # print "UPDATE players SET r1_res = %s WHERE id = %s"
            query = "UPDATE players SET r1_res = '{a}' WHERE id = {i};".format(a = _answer,i = session['user_id'])
            cursor.execute(query)
            conn.commit()
            session['r1_res'] = _answer
            updateDashboardStyle()

            # cursor.execute("UPDATE scores SET points = %s WHERE id = %s", (str(score), str(money), session['correctly_answered'], session['user_id']))

        except Exception as e:
            print str(e)
        finally:
            conn.close()
        reInitializeScore()
        session['curr_round'] = 0
        updateRound(session['curr_round'])

        return render_template('dashboard.html')
    elif(session['curr_round'] == 2):
        _answer = request.form['arch']
        points = 0
        money = 0
        conn=mysql.connect()
        try:
            cursor=conn.cursor()
            cursor2=conn.cursor()

            cursor.execute("UPDATE players SET r2_res = %s WHERE id = %s", (_answer,session['user_id']))
            conn.commit()
            session['r2_res'] = _answer
            updateDashboardStyle()

            cursor2.execute("SELECT * FROM scores WHERE id = %s", (session['user_id']))
            data = cursor2.fetchall()
            for value in data:
                points = float(value[1])
                money = float(value[2])
        except Exception as e:
            print str(e)
        finally:
            conn.close()
        if(_answer == 'UrbanDesigner'):
            money = money - 40
            new_points = points + 4000 + money * 50 #round2 Judgement points
            updatePoints(new_points)
            reInitializeScore()
            session['curr_round'] = 0
            updateRound(session['curr_round'])

            return render_template('scenario_2_1.html')
        elif(_answer == 'GreenDesignArchitect'):
            money = money - 30
            new_points = points + 3000 + money * 50 #round2 Judgement points
            updatePoints(new_points)
            reInitializeScore()
            session['curr_round'] = 0
            updateRound(session['curr_round'])

            return render_template('scenario_2_1.html')

        elif(_answer == 'CommercialArchitect'):
            money = money - 32
            new_points = points + 1500 + money * 50 #round2 Judgement points
            updatePoints(new_points)
            reInitializeScore()
            session['curr_round'] = 0
            updateRound(session['curr_round'])

            return render_template('scenario_2_2.html')
        else:
            pass
        return render_template('404.html',error = "some error with scenario selection")
    elif(session['curr_round'] == 31):
        _answer = request.form['pits']
        points = 0
        money = 0
        conn=mysql.connect()
        try:
            cursor=conn.cursor()
            cursor2=conn.cursor()

            cursor.execute("UPDATE players SET r31_res = %s WHERE id = %s", (_answer,session['user_id']))
            conn.commit()
            session['r31_res'] = _answer


            cursor2.execute("SELECT * FROM scores WHERE id = %s", (session['user_id']))
            data = cursor2.fetchall()
            for value in data:
                points = float(value[1])
                money = float(value[2])
        except Exception as e:
            print str(e)
        finally:
            conn.close()
        new_points = points
        if(_answer == 'TestPits'):
            new_points = points + 1300
            money = money - 6
        elif(_answer == 'Trenching'):
            new_points = points + 3000
            money = money - 8
        elif(_answer == 'InSituTesting'):
            new_points = points +4000
            money = money - 12
        print new_points,money,session['curr_round']
        updatePoints(new_points)
        updateMoney(money)
        session['curr_round'] = 32
        updateRound(session['curr_round'])

        return redirect('/choice')
        # return render_template('choice_R3_2.html')
    elif(session['curr_round'] == 32):
        _answer = request.form['survey']
        points = 0
        money = 0
        conn=mysql.connect()
        try:
            cursor=conn.cursor()
            cursor2=conn.cursor()

            cursor.execute("UPDATE players SET r32_res = %s WHERE id = %s", (_answer,session['user_id']))
            conn.commit()
            session['r32_res'] = _answer
            updateDashboardStyle()


            cursor2.execute("SELECT * FROM scores WHERE id = %s", (session['user_id']))
            data = cursor2.fetchall()
            for value in data:
                points = float(value[1])
                money = float(value[2])
        except Exception as e:
            print str(e)
        finally:
            conn.close()
        new_points = 0

        if(_answer == 'SurveyorA'):
            money = money - 10
            new_points = points + 4000
        elif(_answer == 'SurveyorB'):
            money = money - 7
            new_points = points + 3000
        elif(_answer == 'SurveyorC'):
            money = money - 4
            new_points = points + 1000
        updatePoints(new_points)
        updateMoney(money)
        session['curr_round'] =33
        updateRound(session['curr_round'])

        return redirect('/choice')
        # return render_template('scenario_3.html',money = money)

    elif(session['curr_round'] == 33):
        _answer = request.form['soilReport']
        points = 0
        money = 0
        conn=mysql.connect()
        try:
            cursor2=conn.cursor()
            cursor2.execute("SELECT * FROM scores WHERE id = %s", (session['user_id']))
            data = cursor2.fetchall()
            print _answer
            for value in data:
                points = float(value[1])
                money = float(value[2])
            print points,money
        except Exception as e:
            print str(e)
        finally:
            conn.close()
        if(_answer  == 'replace'):
            money = money - 1.3
            new_points = points + 550
        elif(_answer == 'chemical'):
            money = money - 4
            new_points = points + 1000
        elif(_answer == 'compact'):
            money = money - .5
            new_points = points + 200
        else:
            new_points = points
        new_points = new_points +  money * 11.84

        updatePoints(new_points)
        reInitializeScore()
        session['curr_round'] = 0
        updateRound(session['curr_round'])
        return render_template('dashboard.html')
    elif(session['curr_round'] == 4):
        _answer = request.form['machine']
        points = 0
        money = 0
        scenario = ''
        conn=mysql.connect()
        try:
            cursor=conn.cursor()
            cursor2=conn.cursor()
            
            cursor.execute("UPDATE players SET r4_res = %s WHERE id = %s", (_answer,session['user_id']))
            conn.commit()
            session['r4_res'] = _answer
            updateDashboardStyle()


            
            cursor2.execute("SELECT * FROM scores WHERE id = %s", (session['user_id']))
            data = cursor2.fetchall()
            print _answer
            for value in data:
                points = float(value[1])
                money = float(value[2])
            print points,money
        except Exception as e:
            print str(e)
        finally:
            conn.close()
        if(_answer  == 'modern'):
            money = money - 15 -1.75
            new_points = points + 320
            scenario = 'scenario_4_1.html'
        elif(_answer == 'medium'):
            money = money - 10 -3.25
            new_points = points + 200
            scenario = 'scenario_4_2.html'

        elif(_answer == 'wretched'):
            money = money - 7 - 6.5
            new_points = points + 100
            scenario = 'scenario_4_3.html'
            
        elif(_answer == 'contract'):
            money = money - 25 
            new_points = points + 400
            scenario = 'scenario_4_4.html'
        else:
            new_points = points

        new_points = new_points +  money * 59.6
        updatePoints(new_points)
        reInitializeScore()
        session['curr_round'] = 0
        updateRound(session['curr_round'])
        return render_template(scenario)
    elif(session['curr_round'] == 5):
        _answer = request.form['foundation']
        points = 0
        money = 0
        r1_res = 'AlluvialSoil'
        conn=mysql.connect()
        try:
            cursor=conn.cursor()
            cursor2=conn.cursor()
            cursor3 = conn.cursor()

            cursor.execute("UPDATE players SET r5_res = %s WHERE id = %s", (_answer,session['user_id']))
            conn.commit()
            session['r5_res'] = _answer
            updateDashboardStyle()            
            cursor2.execute("SELECT * FROM scores WHERE id = %s", (session['user_id']))
            data = cursor2.fetchall()

            cursor3.execute("SELECT r1_res FROM players where id = %s",(session['user_id']))
            data2 = cursor3.fetchall()
            print _answer

            for value in data:
                points = float(value[1])
                money = float(value[2])
            for value in data2:
                print value
                r1_res = str(value[0])

            print points,money
        except Exception as e:
            print str(e)
        finally:
            conn.close()

        if(_answer == 'pile'):
            money = money - 80
            if(r1_res == 'AlluvialSoil'):
                points = points + 3000
        elif(_answer == 'stone'):
            money = money - 70
            if(r1_res == 'MountainSoil'):
                points = points + 3000
        elif(_answer == 'strip'):
            money = money - 75
            if(r1_res == 'BlackSoil'):
                points = points + 3000
        elif(_answer == 'raft'):
            money = money - 84
            if(r1_res == 'LateriteSoil'):
                points = points + 3000
        new_points = points + 1000
        updatePoints(new_points)
        updateMoney(money)
        session['curr_round'] = 51
        updateRound(session['curr_round'])
        return redirect('/choice')
    elif(session['curr_round'] == 51):
        _answer = request.form['FReport']
        points = 0
        money = 0
        conn=mysql.connect()
        try:
            cursor2=conn.cursor()
            cursor2.execute("SELECT * FROM scores WHERE id = %s", (session['user_id']))
            data = cursor2.fetchall()
            print _answer
            for value in data:
                points = float(value[1])
                money = float(value[2])
            print points,money
        except Exception as e:
            print str(e)
        finally:
            conn.close()
        if(_answer  == 'increase'):
            money = money - 3
            new_points = points + 1000
        elif(_answer == 'sit'):
            money = money - 0
            new_points = points + 100
        else:
            new_points = points
        new_points = new_points +  money * 41.6

        updatePoints(new_points)
        reInitializeScore()
        session['curr_round'] = 0
        updateRound(session['curr_round'])
        return render_template('dashboard.html')
    elif(session['curr_round'] == 61):
        _answer = request.form['cement']
        points = 0
        money = 0
        conn=mysql.connect()
        try:
            cursor=conn.cursor()
            cursor2=conn.cursor()

            cursor.execute("UPDATE players SET r61_res = %s WHERE id = %s", (_answer,session['user_id']))
            conn.commit()
            session['r61_res'] = _answer


            cursor2.execute("SELECT * FROM scores WHERE id = %s", (session['user_id']))
            data = cursor2.fetchall()
            for value in data:
                points = float(value[1])
                money = float(value[2]) * 3
        except Exception as e:
            print str(e)
        finally:
            conn.close()
        new_points = points
        if(_answer == 'SandlineCorporation'):
            new_points = points + 3000
            money = money - 412.72
        elif(_answer == 'PentosLimited'):
            new_points = points + 1750
            money = money - 350.10
        elif(_answer == 'WestrosEsssosCo'):
            new_points = points + 900
            money = money - 276.35
        print new_points,money,session['curr_round']
        updatePoints(new_points)
        updateMoney(money)
        session['curr_round'] = 62
        updateRound(session['curr_round'])
        return redirect('/choice')

    elif(session['curr_round'] == 62):
        _answer = request.form['FineAggregate']
        points = 0
        money = 0
        conn=mysql.connect()
        try:
            cursor=conn.cursor()
            cursor2=conn.cursor()

            cursor.execute("UPDATE players SET r62_res = %s WHERE id = %s", (_answer,session['user_id']))
            conn.commit()
            session['r62_res'] = _answer


            cursor2.execute("SELECT * FROM scores WHERE id = %s", (session['user_id']))
            data = cursor2.fetchall()
            for value in data:
                points = float(value[1])
                money = float(value[2]) 
        except Exception as e:
            print str(e)
        finally:
            conn.close()
        new_points = points
        if(_answer == 'SandlineCorporation'):
            new_points = points + 3000
            money = money - 179.7
        elif(_answer == 'PentosLimited'):
            new_points = points + 1750
            money = money - 147.9
        elif(_answer == 'WestrosEsssosCo'):
            new_points = points + 900
            money = money - 119.32
        print new_points,money,session['curr_round']
        updatePoints(new_points)
        updateMoney(money)
        session['curr_round'] = 63
        updateRound(session['curr_round'])
        return redirect('/choice')

    elif(session['curr_round'] == 63):
        _answer = request.form['CoarseAggregate']
        points = 0
        money = 0
        conn=mysql.connect()
        try:
            cursor=conn.cursor()
            cursor2=conn.cursor()

            cursor.execute("UPDATE players SET r63_res = %s WHERE id = %s", (_answer,session['user_id']))
            conn.commit()
            session['r63_res'] = _answer


            cursor2.execute("SELECT * FROM scores WHERE id = %s", (session['user_id']))
            data = cursor2.fetchall()
            for value in data:
                points = float(value[1])
                money = float(value[2]) 
        except Exception as e:
            print str(e)
        finally:
            conn.close()
        new_points = points
        if(_answer == 'SandlineCorporation'):
            new_points = points + 3000
            money = money - 310.98
        elif(_answer == 'PentosLimited'):
            new_points = points + 1750
            money = money - 262.28
        elif(_answer == 'WestrosEsssosCo'):
            new_points = points + 900
            money = money - 201.22
        print new_points,money,session['curr_round']
        updatePoints(new_points)
        updateMoney(money)
        session['curr_round'] = 64
        updateRound(session['curr_round'])
        return redirect('/choice')

    elif(session['curr_round'] == 64):
        _answer = request.form['FlyAsh']
        points = 0
        money = 0
        conn=mysql.connect()
        try:
            cursor=conn.cursor()
            cursor2=conn.cursor()

            cursor.execute("UPDATE players SET r64_res = %s WHERE id = %s", (_answer,session['user_id']))
            conn.commit()
            session['r64_res'] = _answer


            cursor2.execute("SELECT * FROM scores WHERE id = %s", (session['user_id']))
            data = cursor2.fetchall()
            for value in data:
                points = float(value[1])
                money = float(value[2]) 
        except Exception as e:
            print str(e)
        finally:
            conn.close()
        new_points = points
        if(_answer == 'SandlineCorporation'):
            new_points = points + 3000
            money = money - 39.52
        elif(_answer == 'PentosLimited'):
            new_points = points + 1750
            money = money - 35.27
        elif(_answer == 'WestrosEsssosCo'):
            new_points = points + 900
            money = money - 32.32
        print new_points,money,session['curr_round']
        updatePoints(new_points)
        updateMoney(money)
        session['curr_round'] = 65
        updateRound(session['curr_round'])
        return redirect('/choice')

    elif(session['curr_round'] == 65):
        _answer = request.form['SuperPlasticizer']
        points = 0
        money = 0
        conn=mysql.connect()
        try:
            cursor=conn.cursor()
            cursor2=conn.cursor()

            cursor.execute("UPDATE players SET r65_res = %s WHERE id = %s", (_answer,session['user_id']))
            conn.commit()
            session['r65_res'] = _answer


            cursor2.execute("SELECT * FROM scores WHERE id = %s", (session['user_id']))
            data = cursor2.fetchall()
            for value in data:
                points = float(value[1])
                money = float(value[2]) 
        except Exception as e:
            print str(e)
        finally:
            conn.close()
        new_points = points
        if(_answer == 'SandlineCorporation'):
            new_points = points + 3000
            money = money - 75.30
        elif(_answer == 'PentosLimited'):
            new_points = points + 1750
            money = money - 63.7
        elif(_answer == 'WestrosEsssosCo'):
            new_points = points + 900
            money = money - 56.42
        money = money - 24.15 - 16.2
        print new_points,money,session['curr_round']
        updatePoints(new_points)
        updateMoney(money)
        session['curr_round'] = 66
        updateRound(session['curr_round'])
        return redirect('/choice')

    elif(session['curr_round'] == 66):
        _answer = request.form['hire']
        points = 0
        money = 0
        conn=mysql.connect()
        try:
            # cursor=conn.cursor()
            cursor2=conn.cursor()

            # cursor.execute("UPDATE players SET r66_res = %s WHERE id = %s", (_answer,session['user_id']))
            # conn.commit()
            session['r66_res'] = _answer


            cursor2.execute("SELECT * FROM scores WHERE id = %s", (session['user_id']))
            data = cursor2.fetchall()
            for value in data:
                points = float(value[1])
                money = float(value[2]) 
        except Exception as e:
            print str(e)
        finally:
            conn.close()
        new_points = points
        if(_answer == 'Accept'):
            new_points = points + 100
            money = money - 150
        elif(_answer == 'Uphold'):
            new_points = points + 2500
            money = money - 200
        print new_points,money,session['curr_round']
        updatePoints(new_points)
        updateMoney(money)
        session['curr_round'] = 67
        updateRound(session['curr_round'])
        return redirect('/choice')

    elif(session['curr_round'] == 67):
        _answer = request.form['negligence']
        points = 0
        money = 0
        conn=mysql.connect()
        try:
            # cursor=conn.cursor()
            cursor2=conn.cursor()

            # cursor.execute("UPDATE players SET r66_res = %s WHERE id = %s", (_answer,session['user_id']))
            # conn.commit()
            session['r67_res'] = _answer


            cursor2.execute("SELECT * FROM scores WHERE id = %s", (session['user_id']))
            data = cursor2.fetchall()
            for value in data:
                points = float(value[1])
                money = float(value[2]) 
        except Exception as e:
            print str(e)
        finally:
            conn.close()
        new_points = points
        if(_answer == 'Bribe'):
            new_points = points + 100
            money = money - 2
        elif(_answer == 'Compensate'):
            new_points = points + 600
            money = money - 8
        elif(_answer == 'CompensateIncrease'):
            new_points = points + 1000
            money = money - 15
        print new_points,money,session['curr_round']
        updatePoints(new_points)
        updateMoney(money)
        session['curr_round'] = 68
        updateRound(session['curr_round'])
        return redirect('/choice')

    elif(session['curr_round'] == 68):
        _answer = request.form['water']
        points = 0
        money = 0
        conn=mysql.connect()
        try:
            # cursor=conn.cursor()
            cursor2=conn.cursor()

            # cursor.execute("UPDATE players SET r66_res = %s WHERE id = %s", (_answer,session['user_id']))
            # conn.commit()
            session['r68_res'] = _answer


            cursor2.execute("SELECT * FROM scores WHERE id = %s", (session['user_id']))
            data = cursor2.fetchall()
            for value in data:
                points = float(value[1])
                money = float(value[2]) 
        except Exception as e:
            print str(e)
        finally:
            conn.close()
        new_points = points
        if(_answer == 'Ignore'):
            new_points = points + 0
            money = money - 0
        elif(_answer == 'Share'):
            new_points = points + 1000
            money = money - 3
        elif(_answer == 'Stop'):
            new_points = points + 500
            money = money - 1.75
        
        new_points = new_points + money * 10.88
        print new_points,money,session['curr_round']
        

        updatePoints(new_points)
        reInitializeScore()
        session['curr_round'] = 0
        updateRound(session['curr_round'])
        return redirect('/final')
    else:
        return render_template('404.html',error = "some problem with round choice")

def updateRound(new_round):
    conn = mysql.connect()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE players SET curr_round = %s WHERE id = %s",(str(new_round), session['user_id']))
        conn.commit()

    except Exception as e:
        print str(e)
    finally:
        conn.close()
    return

def updateMoney(new_money):
    conn = mysql.connect()
    try:
        cursor = conn.cursor()
        print 'hey',new_money
        cursor.execute("UPDATE scores SET money = %s WHERE id = %s",(str(new_money), session['user_id']))
        print 'hey',cursor.fetchall()
        conn.commit()

    except Exception as e:
        print str(e)
    finally:
        conn.close()
    return


def updatePoints(new_Points):
    conn = mysql.connect()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE scores SET points = %s WHERE id = %s",(str(new_Points), session['user_id']))
        conn.commit()

    except Exception as e:
        print str(e)
    finally:
        conn.close()
    return

def reInitializeScore():
    conn=mysql.connect()
    try:
        cursor=conn.cursor()
        cursor.execute("UPDATE scores SET money = '0', correctly_answered = '0' WHERE id = %s", (session['user_id']))
        conn.commit()

    except Exception as e:
        print str(e)
    finally:
        conn.close()
    return
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html',error = 404)

if __name__ == "__main__":
    app.run(debug=True,port=5005,use_evalex=False)
    # app.run(debug=True,host='139.59.17.132',port=80,use_evalex=False)
