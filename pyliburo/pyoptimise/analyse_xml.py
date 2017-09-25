# ==================================================================================================
#
#    Copyright (c) 2016, Chen Kian Wee (chenkianwee@gmail.com)
#
#    This file is part of pyliburo
#
#    pyliburo is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    pyliburo is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Dexen.  If not, see <http://www.gnu.org/licenses/>.
#
# ==================================================================================================
from xml.dom.minidom import Node
import xml.dom.minidom
from xml.dom.minidom import Document
#================================================================================
#xml functions
#================================================================================
def get_childnode_values(node_name, parent_node):
    values = []
    for node in parent_node.getElementsByTagName(node_name):
        node_value = ""
        for cnode in node.childNodes:
            if cnode.nodeType == Node.TEXT_NODE:
                #in case the text node is separated 
                tvalue = str(cnode.nodeValue)
                node_value = node_value + tvalue
                
        values.append(node_value)
                
    return values

def get_childnode_attributes(node_name, parent_node, attribute_name):
    attributes = []
    for node in parent_node.getElementsByTagName(node_name):
        attributes.append(str(node.attributes[attribute_name].value))

    return attributes

def get_childnode_value(node_name, parent_node):
    nodes_list = parent_node.getElementsByTagName(node_name)
    num_nodes = len(nodes_list)
    
    if num_nodes > 1:
        raise Exception("more than one node!!")
    elif num_nodes == 0:
        raise Exception("no nodes!!")
    else:
        values = []
        for node in nodes_list:
            node_value = ""
            for cnode in node.childNodes:
                if cnode.nodeType == Node.TEXT_NODE:
                    #in case the text node is separated 
                    tvalue = str(cnode.nodeValue)
                    node_value = node_value + tvalue
            values.append(node_value)
            
    return values[0]

def edit_nodevalue(node_name, parent_node, change_value):
    nodes_list = parent_node.getElementsByTagName(node_name)
    num_nodes = len(nodes_list)
    
    if num_nodes > 1:
        raise Exception("more than one node!!")
    elif num_nodes == 0:
        raise Exception("no nodes!!")
    else:
        for node in nodes_list:
            for cnode in node.childNodes:
                if cnode.nodeType == Node.TEXT_NODE:
                    cnode.nodeValue = change_value
                    
def create_childnode(node_name, parent_node, value, doc):
    childnode = doc.createElement(node_name)
    value = doc.createTextNode(value)
    childnode.appendChild(value)
    parent_node.appendChild(childnode)

def create_xml_file(doc, ind, status):
    population = doc.getElementsByTagName("population")[0]
    #create the individual 
    individual = doc.createElement("individual")
    population.appendChild(individual)
    #create the identity
    create_childnode("identity", individual, str(ind.id), doc)
    #create the generation
    create_childnode("generation", individual, str(ind.generation), doc)
    #create the status
    create_childnode("status", individual, status, doc)
    #create input params
    inputparams = doc.createElement("inputparams")
    individual.appendChild(inputparams)
    #create inputparam
    #get all the genotype value
    for gen_value in ind.genotype.values:
        if isinstance(gen_value, float):
            create_childnode("inputparam", inputparams, str(round(gen_value, 5)),doc)
        elif isinstance(gen_value, int):
            create_childnode("inputparam", inputparams, str(gen_value),doc)
    #create derived params
    derivedparams = doc.createElement("derivedparams")
    individual.appendChild(derivedparams)
    #create derivedparam
    if len(ind.derivedparams.values) != 0:
        for derived_value in ind.derivedparams.values:
            create_childnode("derivedparam", derivedparams, str(derived_value), doc)
    #create scores
    scores = doc.createElement("scores")
    individual.appendChild(scores)
    #create score
    if ind.is_not_evaluated() == False:
        for score_value in ind.scores:
            create_childnode("score", scores, str(round(score_value, 3)),doc)
    return doc

