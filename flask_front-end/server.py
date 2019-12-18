from flask import (
    Flask,
    request,
    url_for,
    redirect,
    render_template,
    render_template_string,
    jsonify,
)
from rdflib import Graph
import sys
import io
import random
import inspect
import pdfkit

app = Flask(__name__)

ontology = "Ontology.ttl"
g = Graph()
g.parse(ontology, format="ttl")

master_map = {}
master_track_map = {}
updated_knowledge = []
selectedMaster = ""
selectedTrack = ""


############################################
############## RESULTS TO PDF ##############
############################################
def pdf():
    print("Trying to print")
    pdfkit.from_url("127.0.0.1:5000/result", "SEC Out.pdf")


############################################
####### GET TRACK LIST FROM ONTOLOGY #######
############################################
def get_track(degree_name):
    degree = degree_name
    track_list = []
    track_q_result = g.query(
        """select ?track_label where{
         VALUES ?masterdegree { """
        + degree
        + """ }
         ?masterdegree rdf:type sec:MasterDegree .
         ?masterdegree sec:hasTrack ?track .
         ?track rdfs:label ?track_label .
         FILTER (LANG(?track_label) = 'en')
      }order by ?track_label
      """
    )
    for row in track_q_result:
        track_list.append("%s" % row)
    track_list.insert(0, "Choose")

    return track_list


################################################
####### GET KNOWLEDGE LIST FROM ONTOLOGY #######
################################################
def get_knowledge(degree_name, track_name):
    global selectedMaster
    global selectedTrack

    selectedMaster = degree_name
    selectedTrack = track_name

    degree = degree_name
    trackname = track_name
    knowledge_list = []

    knowledge_q_result = g.query(
        """select ?knowledge_label where{
         VALUES ?masterdegree { """
        + degree
        + """ }
         VALUES ?track { """
        + trackname
        + """ }
         ?masterdegree sec:hasTrack ?track .
         ?track rdf:type sec:Track .
         ?track sec:requiresKnowledge ?knowledge .
         ?knowledge rdfs:label ?knowledge_label .
         FILTER (LANG(?knowledge_label) = 'en')
      }order by ?knowledge_label
      """
    )

    for row in knowledge_q_result:
        knowledge_list.append("%s" % row)

    return knowledge_list


###########################################
####### GET BACHELORS FROM ONTOLOGY #######
###########################################
def get_bachelor(degree_name, track_name):
    degree = degree_name
    trackname = track_name
    bachelor_list = []

    bachelor_q_result = g.query(
        """select ?bachelordegree_label where {
         VALUES ?masterdegree { """
        + degree
        + """ }
         VALUES ?track { """
        + trackname
        + """ }
         ?masterdegree rdf:type sec:MasterDegree .
         ?masterdegree sec:hasTrack ?track .
         ?track sec:requiresBachelorDegree ?bachelordegree .
         ?bachelordegree rdf:type sec:BachelorDegree .
         ?bachelordegree rdfs:label ?bachelordegree_label .
         FILTER (LANG(?bachelordegree_label)  = 'en')
      }order by ?bachelordegree_label
      """
    )

    for row in bachelor_q_result:
        bachelor_list.append("%s" % row)
    bachelor_list.insert(0, "Choose")
    bachelor_list.insert(1, "Other")

    return bachelor_list


