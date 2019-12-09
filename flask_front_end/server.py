from flask import Flask, request, render_template
import rdflib
import sys
app = Flask(__name__)

ontology = "/Users/agukalpa/Documents/VU Amsterdam/Knowledge Engineering/StudentEligibilityChecker/flask_front_end/Ontology.ttl" 
graph = rdflib.Graph()
graph.parse(ontology, format='ttl')
#print(result)
qres = graph.query(
    """SELECT DISTINCT ?Track ?ExtraKnowledge
       WHERE {
          ?a sec:Track ?Track .
          ?b sec:ExtraKnowledge ?ExtraKnowledge
       }""")

#print("query:", qres)
for row in qres:
    print("%s requiresKnowledge %s" % row)

@app.route('/index', methods=['GET', 'POST'])
def index():
   print('sup')
   if request.method=='GET':
       print('hiiii', file=sys.stdout)
       array = ['TOEFL-IBT', 'IELTS', 'Cambridge', 'VU Test']
       return render_template('index.html', index = array)
   elif request.method=='POST':
       print('hi', file=sys.stdout)
       text = request.form.get('first-name')
       processed_text = text.upper()
       print(processed_text, file=sys.stdout)
       return render_template('index.html')

# @app.route('/index', methods=['POST'])
# def index_post():
#     print('hi', file=sys.stdout)
#     text = request.form.get('etestt')
#     processed_text = text.upper()
#     print(processed_text, file=sys.stdout)
#     return processed_text

if __name__ == '__main__':
   app.run(debug = True)