def create_xml_individual(doc, identity, generation, status, genotype, ind_derivedparams, ind_scores ):
    #create the individual 
    individual = doc.createElement("individual")
    doc.appendChild(individual)
    #create the identity
    create_childnode("identity", individual, str(identity), doc)
    #create the generation
    create_childnode("generation", individual, str(generation), doc)
    #create the status
    create_childnode("status", individual, status, doc)
    #create input params
    inputparams = doc.createElement("inputparams")
    individual.appendChild(inputparams)
    #create inputparam
    #get all the genotype value
    for gen_value in genotype.values:
        if isinstance(gen_value, float):
            create_childnode("inputparam", inputparams, str(round(gen_value,5)),doc)
        elif isinstance(gen_value, int):
            create_childnode("inputparam", inputparams, str(gen_value),doc)
    #create derived params
    derivedparams = doc.createElement("derivedparams")
    individual.appendChild(derivedparams)
    #create derivedparam
    if len(ind_derivedparams.values) != 0:
        for derived_value in ind_derivedparams.values:
            create_childnode("derivedparam", derivedparams, str(round(derived_value,3)), doc)
    #create scores
    scores = doc.createElement("scores")
    individual.appendChild(scores)
    #create score
    if ind_scores.count(None) == 0:
        for score_value in ind_scores:
            create_childnode("score", scores, str(round(score_value,3)),doc)
    return doc
    
def get_score(ind):
    score_list = get_childnode_values("score", ind)
    score_list_f = []
    for score in score_list:
        score_list_f.append(float(score))
    return score_list_f
    
def get_inputparam(ind):
    input_list = get_childnode_values("inputparam", ind)
    input_list_f = []
    for inputx in input_list:
        input_list_f.append(float(inputx))
    return input_list_f

def get_derivedparam(ind):
    derived_list = get_childnode_values("derivedparam", ind)
    #derived_list_f = []
    #for derived in derived_list:
    #    derived_list_f.append(float(derived))
    return derived_list

def get_id(ind):
    identity = get_childnode_value("identity", ind)
    return identity

def get_inds_frm_xml(xml_filepath):
    doc = xml.dom.minidom.parse(xml_filepath)
    ind_list = doc.getElementsByTagName("individual")
    return ind_list

def write_inds_2_xml(inds, res_path):
    #write an xml file
    doc = Document()
    root_node = doc.createElement("data")
    doc.appendChild(root_node)
    population = doc.createElement("population")
    root_node.appendChild(population)

    doc = xml.dom.minidom.parseString("<data><population></population></data>")
    parent_node = doc.getElementsByTagName("population")[0]
    
    for ind_node in inds:
        parent_node.appendChild(ind_node)
        
    f = open(res_path,"w")
    f.write(doc.toxml())
    f.close()
    
def combine_xml_files(xmlfile1, xmlfile2, resxml_file):
    total_inds = []
    inds1 = get_inds_frm_xml(xmlfile1)
    inds2 = get_inds_frm_xml(xmlfile2)
    total_inds.extend(inds1)
    total_inds.extend(inds2)
    write_inds_2_xml(total_inds, resxml_file)

def rmv_unevaluated_inds(xmlfile):
    eval_inds = []
    inds = get_inds_frm_xml(xmlfile)
    for ind in inds:
        scorelist = get_score(ind)
        if scorelist:
            eval_inds.append(ind)
            
    write_inds_2_xml(eval_inds, xmlfile)
        
def dominates(result_list1, result_list2, min_max_list):
    equal = True
    score1 = result_list1
    score2 = result_list2
    num_scores = len(score1)
    for i in range(num_scores):
        #print ind1
        #print ind2
        val1 = score1[i]
        val2 = score2[i]
        if val1 != val2: equal = False
        if min_max_list[i] == 0:
            if val2 < val1:
                return False
        elif val2>val1:
            return False
    if equal: return False
    return True

def on_pareto_front(score_list, score_2dlist, min_max_list):
    for score_list2 in score_2dlist:
        if dominates(score_list2, score_list, min_max_list):
            return False
    return True
    
def extract_pareto_front(score_2dlist, min_max_list):
    pareto_front = []
    non_pareto_front = []
    for score_list in score_2dlist:
        if (len(score_list)-1) !=0:     
            if on_pareto_front(score_list, score_2dlist, min_max_list):
                pareto_front.append(score_list)
            else:
                non_pareto_front.append(score_list)
    return pareto_front, non_pareto_front

