from flask import Flask, request, render_template
import sys
app = Flask(__name__)

@app.route('/index', methods=['GET', 'POST'])
def index():
   if request.method=='GET':
       print('hiiii', file=sys.stdout)
       array = ['TOEFL-IBT', 'IELTS', 'Cambridge', 'VU Test']
   elif request.method=='POST':
       print('hi', file=sys.stdout)
       text = request.form.get('etestt')
       processed_text = text.upper()
       print(processed_text, file=sys.stdout)
   return render_template('index.html', index = array)

@app.route('/index', methods=['POST'])
def index_post():
    print('hi', file=sys.stdout)
    text = request.form.get('etestt')
    processed_text = text.upper()
    print(processed_text, file=sys.stdout)
    return processed_text

if __name__ == '__main__':
   app.run(debug = True)