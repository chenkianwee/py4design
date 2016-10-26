import pyliburo

livexmlfile = "F:\\kianwee_work\\smart\\case_studies\\5x5ptblks\\nsga2_xml\\archive\\live.xml"
deadxmlfile = "F:\\kianwee_work\\smart\\case_studies\\5x5ptblks\\nsga2_xml\\archive\\dead.xml"
overallxmlfile = "F:\\kianwee_work\\smart\\case_studies\\5x5ptblks\\nsga2_xml\\archive\\overall.xml"
pyliburo.pyoptimise.analyse_xml.combine_xml_files(livexmlfile, deadxmlfile,overallxmlfile)
pyliburo.pyoptimise.analyse_xml.rmv_unevaluated_inds(overallxmlfile)

inds = pyliburo.pyoptimise.analyse_xml.get_inds_frm_xml(overallxmlfile)
pfront, nonpfront = pyliburo.pyoptimise.analyse_xml.extract_pareto_front(inds, [1,1])
pareto_pts = []
for pind in pfront:
    score_list = pyliburo.pyoptimise.analyse_xml.get_score(pind)
    pareto_pts.append(score_list)
    
npareto_pts = []
for upind in nonpfront:
    score_list = pyliburo.pyoptimise.analyse_xml.get_score(upind)
    npareto_pts.append(score_list)

pts2plot_2dlist = []
pts2plot_2dlist.append(pareto_pts)   
#pts2plot_2dlist.append(npareto_pts)

pyliburo.pyoptimise.draw_graph.scatter_plot(pts2plot_2dlist, [0.0,0.8])
print len(pts2plot_2dlist)
print len(pfront), len(nonpfront)