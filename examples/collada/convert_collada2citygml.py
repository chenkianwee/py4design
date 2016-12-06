import pyliburo

display2dlist = []
displaylist = []

dae_file = "F:\\kianwee_work\\smart\\may2016-oct2016\\pycollada_testout\\dae\\simple_case.dae"
dae_file = "F:\\kianwee_work\\smart\\journal\\mdpi_sustainability\\case_study\\dae\\grid_tower.dae"
cityobject_dict = pyliburo.collada2citygml.convert(dae_file)
#print cityobject_dict["plot"]
display2dlist.append(cityobject_dict["terrain"])
display2dlist.append(cityobject_dict["building"])
display2dlist.append(cityobject_dict["road"])
display2dlist.append(cityobject_dict["plot"])
colourlist = ["GREEN", "WHITE", "WHITE", "YELLOW"]
#display2dlist.append(cityobject_dict)
#colourlist = ["YELLOW"]
pyliburo.py3dmodel.construct.visualise(display2dlist, colourlist)