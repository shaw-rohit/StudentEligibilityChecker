# Student Eligibility Checker

Students often spend a lot of money on university applications not knowing if they are eligible for the programme or not. We built an application that assesses eligibility requirements for a specific degree programme at a university before students send in their application, saving both money and time. 

## What the Student Eligibility Checker does?

The Student Eligibility Checker gets user inputs like the masters they want to apply for ,the candidate's GPA, information about their Bachelors, etc. and uses the input to populate an eligibility score. This eligibility score shows the user whether he is eligible or not for the program he wants to apply for.

## Workflow of Student Eligibility Checker:

The system works on an Ontology driven decision making approach. It is configured only to work for courses offered at the ```Vrije Universiteit Amsterdam``` at this point of time. All the information about the courses is stored in the ontology and all the important criterias required for the decision making is also kept in the ontology. This ensures that the ontology forms the heart of the system and the user inputs are used to compare with the ontology to arrive at a decision. 

1) Input: User values - GPA, preferred choice of masters, previous education details, english test scores etc.<br>
2) Decision Making: Ontology - contains the data about the courses and the eligibility criterias.<br>
3) Output: A Eligibility Score -  High eligibility score means the person is eligible for the course and vice versa

## Starting the Student Eligibility Checker System:

The system is basically a ```Website``` built using ```HTML and other frontend technologies like CSS,JQUERY and Javascript```. The website is hosted on a local server using ```Python's Flask Framework```. Python is used to establish the connection between the Website and the ontology. The ontology is a .ttl file and its being queried using ```SPARQL```.

1) Download the repository and extract the contents to a folder.
2) Navigate to the repository location in the command line.
3) Ensure that Flask and rdflib packages are installed in your location using the following commands: <br>
<pre>                            pip install flask                                                       </pre>
<pre>                            pip install rdflib                                                      </pre><br> 
4) To start hosting the server, follow the below command.<br>
<pre>                            python server.py                                                        </pre>
5) Once the script is executed, Go to the following link to start using the Student Eligibility checker:<http://127.0.0.1:5000/index>
6) Now the server and the system are up and running. Try your hands at the Student Eligibility cheecker and save time and money!!



_A project built for the course Knowledge Engineering at Vrije Universiteit Amsterdam._
