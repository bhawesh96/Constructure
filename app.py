import traceback, warnings
warnings.filterwarnings("ignore")

from flask import Flask, render_template, redirect

app = Flask(__name__)
# MySQL configurations

@app.route('/home')
@app.route('/')
def main():
    return render_template('home.html')

@app.route('/logout')
def logout():
    return redirect('/')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(debug=True,port=5005,use_evalex=False)