############################################
# GET ENGLISH TEST THRESHOLD FROM ONTOLOGY #
############################################
def get_english_threshold(test_name):
    global selectedMaster
    global selectedTrack

    degree = selectedMaster
    trackname = selectedTrack
    test = test_name
    test_dict = {}

    print("Test_name: ", test)

    english_thresh_q_result = g.query(
        """select ?englishprof_label ?score where {
        VALUES ?master { """
        + degree
        + """ }
        VALUES ?track { """
        + trackname
        + """ }
   	    ?master sec:hasTrack ?track .
	    ?track rdf:type sec:Track .
	    ?track sec:requiresEnglishProf ?engprofquantity .
        ?engprofquantity sec:hasType ?englishprof .
        ?englishprof rdfs:label ?englishprof_label .
        FILTER (LANG(?englishprof_label)  = 'en')
        ?engprofquantity sec:hasScore ?score .
        }
        """
    )

    ### figure the quotes for rdfs label
    # english_thresh_q_result = g.query(
    # """select ?score where {
    #     VALUES ?master { """
    #    + degree
    #    + """ }
    #     VALUES ?track { """
    #    + trackname
    #    + """ }
    #    VALUES ?testname { """
    #   + " test "
    #   + """ }
    #     ?master sec:hasTrack ?track .
    #     ?track rdf:type sec:Track .
    #     ?track sec:requiresEnglishProf ?engprofquantity .
    # 	?engprofquantity sec:hasType ?englishprof .
    # 	?englishprof rdf:type sec:EnglishTest .
    # 	?englishprof rdfs:label ?testname @en .
    #    	?engprofquantity  sec:hasScore ?score .
    #     }
    # """
    # )

    print("Threshold results: ")
    for row in english_thresh_q_result:
        string = "%s_%s" % row
        string_list = string.split("_")
        test_dict[string_list[0]] = string_list[-1]

    print(test_dict)

    return test_dict[test]


@app.route("/result")
def result():
    return render_template(
        "result.html",
        selected_master=request.args.get("selected_master"),
        selected_track=request.args.get("selected_track"),
        gpa=request.args.get("gpa"),
        gpa_scale=request.args.get("gpa_scale"),
        converted_gpa=request.args.get("converted_gpa"),
        selected_bachelor=request.args.get("selected_bachelor"),
        selected_bachelor_type=request.args.get("selected_bachelor_type"),
        selected_native=request.args.get("selected_native"),
        eligibility_score=request.args.get("eligibility_score"),
        bachelor_score_comment=request.args.get("bachelor_score_comment"),
        bachelor_type_score_comment=request.args.get("bachelor_type_score_comment"),
        gpa_score_comment=request.args.get("gpa_score_comment"),
        work_ex_score_comment=request.args.get("work_ex_score_comment"),
        knowledge_score_comment=request.args.get("knowledge_score_comment"),
        english_score_comment=request.args.get("english_score_comment"),
    )

    pdf()


@app.route("/index")
def index_get():
    global master_map
    global master_track_map
    print("sup")
    if request.method == "GET":
        print("hiiii", file=sys.stdout)
        ##########################################
        ####### DISPLAY MASTER PRGRM BEGIN #######
        ##########################################
        master_q_result = g.query(
            """select ?master_label where {
           ?university rdf:type sec:University .
           ?university sec:hasMasterDegree ?master .
           ?master rdfs:label ?master_label .
           FILTER (LANG(?master_label ) = "en")
        }order by ?master_label"""
        )
        master_prgrm = []
        master_id = [
            "ai",
            "bsb",
            "ba",
            "cs",
            "eoc",
            "gbh",
            "is",
            "lgs",
            "math",
            "pdcs",
            "sbi",
            "sfm",
        ]
        for row in master_q_result:
            master_prgrm.append("%s" % row)
            # print("%s" % row)
        # print(master_prgrm)
        # print(master_id)
        master_map = dict(zip(master_prgrm, master_id))
        # print(master_map)
        ##########################################
        ####### DISPLAY MASTER PRGRM END #########
        ##########################################

        ##########################################
        ####### DISPLAY ENGLISH TEST BEGIN #######
        ##########################################
        english_q_result = g.query(
            """select ?englishtest_label where {
          ?englishtest rdf:type sec:EnglishTest .
          ?englishtest rdfs:label ?englishtest_label .
          FILTER (LANG(?englishtest_label)  = 'en')
        }"""
        )
        english_test = []
        for row in english_q_result:
            english_test.append("%s" % row)
            # print("%s" % row)
        # print(english_test)
        ########################################
        ####### DISPLAY ENGLISH TEST END #######
        ########################################
        tracks = ["select master program"]
        knowledge = ["select track"]
        bachelors = ["Other"]

        return render_template(
            "index.html",
            master_map=master_map,
            english_test=english_test,
            tracks=tracks,
            knowledge=knowledge,
            bachelors=bachelors,
        )