def c_measures (score_2dlist1,score_2dlist2, min_max_list):
    num_inds2 = len(score_2dlist2)
    ind_list = []
    for score_list2 in score_2dlist2:
        if not on_pareto_front(score_list2, score_2dlist1, min_max_list):
            #if it is not dominating means it is dominated
            ind_list.append(score_list2)
    
    num_dominated_inds = len(ind_list)
    print num_dominated_inds, num_inds2
    return float(num_dominated_inds)/float(num_inds2)

def minimise_score_4_hypervolume(score_list, min_max_list):
    score_list_f = []
    scnt = 0
    for score in score_list:
        min_max = min_max_list[scnt]
        if min_max == 1:
            score_new = float(score)*-1
        if min_max == 0:
            score_new = float(score)
        score_list_f.append(score_new)
        scnt = scnt + 1
    return score_list_f

def prepare_front_4_hypervolume(score_2dlist, min_max_list):
    front = []
    for score_list in score_2dlist:
        score_list = minimise_score_4_hypervolume(score_list,min_max_list)
        front.append(score_list)
    return front

def hyper_volume(score_2dlist, ref_pt, min_max_list):
    import hv
    hypervolume = hv.HyperVolume(ref_pt)
    min_front = prepare_front_4_hypervolume(score_2dlist, min_max_list)
    volume = hypervolume.compute(min_front)
    return volume
    

def inds_2_score_2dlist(inds):
    score_2dlist = []
    for ind in inds:
        scorelist = get_score(ind)
        score_2dlist.append(scorelist)
    return score_2dlist
        
def extract_pareto_front_inds(inds, min_max_list):
    '''
    min_max_list = [0,1]
    0 = minimise
    1 = maximise
    '''
    pareto_front = []
    non_pareto_front = []
    score_2dlist = inds_2_score_2dlist(inds)
    for ind in inds:
        score_list = get_score(ind)
        if (len(score_list)-1) !=0:     
            if on_pareto_front(score_list, score_2dlist, min_max_list):
                pareto_front.append(ind)
            else:
                non_pareto_front.append(ind)
    return pareto_front, non_pareto_front

def calc_min_max_range(data_2dlist):
    min_max_range = list()
    for m in zip(*data_2dlist):
        mn = min(m)
        mx = max(m)
        if mn == mx:
            mn -= 0.5
            mx = mn + 1.
        r  = float(mx - mn)
        min_max_range.append((mn, mx, r))
    return min_max_range

def normalise(data_2dlist):
    #data is in array [nsamples][dimensions]
    min_max_range = calc_min_max_range(data_2dlist)
    # Normalize the data sets
    norm_data_sets = list()
    #for ds in ind_score_list:
    for ds in data_2dlist:
        nds = [(value - min_max_range[dimension][0]) / 
                min_max_range[dimension][2] 
                for dimension,value in enumerate(ds)]
        norm_data_sets.append(nds)
        
    return norm_data_sets

def denormalise(data_2dlist, orig_data_2dlist):
    #data is in array [nsamples][dimensions]
    min_max_range = calc_min_max_range(orig_data_2dlist)
    denorm_2dlist = []
    for dx in data_2dlist:
        dx_ip_cnt = 0
        real_input_parm = []
        for dx_ip in dx:
            real_range = dx_ip*min_max_range[dx_ip_cnt][2]
            real_parm = min_max_range[dx_ip_cnt][0] + real_range
            real_input_parm.append(real_parm)
            dx_ip_cnt = dx_ip_cnt + 1
            
        denorm_2dlist.append(real_input_parm)
    return denorm_2dlist
    
def kmeans_inds(inds, attribs_2_cluster, n_clusters = None):
    from sklearn.cluster import KMeans
    import numpy as np
    
    #attribs_2_cluster =  "score", "inputparam", "derivedparam"  
    #read the inds and get the attribs ready for clustering
    ind_att_list = []
    for ind in inds:
        if attribs_2_cluster == "score":
            score_list = get_score(ind)
            ind_att_list.append(score_list)
        if attribs_2_cluster == "inputparam":
            input_list = get_inputparam(ind)
            ind_att_list.append(input_list)
        if attribs_2_cluster == "derivedparam":
            derived_list = get_derivedparam(ind)
            ind_att_list.append(derived_list)
            
    #process the data accordingly 
    #normalise the attributes
    normalised_ind_att_list = normalise(ind_att_list)
    X = np.array(normalised_ind_att_list)
    
    cluster_list = []
    if n_clusters == None:
        #do the elbow test 
        n_clusters = elbow_test(X, 6)
        
    k_means = KMeans(n_clusters=n_clusters)
    k_means.fit(X)
    k_means_labels = k_means.labels_
    k_means_labels_unique = np.unique(k_means_labels)
    
    for i in k_means_labels_unique:
        cluster_list.append([])
        cnt = 0
        for j in k_means_labels:
            if j == i:
                cluster_list[-1].append(inds[cnt])
            cnt = cnt + 1
        
    centroids = k_means.cluster_centers_
    denorm_centroids = denormalise(centroids, ind_att_list)
    result_dict = {}
    result_dict["cluster_list"] = cluster_list
    result_dict["centroids"] = denorm_centroids
    return result_dict
    
