# ==================================================================================================
#
#    Copyright (c) 2016, Chen Kian Wee (chenkianwee@gmail.com)
#
#    This file is part of py4design
#
#    py4design is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    py4design is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with py4design.  If not, see <http://www.gnu.org/licenses/>.
#
# ==================================================================================================
"""
Pyoptimise
================================================
Documentation is available in the docstrings and online at ....

Submodules
-----------
::
    
 analyse_xml                  --- Functions for analysing the generated xml from the optimisation.
                                  dependencies: scipy, numpy, scikit-learn, pymf
 draw_graph                   --- Functions for drawing graphs.
                                  dependencies: matplotlib
 nsga2                        --- Classes and functions for performing NSGA2 optimisation.
"""
import nsga2
import analyse_xml
import draw_graph

def empty_xml_files(xml_filelist):
    """
    This function empties all the xml files.
    
    Parameters
    ----------
    xml_filelist : list of str
        The list of xml files to be emptied.
        
    """
    for xmlf in xml_filelist:
        open(xmlf,"w").close()
        
def create_nsga2_population_class(gene_dict_list, score_dict_list, mutation_rate,crossover_rate,init_population,
          live_file,dead_file):
    
    """
    This function creates a population class.
    
    Parameters
    ----------
    gene_dict_list : list of dictionaries
        Each dictionary contains the parameters for creating a Gene class instance. Each dictionay is in this format: {"type": "int_range", "range": (0,4,1)}.
        
    score_dict_list : list of dictionaries
        Each dictionary contains the parameters for creating a ScoreMeta class instance. Each dictionay is in this format: {"name": "solar", "minmax": "min"}.
        
    mutation_rate : float
        The mutation probability, the probability is between 0 to 1. The usual mutation probability is about 0.01.
    
    crossover_rate : float
        The crossover rate, the rate is between 0 to 1. The usual crossover rate is about 0.8.
    
    init_population : int
        The population size. The usual size is about 100.
    
    live_file : str
        The file path of the XML file that documents all the living individuals.
    
    dead_file : str
        The file path of the XML file that documents all the dead individuals.
    
    Returns
    -------
    population : Population class instance
        The created population class instance.
    """
    #====================================
    #initialise the genotype class object
    #====================================
    gm = nsga2.GenotypeMeta()
    #====================================
    #get the gene meta setting 
    #====================================
    for gene_dict in gene_dict_list:
        gene_type = gene_dict["type"]
        gene_range = gene_dict["range"]
        gene = nsga2.Gene(gene_type, gene_range)
        gm.add_gene(gene)
    gm.gene_position()
    #====================================
    #score meta
    #====================================
    #initiate the score meta class
    score_m_list = []
    score_name_list = []
    for score_dict in score_dict_list:
        score_name = score_dict["name"]
        score_name_list.append(score_name)
        score_minmax = score_dict["minmax"]
        if score_minmax == "min":
            score_m_list.append(nsga2.ScoreMeta.MIN)
        if score_minmax == "max":
            score_m_list.append(nsga2.ScoreMeta.MAX)

    sm = nsga2.ScoreMeta(score_name_list, score_m_list)
    #====================================
    #population class parameters
    #====================================
    
    p = nsga2.Population(init_population, gm, sm, live_file , dead_file, mutation_rate, crossover_rate)
    return p

def initialise_nsga2(gene_dict_list, score_dict_list, mutation_rate,crossover_rate,init_population,
          live_file,dead_file ):
              
    """
    This function initialises the population and writes the xml files for an NSGA2 optimisation process.
    
    Parameters
    ----------
    gene_dict_list : list of dictionaries
        Each dictionary contains the parameters for creating a Gene class instance. Each dictionay is in this format: {"type": "int_range", "range": (0,4,1)}.
        
    score_dict_list : list of dictionaries
        Each dictionary contains the parameters for creating a ScoreMeta class instance. Each dictionay is in this format: {"name": "solar", "minmax": "min"}.
        
    mutation_rate : float
        The mutation probability, the probability is between 0 to 1. The usual mutation probability is about 0.01.
    
    crossover_rate : float
        The crossover rate, the rate is between 0 to 1. The usual crossover rate is about 0.8.
    
    init_population : int
        The population size. The usual size is about 100.
    
    live_file : str
        The file path of the XML file that documents all the living individuals.
    
    dead_file : str
        The file path of the XML file that documents all the dead individuals.
    
    Returns
    -------
    population : Population class instance
        The created population class instance.
    """
    empty_xml_files([live_file, dead_file])
    p = create_nsga2_population_class(gene_dict_list, score_dict_list, mutation_rate,crossover_rate,init_population,
          live_file,dead_file)
    p.randomise()
    not_evaluated = p.individuals
    for ind in not_evaluated:
        ind.add_generation(0)
        
    p.write()
    return p
    
def resume_nsga2(gene_dict_list, score_dict_list, mutation_rate,crossover_rate,init_population,
      live_file,dead_file ):
              
    """
    This function resumes a broken NSGA2 optimisation process based on the dead xml file.
    
    Parameters
    ----------
    gene_dict_list : list of dictionaries
        Each dictionary contains the parameters for creating a Gene class instance. Each dictionay is in this format: {"type": "int_range", "range": (0,4,1)}.
        
    score_dict_list : list of dictionaries
        Each dictionary contains the parameters for creating a ScoreMeta class instance. Each dictionay is in this format: {"name": "solar", "minmax": "min"}.
        
    mutation_rate : float
        The mutation probability, the probability is between 0 to 1. The usual mutation probability is about 0.01.
    
    crossover_rate : float
        The crossover rate, the rate is between 0 to 1. The usual crossover rate is about 0.8.
    
    init_population : int
        The population size. The usual size is about 100.
    
    live_file : str
        The file path of the XML file that documents all the living individuals.
    
    dead_file : str
        The file path of the XML file that documents all the dead individuals.
    
    Returns
    -------
    population : Population class instance
        The resumed population class instance.
    """
    p = create_nsga2_population_class(gene_dict_list, score_dict_list, mutation_rate,crossover_rate,init_population,
          live_file,dead_file)
          
    p.read()       
    return p

def feedback_nsga2(population):
    """
    This function performs the feedback process of a population.
    
    Parameters
    ----------
    population : Population class instance
        The function will perform the reproduction on this population and generate a new generation of individuals.
   
    """
    #===================================
    #feedback
    #=================================== 
    current_gen = population.individuals[0].generation
    population.reproduce(population.individuals, current_gen+1)
    population.write()
    #====================================
    #separate the evaluated individuals from the unevaluated one  
    #====================================
    unevaluated = []
    for ind in population.individuals:
        if ind.live == True:
            unevaluated.append(ind)
            
    population.individuals = unevaluated