@app.route("/index", methods=["POST"])
def index_post():
    print("sup")
    global updated_knowledge
    if request.method == "POST":
        #########################
        ####### MASTER BEGIN #######
        #########################
        # master_id = ['ai', 'bsb', 'ba', 'cs', 'eoc', 'gbh', 'is', 'lgs', 'math', 'pdcs', 'sbi', 'sfm']
        selected_master = request.form.get("programme")
        if selected_master == "ai":
            selected_master = "MSc Artificial Intelligence"
        elif selected_master == "cs":
            selected_master = "MSc Computer Science"
        elif selected_master == "ba":
            selected_master = "MSc Business Analytics"
        elif selected_master == "is":
            selected_master = "MSc Information Science"
        elif selected_master == "bsb":
            selected_master = "MSc Bioinformatics & Systems Biology"
        elif selected_master == "eoc":
            selected_master = "MSc Econometrics and Operations Research"
        elif selected_master == "gbh":
            selected_master = "MSc Genes In Behaviour and Health"
        elif selected_master == "lgs":
            selected_master = "MSc Linguistics"
        elif selected_master == "math":
            selected_master = "MSc Mathematics"
        elif selected_master == "pdcs":
            selected_master = "MSc Parallel Distributed Computer Systems"
        elif selected_master == "sbi":
            selected_master = "MSc Science Business Innovation"
        elif selected_master == "sfm":
            selected_master = "MSc Stochastics & Financial Mathematics"

        ##############################
        ######### TRACK BEGIN ########
        ##############################

        selected_track = request.form.get("tracks")

        ##############################
        ####### BACHELOR BEGIN #######
        ##############################

        selected_bachelor = request.form.get("bachelors")
        print("Selected Bachelor:", selected_bachelor)

        ##############################
        #### BACHELOR TYPE BEGIN #####
        ##############################

        selected_bachelor_type = request.form.get("btype")
        print("Selected Bachelor type:", selected_bachelor_type)

        ##############################
        ########## GPA BEGIN #########
        ##############################
        grading_scale = {"usa": "0-4", "ind": "0-10"}
        gpa_scale = request.form.get("gpascale")
        print("selected GPA scale:", gpa_scale)
        gpa = request.form.get("gpa")
        gpa = float(gpa)
        print("GPA:", gpa)
        converted_gpa = 0
        #####check for grading scale
        if gpa_scale in grading_scale["usa"]:
            # print('usa conversion')
            ###calls us to uk gpa conversion
            calc_us_gpa = us_to_uk(gpa)
            print(calc_us_gpa)
            converted_gpa = calc_us_gpa
        else:
            print("carrying india to us conversion first")
            ###converts indian gpa to usa gpa first
            usa_gpa = ind_to_us(gpa)
            # print(usa_gpa)
            ###converts us gpa to uk gpa
            calc_ind_gpa = us_to_uk(usa_gpa)
            print(calc_ind_gpa)
            converted_gpa = calc_ind_gpa

        ##############################
        #### NATIVE ENGLISH BEGIN ####
        ##############################
        selected_native = request.form.get("native")
        print("Native speaker: ", selected_native)

        ############################
        #### ENGLISH TEST BEGIN ####
        ############################
        selected_engtest = request.form.get("englishtest")
        print("English test: ", selected_engtest)
        selected_eng_score = request.form.get("etest")
        print("English score: ", selected_eng_score)

        ############################
        #####  WORK EXP. BEGIN #####
        ############################
        selected_work = request.form.get("work")
        print("Work exp: ", selected_work)

        ############################
        #####  KNOWLEDGE BEGIN #####
        ############################
        selected_knowledge = request.form.getlist("knowledge")
        print("Knowledge: ", selected_knowledge)

        ############################
        ## FINAL ELIGIBILITY SCORE #
        ############################

        # Bachelor's course selection score [5% weight]
        if selected_bachelor == "Other":
            bachelor_score = 0.0
            bachelor_score_comment = "(Your background differs from the ones preferred)"
        else:
            bachelor_score = 5.0
            bachelor_score_comment = ""

        # Bachelor's - Research or not - score [40% weight]
        if selected_bachelor_type == "Yes":
            bachelor_type_score = 40.0
            bachelor_type_score_comment = ""
        else:
            bachelor_type_score = 0.0
            bachelor_type_score_comment = "(You lack experience in research)"

        # Bachelor's GPA - score [5% weight]
        if converted_gpa >= 65.00:
            gpa_score = 5.0
            gpa_score_comment = ""
        else:
            gpa_score = 0.0
            gpa_score_comment = "(You do not meet the minimum GPA requirements)"

        # English language proficiency score [5% weight]
        if selected_native == "Yes":
            english_score = 5.0
        elif selected_engtest == "IELTS":
            selected_eng_thresh = float(get_english_threshold(selected_engtest))
            if (
                (float(selected_eng_score) < selected_eng_thresh)
                and (float(selected_eng_score) >= 0.0)
                and (float(selected_eng_score) <= 9.0)
            ):
                english_score = 0.0
                english_score_comment = "English Language: You do not meet the English language requirements"
            elif (
                (float(selected_eng_score) >= selected_eng_thresh)
                and (float(selected_eng_score) >= 0.0)
                and (float(selected_eng_score) <= 9.0)
            ):
                english_score = 5.0
                english_score_comment = ""
            else:
                english_score = 0.0
                english_score_comment = "Invalid score"
        elif selected_engtest == "TOEFL Internet Based":
            selected_eng_thresh = int(get_english_threshold(selected_engtest))
            if (
                (int(selected_eng_score) < selected_eng_thresh)
                and (int(selected_eng_score) >= 0)
                and (int(selected_eng_score) <= 120)
            ):
                english_score = 0.0
                english_score_comment = "English Language: You do not meet the English language requirements"
            elif (
                (int(selected_eng_score) >= selected_eng_thresh)
                and (int(selected_eng_score) >= 0)
                and (int(selected_eng_score) <= 120)
            ):
                english_score = 5.0
                english_score_comment = ""
            else:
                english_score = 0.0
                english_score_comment = "Invalid score"
        elif selected_engtest == "TOEFL Paper Based":
            selected_eng_thresh = int(get_english_threshold(selected_engtest))
            if (
                (int(selected_eng_score) < selected_eng_thresh)
                and (int(selected_eng_score) >= 310)
                and (int(selected_eng_score) <= 677)
            ):
                english_score = 0.0
                english_score_comment = "English Language: You do not meet the English language requirements"
            elif (
                (int(selected_eng_score) >= selected_eng_thresh)
                and (int(selected_eng_score) >= 310)
                and (int(selected_eng_score) <= 677)
            ):
                english_score = 5.0
                english_score_comment = ""
            else:
                english_score = 0.0
                english_score_comment = "Invalid score"
        elif selected_engtest == "VU-Test English Language Proficiency":
            selected_eng_thresh = int(get_english_threshold(selected_engtest))
            if (
                (int(selected_eng_score) < selected_eng_thresh)
                and (int(selected_eng_score) >= 310)
                and (int(selected_eng_score) <= 677)
            ):
                english_score = 0.0
                english_score_comment = "English Language: You do not meet the English language requirements"
            elif (
                (int(selected_eng_score) >= selected_eng_thresh)
                and (int(selected_eng_score) >= 310)
                and (int(selected_eng_score) <= 677)
            ):
                english_score = 5.0
                english_score_comment = ""
            else:
                english_score = 0.0
                english_score_comment = "Invalid score"
        elif selected_engtest == "Cambridge Certificate in Advanced English":
            selected_eng_thresh = get_english_threshold(selected_engtest)
            scoreA = 3
            scoreB = 2
            scoreC = 1
            scoreVal = 0
            scoreThresh = 0

            if selected_eng_score == "A":
                scoreVal = scoreA
            elif selected_eng_score == "B":
                scoreVal = scoreB
            elif selected_eng_score == "C":
                scoreVal = scoreC
            else:
                scoreVal = 0

            if selected_eng_thresh == "A":
                scoreThresh = scoreA
            elif selected_eng_thresh == "B":
                scoreThresh = scoreB
            elif selected_eng_thresh == "C":
                scoreThresh = scoreC
            else:
                scoreThresh = 0

            if scoreVal >= scoreThresh:
                english_score = 5.0
                english_score_comment = ""
            else:
                english_score = 0.0
                english_score_comment = "English Language: You do not meet the English language requirements"
        elif selected_engtest == "Cambridge Certificate of Proficiency in English":
            selected_eng_thresh = get_english_threshold(selected_engtest)
            scoreA = 3
            scoreB = 2
            scoreC = 1
            scoreVal = 0
            scoreThresh = 0

            if selected_eng_score == "A":
                scoreVal = scoreA
            elif selected_eng_score == "B":
                scoreVal = scoreB
            elif selected_eng_score == "C":
                scoreVal = scoreC

            if selected_eng_thresh == "A":
                scoreThresh = scoreA
            elif selected_eng_thresh == "B":
                scoreThresh = scoreB
            elif selected_eng_thresh == "C":
                scoreThresh = scoreC

            if scoreVal >= scoreThresh:
                english_score = 5.0
                english_score_comment = ""
            else:
                english_score = 0.0
                english_score_comment = "English Language: You do not meet the English language requirements"

        # Work experience score [5% weight]
        if (selected_work == "2 years") or (selected_work == "more 2 years"):
            work_ex_score = 5.0
            work_ex_score_comment = "Work Experience: Your work experience might have a positive inflience on your admit decision"
        else:
            work_ex_score = 0.0
            work_ex_score_comment = ""

        # Knowledge score [40% weight]
        total_knowledge_items = len(updated_knowledge)
        selected_knowledge_items = len(selected_knowledge)
        individual_item_weight = 40.0 / total_knowledge_items
        knowledge_score = individual_item_weight * selected_knowledge_items

        if knowledge_score < 24.0:  # Considering 60% knowledge as the threshold
            knowledge_score_comment = (
                "Knowledge: You lack most of the knowledge required for this programme"
            )
        else:
            knowledge_score_comment = ""

        # Eligibility score
        eligibility_score = round(
            bachelor_score
            + bachelor_type_score
            + gpa_score
            + work_ex_score
            + knowledge_score
        )

        print(converted_gpa)
        return redirect(
            url_for(
                "result",
                selected_master=selected_master,
                selected_track=selected_track,
                gpa=gpa,
                gpa_scale=gpa_scale,
                converted_gpa=converted_gpa,
                selected_bachelor=selected_bachelor,
                selected_bachelor_type=selected_bachelor_type,
                selected_native=selected_native,
                eligibility_score=eligibility_score,
                bachelor_score_comment=bachelor_score_comment,
                bachelor_type_score_comment=bachelor_type_score_comment,
                gpa_score_comment=gpa_score_comment,
                work_ex_score_comment=work_ex_score_comment,
                knowledge_score_comment=knowledge_score_comment,
                english_score_comment=english_score_comment,
            )
        )


