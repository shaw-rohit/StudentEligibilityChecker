from flask import Flask, request, url_for, redirect, render_template, render_template_string, jsonify
from rdflib import Graph
import sys
import io
import random
app = Flask(__name__)

ontology = "Ontology.ttl"
g = Graph()
g.parse(ontology, format='ttl')

master_map = {}
master_track_map = {}

############################################
####### GET TRACK LIST FROM ONTOLOGY #######
############################################
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
      }order by ?track_label
      """)
    for row in track_q_result:
        track_list.append("%s" % row)
    track_list.insert(0, "Choose")
    
    return(track_list)

################################################
####### GET KNOWLEDGE LIST FROM ONTOLOGY #######
################################################
def get_knowledge(degree_name, track_name):
    degree = degree_name
    trackname = track_name
    knowledge_list = []

    knowledge_q_result = g.query(
      """select ?knowledge_label where{
         VALUES ?masterdegree { """+degree+""" }
         VALUES ?track { """+trackname+""" }
         ?masterdegree sec:hasTrack ?track .
         ?track rdf:type sec:Track .
         ?track sec:requiresKnowledge ?knowledge .
         ?knowledge rdfs:label ?knowledge_label .
         FILTER (LANG(?knowledge_label) = 'en')
      }order by ?knowledge_label
      """)

    for row in knowledge_q_result:
      knowledge_list.append("%s" % row)

    return (knowledge_list)



@app.route('/result')
def result():
    return render_template('result.html',
      selected_master=request.args.get('selected_master'),
      gpa=request.args.get('gpa'),
      gpa_scale=request.args.get('gpa_scale'),
      converted_gpa=request.args.get('converted_gpa'))


@app.route('/index')
def index_get():
   global master_map
   global master_track_map
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
           #print("%s" % row)
       #print(master_prgrm)
       #print(master_id)
       master_map = dict(zip(master_prgrm, master_id))
       #print(master_map)
       ##########################################
       ####### DISPLAY MASTER PRGRM END #########
       ##########################################

       ##########################################
       ####### DISPLAY MASTER TRACK BEGIN #######
       ##########################################

       ## Creating a dictionary here - {programme1: [track1, track2, ...], programme2: [], ...}
       ## The idea is to read the keys as programmes and populate the tracks accordingly

       # sec_name = ["sec:mscArtificialIntelligence", "sec:mscBioinformaticsAndSystemsBiology", "sec:mscBusinessAnalytics",
       #          "sec:mscComputerScience", "sec:mscEconometricsAndOperationsResearch", "sec:mscGenesInBehaviourAndHealth", 
       #          "sec:mscInformationScience", "sec:mscLinguistic", "sec:mscMathematics", "sec:mscParallelDistributedComputerSystem",
       #          "sec:mscScienceBusinessInnovation", "sec:mscStochasticsAndFinancialMathematics"]

       # track_list = []

       # for item in sec_name:
       #     tracks = get_track(item)
       #     track_list.append(tracks)

       # master_track_map = dict(zip(master_prgrm, track_list))

       # get the selected master program
       # after getting the selected master program do something like this for ALL 12 programs.
       # if (selected_master == "MSc Artificial Intelligence"):
          # selected_master = "sec:mscArtificialIntelligence"
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
           #print("%s" % row)
       #print(english_test)
       ########################################
       ####### DISPLAY ENGLISH TEST END #######
       ########################################
       tracks=['select master program']
       knowledge = ['select track']

       return render_template('index.html', 
        master_map=master_map, 
        english_test=english_test, 
        tracks=tracks, 
        knowledge=knowledge)


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


# this method gets the selected master program, and updated the track menu accordingly
@app.route('/update_track_menu')
def update_track_menu():

    # the value of the first dropdown (selected by the user)
    selected_master = request.args.get('selected_master', type=str)
    print('selected master: ',selected_master)
           # master_id = ['ai', 'bsb', 'ba', 'cs', 'eoc', 'gbh', 'is', 'lgs', 'math', 'pdcs', 'sbi', 'sfm']

    updated_tracks = check_track(selected_master)
    print('track list: ', updated_tracks)

    # create the values in the dropdown as a html string
    html_string_selected = ''
    for entry in updated_tracks:
        html_string_selected += '<option value="{}">{}</option>'.format(entry, entry)

    return jsonify(html_string_selected=html_string_selected)

#######################################
####### POPULATE KNOWLEDGE LIST #######
#######################################
@app.route('/update_knowledge')
def update_knowledge():
  # gonna update knowledge here depending on selected track, once jquery is fixed
  print('wassup')
  selected_track = request.args.get('selected_track', type=str)
  print('selected_track: ', selected_track)

  updated_knowledge = check_knowledge(selected_track)

  print('knowledge list: ', updated_knowledge)
  html_string_selected = ''
  for entry in updated_knowledge:
      html_string_selected += '<label value="{}">{}</label>'.format(entry, entry)

  return jsonify(html_string_selected=html_string_selected)


###############################
####### CHECK TRACK ###########
###############################
def check_track(selected_master):
  if selected_master == 'math':
    selected_master = "sec:mscMathematics"
    updated_tracks = get_track(selected_master)
    return updated_tracks
  elif selected_master == 'ai':
    selected_master = "sec:mscArtificialIntelligence"
    updated_tracks = get_track(selected_master)
    return updated_tracks
  elif selected_master == 'cs':
    selected_master = "sec:mscComputerScience"
    updated_tracks = get_track(selected_master)
    return updated_tracks
  elif selected_master == 'ba':
    selected_master = "sec:mscBusinessAnalytics"
    updated_tracks = get_track(selected_master)
    return updated_tracks
  elif selected_master == 'bsb':
    selected_master = "sec:mscBioinformaticsAndSystemsBiology"
    updated_tracks = get_track(selected_master)
    return updated_tracks
  elif selected_master == 'eoc':
    selected_master = "sec:mscEconometricsAndOperationsResearch"
    updated_tracks = get_track(selected_master)
    return updated_tracks
  elif selected_master == 'gbh':
    selected_master = "sec:mscGenesInBehaviourAndHealth"
    updated_tracks = get_track(selected_master)
    return updated_tracks
  elif selected_master == 'is':
    selected_master = "sec:mscInformationScience"
    updated_tracks = get_track(selected_master)
    return updated_tracks
  elif selected_master == 'lgs':
    selected_master = "sec:mscLinguistic"
    updated_tracks = get_track(selected_master)
    return updated_tracks
  elif selected_master == 'pdcs':
    selected_master = "sec:mscParallelDistributedComputerSystem"
    updated_tracks = get_track(selected_master)
    return updated_tracks
  elif selected_master == 'sbi':
    selected_master = "sec:mscScienceBusinessInnovation"
    updated_tracks = get_track(selected_master)
    return updated_tracks
  elif selected_master == 'sfm':
    selected_master = "sec:mscStochasticsAndFinancialMathematics"
    updated_tracks = get_track(selected_master)
    return updated_tracks

###############################
####### CHECK KNOWLEDGE #######
###############################
def check_knowledge(selected_track):
  if selected_track == 'Cognitive Science':
    selected_track = "sec:cognitiveScience"
    selected_master = "sec:mscArtificialIntelligence"
    updated_knowledge = get_knowledge(selected_master, selected_track)
    return updated_knowledge
  elif selected_track == 'Artificial Intelligence':
    selected_track = "sec:artificialIntelligence"
    selected_master = "sec:mscArtificialIntelligence"
    updated_knowledge = get_knowledge(selected_master, selected_track)
    return updated_knowledge
  elif selected_track == 'Business Analytics':
    selected_track = "sec:businessAnalytics"
    selected_master = "sec:mscBusinessAnalytics"
    updated_knowledge = get_knowledge(selected_master, selected_track)
    return updated_knowledge
  elif selected_track == 'Big Data Engineering':
    selected_track = "sec:bigDataEngineering"
    selected_master = "sec:mscComputerScience"
    updated_knowledge = get_knowledge(selected_master, selected_track)
    return updated_knowledge
  elif selected_track == 'Computer Systems Security':
    selected_track = "sec:computerSystemsSecurity"
    selected_master = "sec:mscComputerScience"
    updated_knowledge = get_knowledge(selected_master, selected_track)
    return updated_knowledge
  elif selected_track == 'Foundations of Computing and Concurrency':
    selected_track = "sec:foundationsOfComputingAndConcurrency"
    selected_master = "sec:mscComputerScience"
    updated_knowledge = get_knowledge(selected_master, selected_track)
    return updated_knowledge
  elif selected_track == 'Internet and Web Technology':
    selected_track = "sec:internetAndWebTechnology"
    selected_master = "sec:mscComputerScience"
    updated_knowledge = get_knowledge(selected_master, selected_track)
    return updated_knowledge
  elif selected_track == 'Parallel Computing Systems':
    selected_track = "sec:parallelComputingSystems"
    selected_master = "sec:mscComputerScience"
    updated_knowledge = get_knowledge(selected_master, selected_track)
    return updated_knowledge
  elif selected_track == 'Software Engineering and Green IT':
    selected_track = "sec:softwareEngineeringAndGreenIT"
    selected_master = "sec:mscComputerScience"
    updated_knowledge = get_knowledge(selected_master, selected_track)
    return updated_knowledge
  elif selected_track == 'Econometrics and Data Science':
    selected_track = "sec:econometricsAndDataScience"
    selected_master = "sec:mscEconometricsAndOperationsResearch"
    updated_knowledge = get_knowledge(selected_master, selected_track)
    return updated_knowledge
  elif selected_track == 'Financial Engineering':
    selected_track = "sec:financialEngineering"
    selected_master = "sec:mscEconometricsAndOperationsResearch"
    updated_knowledge = get_knowledge(selected_master, selected_track)
    return updated_knowledge
  elif selected_track == 'Operations Research Theory':
    selected_track = "sec:operationsResearchTheory"
    selected_master = "sec:mscEconometricsAndOperationsResearch"
    updated_knowledge = get_knowledge(selected_master, selected_track)
    return updated_knowledge
  elif selected_track == 'Supply Chain Management':
    selected_track = "sec:supplyChainManagement"
    selected_master = "sec:mscEconometricsAndOperationsResearch"
    updated_knowledge = get_knowledge(selected_master, selected_track)
    return updated_knowledge
  elif selected_track == 'Research Master':
    selected_track = "sec:researchMaster"
    selected_master = "sec:mscGenesInBehaviourAndHealth"
    updated_knowledge = get_knowledge(selected_master, selected_track)
    return updated_knowledge
  elif selected_track == 'Information Science':
    selected_track = "sec:informationScience"
    selected_master = "sec:mscInformationScience"
    updated_knowledge = get_knowledge(selected_master, selected_track)
    return updated_knowledge
  elif selected_track == 'Text Mining':
    selected_track = "sec:textMining"
    selected_master = "sec:mscLinguistic"
    updated_knowledge = get_knowledge(selected_master, selected_track)
    return updated_knowledge
  elif selected_track == 'Mathematics':
    selected_track = "sec:mathematics"
    selected_master = "sec:mscMathematics"
    updated_knowledge = get_knowledge(selected_master, selected_track)
    return updated_knowledge
  elif selected_track == 'Science Business Innovation':
    selected_track = "sec:scienceBusinessInnovation"
    selected_master = "sec:mscScienceBusinessInnovation"
    updated_knowledge = get_knowledge(selected_master, selected_track)
    return updated_knowledge
  elif selected_track == 'Stochastics and Financial Mathematics':
    selected_track = "sec:stochasticsAndFinancialMathematics"
    selected_master = "sec:mscStochasticsAndFinancialMathematics"
    updated_knowledge = get_knowledge(selected_master, selected_track)
    return updated_knowledge





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
   print("\n--------------------------------------------------")
   print("| Quick access link: http://127.0.0.1:5000/index |")
   print("--------------------------------------------------\n")
   app.run(debug = True)
