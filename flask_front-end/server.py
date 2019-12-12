from flask import Flask, request, url_for, redirect, render_template, render_template_string, jsonify
import rdflib
import sys
import random
app = Flask(__name__)

ontology = "Ontology.ttl"
g = rdflib.Graph()
g.parse(ontology, format='ttl')

def get_track(degree_name):
    degree = degree_name
    track_list = []
    track_q_result = g.query(
      """select ?track_label where{
         VALUES ?masterdegree { """+degree+""" }
         ?masterdegree rdf:type sec:MasterDegree .
         ?masterdegree sec:hasTrack ?track .
         ?track rdfs:label ?track_label .
         FILTER (LANG(?track_label) = 'en')
      }
      """)
    print("track:")
    for row in track_q_result:
           track_list.append("%s" % row)
           print("%s" % row)

@app.route('/result')
def result():
    return render_template('result.html',
      selected_master=request.args.get('selected_master'),
      gpa=request.args.get('gpa'),
      gpa_scale=request.args.get('gpa_scale'),
      converted_gpa=request.args.get('converted_gpa'))

@app.route('/index')
def index_get():
   print('sup')
   if request.method=='GET':
       print('hiiii', file=sys.stdout)
       ##########################################
       ####### DISPLAY MASTER PRGRM BEGIN #######
       ##########################################
       master_q_result = g.query(
        """select ?master_label where {
           ?university rdf:type sec:University .
           ?university sec:hasMasterDegree ?master .
           ?master rdfs:label ?master_label .
           FILTER (LANG(?master_label ) = "en")
        }order by ?master_label""")
       master_prgrm = []
       master_id = ['ai', 'bsb', 'ba', 'cs', 'eoc', 'gbh', 'is', 'lgs', 'math', 'pdcs', 'sbi', 'sfm']
       for row in master_q_result:
           master_prgrm.append("%s" % row)
           print("%s" % row)
       print(master_prgrm)
       print(master_id)
       master_dict = dict(zip(master_prgrm, master_id))
       print(master_dict)
       ##########################################
       ####### DISPLAY MASTER PRGRM END #########
       ##########################################

       ##########################################
       ####### DISPLAY MASTER TRACK BEGIN #######
       ##########################################

       # get the selected master program
       # after getting the selected master program do something like this for ALL 12 programs.
       # if (selected_master == "MSc Artificial Intelligence"):
          # selected_master = "sec:mscArtificalIntelligence"
          # get_track(selected_master)
       # ^ that is needed to pass to the query and query from the ontology.

       ##########################################
       ####### DISPLAY MASTER TRACK END #########
       ##########################################

       ##########################################
       ####### DISPLAY ENGLISH TEST BEGIN #######
       ##########################################
       english_q_result = g.query(
        """select ?englishtest_label where {
          ?englishtest rdf:type sec:EnglishTest .
          ?englishtest rdfs:label ?englishtest_label .
          FILTER (LANG(?englishtest_label)  = 'en')
        }""")
       english_test = []
       for row in english_q_result:
           english_test.append("%s" % row)
           print("%s" % row)
       print(english_test)
       ########################################
       ####### DISPLAY ENGLISH TEST END #######
       ########################################

       return render_template('index.html', master_dict=master_dict, english_test=english_test)

@app.route('/index', methods=['POST'])
def index_post():
   print('sup')
   if request.method=='POST':
       selected_master = request.form.get('programme')
       if selected_master == 'ai':
           selected_master = 'MSc Artificial Intelligence'
       elif selected_master == 'cs':
           selected_master = 'MSc Computer Science'
       elif selected_master == 'ba':
           selected_master = 'MSc Business Analytics'
       elif selected_master == 'is':
           selected_master = 'MSc Information Science'
       #########################
       ####### GPA BEGIN #######
       #########################
       grading_scale = {'usa' :'0-4',
                 'ind':'0-10'}
       gpa_scale = request.form.get('gpascale')
       print("selected GPA scale:", gpa_scale)
       gpa = request.form.get('gpa')
       gpa = float(gpa)
       print("GPA:", gpa)
       converted_gpa = 0
       #####check for grading scale
       if gpa_scale in grading_scale['usa']:
           #print('usa conversion')
           ###calls us to uk gpa conversion
           calc_us_gpa = us_to_uk(gpa)
           print(calc_us_gpa)
           converted_gpa  = calc_us_gpa
       else:
           print('carrying india to us conversion first')
           ###converts indian gpa to usa gpa first
           usa_gpa = ind_to_us(gpa)
           #print(usa_gpa)
           ###converts us gpa to uk gpa
           calc_ind_gpa = us_to_uk(usa_gpa)
           print(calc_ind_gpa)
           converted_gpa = calc_ind_gpa
        #########################
        ####### GPA END #######
        #########################
       print(converted_gpa)
       return redirect(url_for('result',
        selected_master=selected_master,
        gpa=gpa,
        gpa_scale=gpa_scale,
        converted_gpa=converted_gpa))


@app.route('/programme',methods=['POST'])
def programme():
    name=request.args.get('value')
    print(name)
    return jsonify({'reply':'success'})


#####converts us gpa to uk gpa
def us_to_uk(score):
    print('comes into the conversion')
    print(score)
    if score == 4:
        return round(random.uniform(70, 99), 2)
    if score < 4 and score >= 3.7:
        return round(random.uniform(65, 69), 2)
    if score < 3.7 and score >= 3.3:
        return round(random.uniform(60, 64), 2)
    if score < 3.3 and score >= 3:
        return round(random.uniform(55, 59), 2)
    if score < 3 and score >= 2.7:
        return round(random.uniform(50, 54), 2)
    if score < 2.7 and score >= 2.3:
        return round(random.uniform(45, 49), 2)
    if score < 2.3 and score >= 2:
        return round(random.uniform(40, 44), 2)
    if score <= 2 and score >= 1:
        return round(random.uniform(35, 39), 2)
    if score < 1:
        return round(random.uniform(0, 35), 2)

#####Converts indian gpa to US gpa
def ind_to_us(gpa):
    if gpa >= 8.5:
        return round(random.uniform(3.7, 4.0), 1)
    if gpa >= 8 and gpa <= 8.4:
        print('3.7')
        return 3.7
    if gpa >= 7.5 and gpa <= 7.9:
        return 3.3
    if gpa >= 7 and gpa <= 7.4:
        return 3.0
    if gpa >= 6.5 and gpa <= 6.9:
        return 2.7
    if gpa >= 6.0 and gpa <= 6.4:
        return 2.3
    if gpa >= 5.5 and gpa <= 5.9:
        return 2
    if gpa >= 5.0 and gpa <= 5.4:
        return 1.7
    if gpa < 5:
        return round(random.uniform(0, 1.3), 1)

if __name__ == '__main__':
   print("\nQuick access link: http://127.0.0.1:5000/index")
   print("\n")
   app.run(debug = True)