# this method gets the selected master program, and updated the track menu accordingly
@app.route("/update_track_menu")
def update_track_menu():
    # the value of the first dropdown (selected by the user)
    selected_master = request.args.get("selected_master", type=str)
    print("selected master: ", selected_master)
    # master_id = ['ai', 'bsb', 'ba', 'cs', 'eoc', 'gbh', 'is', 'lgs', 'math', 'pdcs', 'sbi', 'sfm']

    updated_tracks = check_track(selected_master)
    print("track list: ", updated_tracks)

    # create the values in the dropdown as a html string
    html_string_selected = ""
    for entry in updated_tracks:
        html_string_selected += '<option value="{}">{}</option>'.format(entry, entry)

    return jsonify(html_string_selected=html_string_selected)


#######################################
####### POPULATE KNOWLEDGE LIST #######
#######################################
@app.route("/update_knowledge")
def update_knowledge():
    # gonna update knowledge here depending on selected track, once jquery is fixed
    print("wassup")
    global updated_knowledge
    selected_track = request.args.get("selected_track", type=str)
    print("selected_track: ", selected_track)

    updated_knowledge = check_knowledge_or_bachelor(selected_track)

    print("knowledge list: ", updated_knowledge)
    html_string_selected = ""
    for entry in updated_knowledge:
        html_string_selected += '<input type="checkbox" name="knowledge" value="{}">{}</br>'.format(
            entry, entry
        )

    return jsonify(html_string_selected=html_string_selected)