def kmeans(np_array, n_clusters):
    from sklearn.cluster import KMeans
    import numpy as np
    k_means = KMeans(n_clusters=n_clusters)
    k_means.fit(np_array)
    k_means_labels = k_means.labels_
    k_means_labels_unique = np.unique(k_means_labels)
    centroids = k_means.cluster_centers_
    cluster_list = []
    
    for i in k_means_labels_unique:
        cluster_list.append([])
        cnt = 0
        for j in k_means_labels:
            if j == i:
                cluster_list[-1].append(np_array[cnt])
            cnt = cnt + 1
            
    result_dict = {}
    result_dict["cluster_list"] = cluster_list
    result_dict["centroids"] = centroids
    return result_dict

#run through a series kmeans to determine the elbow
def elbow_test(X, max_cluster):
    from sklearn.cluster import KMeans
    from sklearn import metrics
    inertia_list = []
    s_list = []
    for cluster_cnt in range(max_cluster-1):
        k_means = KMeans(n_clusters=cluster_cnt+2)
        k_means.fit(X)
        k_means_labels = k_means.labels_
        s_factor = metrics.silhouette_score(X, k_means_labels, metric='euclidean')
        s_list.append(s_factor)
        kmeans_inertia = k_means.inertia_
        inertia_list.append(kmeans_inertia)

    inertia_cnt = 0
    i_diff_list = []
    for inertia in inertia_list:
        #look for the difference between each difference in cluster number
        if inertia_cnt != len(inertia_list) - 1:
            i_diff = inertia - inertia_list[inertia_cnt + 1]
            i_diff_list.append(i_diff)
        inertia_cnt = inertia_cnt + 1

    #find the biggest difference and use that number for the best number of cluster
    max_diff = max(i_diff_list)
    max_diff_index = i_diff_list.index(max_diff)
    #+3 because of the counting 
    best_no_cluster = max_diff_index + 3
    return best_no_cluster

def archetypal_analysis_inds(inds, attribs_2_cluster, max_archetypes, niter = 200):
    import numpy as np
    
    #attribs_2_cluster =  "score", "inputparam", "derivedparam"  
    #read the inds and get the attribs ready for clustering
    ind_att_list = []
    for ind in inds:
        if attribs_2_cluster == "score":
            score_list = get_score(ind)
            ind_att_list.append(score_list)
        if attribs_2_cluster == "inputparam":
            input_list = get_inputparam(ind)
            ind_att_list.append(input_list)
        if attribs_2_cluster == "derivedparam":
            derived_list = get_derivedparam(ind)
            ind_att_list.append(derived_list)
            
    #process the data accordingly 
    #normalise the attributes
    normalised_ind_att_list = normalise(ind_att_list)
    X = np.array(normalised_ind_att_list)
    A = X.T
    archetypes = archetypal_analysis(A, max_archetypes, niter = niter)
    denorm_archetypes = denormalise(archetypes, ind_att_list)
    return denorm_archetypes

def archetypal_analysis(np_array, max_archetypes, niter = 200):
    import pymf
    m = pymf.AA(np_array, num_bases=max_archetypes)
    #m.initialization()      
    m.factorize()
    data_t = np_array.T

    #find archetypes
    beta = m.beta
    beta_shape = beta.shape
    archetypes = []
    for k in range(beta_shape[0]):
        zk = 0
        for j in range(beta_shape[1]):
            z = beta[k][j]*data_t[j]
            zk = zk + z
        archetypes.append(zk)
    #f = m.ferr[-1]/(np_array.shape[0] + np_array.shape[1])
    return archetypes
