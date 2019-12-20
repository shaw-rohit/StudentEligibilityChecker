import rdflib

g = rdflib.Graph()
g.parse("D:/Amsterdam/VU/KE2019/StudentEligibilityChecker/datamodel/StudentEligibilityChecker.ttl", format='turtle')

qres = g.query(
    """select ?master_label where {
        ?university rdf:type sec:University .
	    ?university sec:hasMasterDegree ?master .
        ?master rdfs:label ?master_label .
        FILTER (LANG(?master_label ) = "en")
    }""")

for row in qres:
    print("%s" % row)
