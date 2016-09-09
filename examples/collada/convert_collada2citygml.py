import pyliburo

display2dlist = []
displaylist = []

collada_file = "F:\\kianwee_work\\smart\\may2016-oct2016\\pycollada_testout\\dae\\plot_n_3buildings_terrain.dae"
ssdict = pyliburo.collada2citygml.convert(collada_file)

    
display2dlist.append(ssdict) #[0:531])
colourlist = ["WHITE"]
pyliburo.py3dmodel.construct.visualise(display2dlist, colourlist)