#######################################
####### POPULATE BACHELOR LIST ########
#######################################
@app.route("/update_bachelor")
def update_bachelor():
    # gonna update knowledge here depending on selected track, once jquery is fixed
    # selected_master = request.args.get('selected_master', type=str)
    selected_track = request.args.get("selected_track", type=str)

    updated_bachelor = check_knowledge_or_bachelor(selected_track)

    print("bachelors list: ", updated_bachelor)
    html_string_selected = ""
    for entry in updated_bachelor:
        html_string_selected += '<option value="{}">{}</option>'.format(entry, entry)

    return jsonify(html_string_selected=html_string_selected)


###############################
######## CHECK TRACK ##########
###############################
def check_track(selected_master):
    if selected_master == "math":
        selected_master = "sec:mscMathematics"
        updated_tracks = get_track(selected_master)
        return updated_tracks
    elif selected_master == "ai":
        selected_master = "sec:mscArtificialIntelligence"
        updated_tracks = get_track(selected_master)
        return updated_tracks
    elif selected_master == "cs":
        selected_master = "sec:mscComputerScience"
        updated_tracks = get_track(selected_master)
        return updated_tracks
    elif selected_master == "ba":
        selected_master = "sec:mscBusinessAnalytics"
        updated_tracks = get_track(selected_master)
        return updated_tracks
    elif selected_master == "bsb":
        selected_master = "sec:mscBioinformaticsAndSystemsBiology"
        updated_tracks = get_track(selected_master)
        return updated_tracks
    elif selected_master == "eoc":
        selected_master = "sec:mscEconometricsAndOperationsResearch"
        updated_tracks = get_track(selected_master)
        return updated_tracks
    elif selected_master == "gbh":
        selected_master = "sec:mscGenesInBehaviourAndHealth"
        updated_tracks = get_track(selected_master)
        return updated_tracks
    elif selected_master == "is":
        selected_master = "sec:mscInformationScience"
        updated_tracks = get_track(selected_master)
        return updated_tracks
    elif selected_master == "lgs":
        selected_master = "sec:mscLinguistic"
        updated_tracks = get_track(selected_master)
        return updated_tracks
    elif selected_master == "pdcs":
        selected_master = "sec:mscParallelDistributedComputerSystem"
        updated_tracks = get_track(selected_master)
        return updated_tracks
    elif selected_master == "sbi":
        selected_master = "sec:mscScienceBusinessInnovation"
        updated_tracks = get_track(selected_master)
        return updated_tracks
    elif selected_master == "sfm":
        selected_master = "sec:mscStochasticsAndFinancialMathematics"
        updated_tracks = get_track(selected_master)
        return updated_tracks


