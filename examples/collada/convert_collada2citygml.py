import pyliburo

display2dlist = []
displaylist = []

collada_file = "F:\\kianwee_work\\smart\\may2016-oct2016\\pycollada_testout\\dae\\3plots_n_roads.dae"
cityobject_dict = pyliburo.collada2citygml.convert(collada_file)

display2dlist.append(cityobject_dict["terrain"])
display2dlist.append(cityobject_dict["building"])
display2dlist.append(cityobject_dict["road"])
display2dlist.append(cityobject_dict["plot"])
colourlist = ["GREEN", "WHITE", "WHITE", "YELLOW"]
pyliburo.py3dmodel.construct.visualise(display2dlist, colourlist)