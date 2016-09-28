import pyliburo

display2dlist = []
displaylist = []

collada_file = "F:\\kianwee_work\\smart\\may2016-oct2016\\pycollada_testout\\dae\\simple_case.dae"

cityobject_dict = pyliburo.collada2citygml.convert(collada_file)
#print cityobject_dict["plot"]
display2dlist.append(cityobject_dict["terrain"])
display2dlist.append(cityobject_dict["building"])
display2dlist.append(cityobject_dict["road"])
display2dlist.append(cityobject_dict["plot"])
colourlist = ["GREEN", "WHITE", "WHITE", "YELLOW"]
#display2dlist.append(cityobject_dict)
#colourlist = ["YELLOW"]
pyliburo.py3dmodel.construct.visualise(display2dlist, colourlist)