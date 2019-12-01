from flask import Flask, render_template
app = Flask(__name__)

@app.route('/index')
def index():
   array = ['TOEFL-IBT', 'IELTS', 'Cambridge', 'VU Test']
   return render_template('index.html', index = array)

if __name__ == '__main__':
   app.run(debug = True)