##########################################
####### CHECK KNOWLEDGE & BACHELOR #######
##########################################
def check_knowledge_or_bachelor(selected_track):
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)
    print("caller name:", calframe[1][3])
    if calframe[1][3] == "update_track_menu":
        test()
    if selected_track == "Cognitive Science":
        selected_track = "sec:cognitiveScience"
        selected_master = "sec:mscArtificialIntelligence"
        if calframe[1][3] == "update_knowledge":
            updated_knowledge = get_knowledge(selected_master, selected_track)
            return updated_knowledge
        elif calframe[1][3] == "update_bachelor":
            updated_bachelor = get_bachelor(selected_master, selected_track)
            return updated_bachelor
    elif selected_track == "Artificial Intelligence":
        selected_track = "sec:artificialIntelligence"
        selected_master = "sec:mscArtificialIntelligence"
        if calframe[1][3] == "update_knowledge":
            updated_knowledge = get_knowledge(selected_master, selected_track)
            return updated_knowledge
        elif calframe[1][3] == "update_bachelor":
            updated_bachelor = get_bachelor(selected_master, selected_track)
            return updated_bachelor
    elif selected_track == "Business Analytics":
        selected_track = "sec:businessAnalytics"
        selected_master = "sec:mscBusinessAnalytics"
        if calframe[1][3] == "update_knowledge":
            updated_knowledge = get_knowledge(selected_master, selected_track)
            return updated_knowledge
        elif calframe[1][3] == "update_bachelor":
            updated_bachelor = get_bachelor(selected_master, selected_track)
            return updated_bachelor
    elif selected_track == "Big Data Engineering":
        selected_track = "sec:bigDataEngineering"
        selected_master = "sec:mscComputerScience"
        if calframe[1][3] == "update_knowledge":
            updated_knowledge = get_knowledge(selected_master, selected_track)
            return updated_knowledge
        elif calframe[1][3] == "update_bachelor":
            updated_bachelor = get_bachelor(selected_master, selected_track)
            return updated_bachelor
    elif selected_track == "Computer Systems Security":
        selected_track = "sec:computerSystemsSecurity"
        selected_master = "sec:mscComputerScience"
        if calframe[1][3] == "update_knowledge":
            updated_knowledge = get_knowledge(selected_master, selected_track)
            return updated_knowledge
        elif calframe[1][3] == "update_bachelor":
            updated_bachelor = get_bachelor(selected_master, selected_track)
            return updated_bachelor
    elif selected_track == "Foundations of Computing and Concurrency":
        selected_track = "sec:foundationsOfComputingAndConcurrency"
        selected_master = "sec:mscComputerScience"
        if calframe[1][3] == "update_knowledge":
            updated_knowledge = get_knowledge(selected_master, selected_track)
            return updated_knowledge
        elif calframe[1][3] == "update_bachelor":
            updated_bachelor = get_bachelor(selected_master, selected_track)
            return updated_bachelor
    elif selected_track == "Internet and Web Technology":
        selected_track = "sec:internetAndWebTechnology"
        selected_master = "sec:mscComputerScience"
        if calframe[1][3] == "update_knowledge":
            updated_knowledge = get_knowledge(selected_master, selected_track)
            return updated_knowledge
        elif calframe[1][3] == "update_bachelor":
            updated_bachelor = get_bachelor(selected_master, selected_track)
            return updated_bachelor
    elif selected_track == "Parallel Computing Systems":
        selected_track = "sec:parallelComputingSystems"
        selected_master = "sec:mscComputerScience"
        if calframe[1][3] == "update_knowledge":
            updated_knowledge = get_knowledge(selected_master, selected_track)
            return updated_knowledge
        elif calframe[1][3] == "update_bachelor":
            updated_bachelor = get_bachelor(selected_master, selected_track)
            return updated_bachelor
    elif selected_track == "Software Engineering and Green IT":
        selected_track = "sec:softwareEngineeringAndGreenIT"
        selected_master = "sec:mscComputerScience"
        if calframe[1][3] == "update_knowledge":
            updated_knowledge = get_knowledge(selected_master, selected_track)
            return updated_knowledge
        elif calframe[1][3] == "update_bachelor":
            updated_bachelor = get_bachelor(selected_master, selected_track)
            return updated_bachelor
    elif selected_track == "Econometrics and Data Science":
        selected_track = "sec:econometricsAndDataScience"
        selected_master = "sec:mscEconometricsAndOperationsResearch"
        if calframe[1][3] == "update_knowledge":
            updated_knowledge = get_knowledge(selected_master, selected_track)
            return updated_knowledge
        elif calframe[1][3] == "update_bachelor":
            updated_bachelor = get_bachelor(selected_master, selected_track)
            return updated_bachelor
    elif selected_track == "Financial Engineering":
        selected_track = "sec:financialEngineering"
        selected_master = "sec:mscEconometricsAndOperationsResearch"
        if calframe[1][3] == "update_knowledge":
            updated_knowledge = get_knowledge(selected_master, selected_track)
            return updated_knowledge
        elif calframe[1][3] == "update_bachelor":
            updated_bachelor = get_bachelor(selected_master, selected_track)
            return updated_bachelor
    elif selected_track == "Operations Research Theory":
        selected_track = "sec:operationsResearchTheory"
        selected_master = "sec:mscEconometricsAndOperationsResearch"
        if calframe[1][3] == "update_knowledge":
            updated_knowledge = get_knowledge(selected_master, selected_track)
            return updated_knowledge
        elif calframe[1][3] == "update_bachelor":
            updated_bachelor = get_bachelor(selected_master, selected_track)
            return updated_bachelor
    elif selected_track == "Supply Chain Management":
        selected_track = "sec:supplyChainManagement"
        selected_master = "sec:mscEconometricsAndOperationsResearch"
        if calframe[1][3] == "update_knowledge":
            updated_knowledge = get_knowledge(selected_master, selected_track)
            return updated_knowledge
        elif calframe[1][3] == "update_bachelor":
            updated_bachelor = get_bachelor(selected_master, selected_track)
            return updated_bachelor
    elif selected_track == "Research Master":
        selected_track = "sec:researchMaster"
        selected_master = "sec:mscGenesInBehaviourAndHealth"
        if calframe[1][3] == "update_knowledge":
            updated_knowledge = get_knowledge(selected_master, selected_track)
            return updated_knowledge
        elif calframe[1][3] == "update_bachelor":
            updated_bachelor = get_bachelor(selected_master, selected_track)
            return updated_bachelor
    elif selected_track == "Information Sciences":
        selected_track = "sec:informationScience"
        selected_master = "sec:mscInformationScience"
        if calframe[1][3] == "update_knowledge":
            updated_knowledge = get_knowledge(selected_master, selected_track)
            return updated_knowledge
        elif calframe[1][3] == "update_bachelor":
            updated_bachelor = get_bachelor(selected_master, selected_track)
            return updated_bachelor
    elif selected_track == "Text Mining":
        selected_track = "sec:textMining"
        selected_master = "sec:mscLinguistic"
        if calframe[1][3] == "update_knowledge":
            updated_knowledge = get_knowledge(selected_master, selected_track)
            return updated_knowledge
        elif calframe[1][3] == "update_bachelor":
            updated_bachelor = get_bachelor(selected_master, selected_track)
            return updated_bachelor
    elif selected_track == "Mathematics":
        selected_track = "sec:mathematics"
        selected_master = "sec:mscMathematics"
        if calframe[1][3] == "update_knowledge":
            updated_knowledge = get_knowledge(selected_master, selected_track)
            return updated_knowledge
        elif calframe[1][3] == "update_bachelor":
            updated_bachelor = get_bachelor(selected_master, selected_track)
            return updated_bachelor
    elif selected_track == "Science Business Innovation":
        selected_track = "sec:scienceBusinessInnovation"
        selected_master = "sec:mscScienceBusinessInnovation"
        if calframe[1][3] == "update_knowledge":
            updated_knowledge = get_knowledge(selected_master, selected_track)
            return updated_knowledge
        elif calframe[1][3] == "update_bachelor":
            updated_bachelor = get_bachelor(selected_master, selected_track)
            return updated_bachelor
    elif selected_track == "Stochastics and Financial Mathematics":
        selected_track = "sec:stochasticsAndFinancialMathematics"
        selected_master = "sec:mscStochasticsAndFinancialMathematics"
        if calframe[1][3] == "update_knowledge":
            updated_knowledge = get_knowledge(selected_master, selected_track)
            return updated_knowledge
        elif calframe[1][3] == "update_bachelor":
            updated_bachelor = get_bachelor(selected_master, selected_track)
            return updated_bachelor
    elif selected_track == "Bioinformatics and Systems Biology":
        selected_track = "sec:bioinformaticsAndSystemsBiology"
        selected_master = "sec:mscBioinformaticsAndSystemsBiology"
        if calframe[1][3] == "update_knowledge":
            updated_knowledge = get_knowledge(selected_master, selected_track)
            return updated_knowledge
        elif calframe[1][3] == "update_bachelor":
            updated_bachelor = get_bachelor(selected_master, selected_track)
            return updated_bachelor
    elif selected_track == "Parallel Distributed Computer Systems":
        selected_track = "sec:parallelDistributedComputerSystem"
        selected_master = "sec:mscParallelDistributedComputerSystem"
        if calframe[1][3] == "update_knowledge":
            updated_knowledge = get_knowledge(selected_master, selected_track)
            return updated_knowledge
        elif calframe[1][3] == "update_bachelor":
            updated_bachelor = get_bachelor(selected_master, selected_track)
            return updated_bachelor


#####converts us gpa to uk gpa
def us_to_uk(score):
    print("comes into the conversion")
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
        print("3.7")
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


if __name__ == "__main__":
    print("\n--------------------------------------------------")
    print("| Quick access link: http://127.0.0.1:5000/index |")
    print("--------------------------------------------------\n")
    app.run(debug=True)
