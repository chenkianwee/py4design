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
#    along with Pyliburo.  If not, see <http://www.gnu.org/licenses/>.
#
# ==================================================================================================
import os
import math
import random

import xml.dom.minidom
from xml.dom.minidom import Document

import analyse_xml
#================================================================================
def frange(start, end=None, inc=None):
    """
    A range function, that does accept float increments.
    
    Parameters
    ----------
    start : float
        The starting number of the sequence.
        
    end : float, optional
        Generate numbers up to, but not including this number, Default = None. When None, end == start and start = 0.0.
        
    inc : float, optional
        The difference between each number in the sequence, Default = None. When None, inc = 1.0.
        
    Returns
    -------
    sequence of floats : list of floats
        A list of float.
    """
    if end == None:
        end = start + 0.0
        start = 0.0
    else: start += 0.0 # force it to be a float

    if inc == None:
        inc = 1.0
    count = int(math.ceil((end - start) / inc))

    L = [None,] * count

    L[0] = start
    for i in xrange(1,count):
        L[i] = L[i-1] + inc
    return L
    
#================================================================================
class Gene(object):
    """
    An object that contains all the gene information for running a NSGA2 optimisation.
    
    Parameters
    ----------
    gene_type : str
        The type of the gene. There are four options: "int_range", "int_choice", "float_range", "float_choice".
        
    value_range : list of int/floats
        List of ints/floats. If the gene_type is "int_range" or "float_range", the list has three elements. The first element is the starting number, 
        the second element is the ending number (not included in the sequence), and the last element is the difference between each number in the sequence.
        If the gene_type is "int_choice" or "float_choice", the list is made up of all the possible options.
    
    Attributes
    ----------
    gene_type : str
        see Parameters.
        
    value_range : list of int/floats
        see Parameters.
        
    position : int
        The position of the gene in the genotype. If the position is 0 the gene is in the first postion.
    """
    def __init__(self, gene_type, value_range):
        """Initialises the Gene class"""
        self.gene_type = gene_type
        self.value_range = value_range
        self.position = None
        
class GenotypeMeta(object):
    """
    An object that contains all the meta information of a genotype for running a NSGA2 optimisation.
    
    Attributes
    ----------
    gene_list : list of Gene class instances
        The list of Gene class instances that will be developed in the Genotype class.
    """
    def __init__(self):
        """Initialises the GenotypeMeta class"""
        self.gene_list = []

    def add_gene(self, gene):
        """
        This function adds a gene to the gene list.
        
        Parameters
        ----------
        gene : Gene class instance
            The gene to be added to the Genotype class.
        """
        self.gene_list.append(gene)       

    def gene_position(self):
        """
        This function assigns a position to each gene in the gene list.
        """
        gene_list = self.gene_list
        cnt = 0
        for g in gene_list:
            g.position = cnt
            cnt = cnt + 1
            
    def length(self):
        """
        This function returns the number of genes in the gene list.
        
        Returns
        -------
        length : int
            The number of genes in the gene list.
        """
        length = len(self.gene_list)
        return length

#================================================================================
class Genotype(object):
    """
    An object that contains all the information and methods for developing a genotype for an individual.
    
    Parameters
    ----------
    genotype_meta : GenotypeMeta class instance
        The meta information of the genotype.
        
    Attributes
    ----------
    genotype_meta : GenotypeMeta class instance
        See Parameters.
        
    values : list of floats/ints
        The Genotype values of an individual to develop the individual's phenotype.
    """
    def __init__(self, genotype_meta):
        """Initialises the Genotype class"""
        self.genotype_meta = genotype_meta
        self.values = []
        
    def randomise(self):
        """This function randomly generates the Genotype values"""
        genes = self.genotype_meta.gene_list
        for gene in genes:
            gene_type = gene.gene_type
            value_range = gene.value_range
            if gene_type == "float_range":
                if len(value_range) == 3:
                    gene_range = frange(value_range[0], value_range[1], value_range[2])#random.uniform( value_range[0], value_range[1])
                    gene_value = random.choice(gene_range)
                    self.values.append(gene_value)
                if len(value_range) == 2:
                    gene_value = random.uniform(value_range[0], value_range[1])
                    self.values.append(gene_value)
                
            if gene_type == "float_choice":
                gene_value = random.choice(value_range)
                self.values.append(gene_value)
                
            if gene_type == "int_range":
                gene_value = random.randrange(value_range[0], value_range[1], value_range[2])
                self.values.append(gene_value)
                
            if gene_type == "int_choice":
                gene_value = random.choice(value_range)
                self.values.append(gene_value)
        
    def mutate(self, mutation_prob):
        """
        This function mutates the genotype values.
        
        Parameters
        ----------
        mutation_prob : float
            The mutation probability, the probability is between 0 to 1.
        """
        gene_list = self.genotype_meta.gene_list
        
        for c in range(len(gene_list)):
            roll = random.random()
            if roll <= mutation_prob:
                gene_type = None
                value_range = None
                for gene in gene_list:
                    if gene.position == c:
                        gene_type = gene.gene_type
                        value_range = gene.value_range

                if gene_type == "float_range":
                    if len(value_range) == 3:
                        self.values[c] = random.choice(frange(value_range[0], value_range[1], value_range[2]))
                    if len(value_range) == 2:
                        self.values[c] = random.uniform(value_range[0], value_range[1])
                
                if gene_type == "float_choice":
                    self.values[c] = random.choice(value_range)
                
                if gene_type == "int_range":
                    self.values[c] = random.randrange(value_range[0], value_range[1], value_range[2])
                
                if gene_type == "int_choice":
                    self.values[c] = random.choice(value_range)
                    
    def read_str(self,string):
        """
        This function reads a string and convert it into a list for values attribute.
        
        Parameters
        ----------
        string : str
            The values in string format, e.g. "0.2 3.2 5 0 6.5". The string will be converted to a list and saved as the values attribute.
        """
        self.values = map(float, string.split(" "))

    def write_str(self):
        """
        This function writes the values attribute into a string. 
        
        Returns
        -------
        string : str
            The values is converted from [0.2, 3.2, 5, 0, 6.5] to string format "0.2 3.2 5 0 6.5". 
        """
        return " ".join(map(str,self.values))

    def __repr__(self):
        return self.write_str()
#================================================================================      
class DerivedParams(object):
    """
    An object that contains all the information of derived parameters extracted from the individual.
    
    Attributes
    ----------        
    values : list of floats/ints
        The values of each derived parameter of an individual.
    """
    def __init__(self):
        """Initialises the DerivedParams class"""
        self.values = []
        
    def add_param(self, param):
        """
        This function adds a derived parameter value.
        
        Parameters
        ----------
        param : float
            The value of a derived parameter.
        """
        self.values.append(param)

    def length(self):
        """
        This function returns the number of derived parameter values in the values attribute.
        
        Returns
        -------
        length : int
            The number of derived parameter values in the values attribute.
        """
        length = len(self.values)
        return length
    
    def read_str(self,string):
        """
        This function reads a string and convert it into a list for values attribute.
        
        Parameters
        ----------
        string : str
            The values in string format, e.g. "0.2 3.2 5 0 6.5". The string will be converted to a list and saved as the values attribute.
        """
        self.values = map(float, string.split(" "))

    def write_str(self):
        """
        This function writes the values attribute into a string. 
        
        Returns
        -------
        string : str
            The values is converted from [0.2, 3.2, 5, 0, 6.5] to string format "0.2 3.2 5 0 6.5". 
        """
        return " ".join(map(str,self.values))

    def __repr__(self):
        return self.write_str()

#================================================================================      
class Individual(object):
    """
    An object that contains all the information and methods for developing an individual.
    
    Parameters
    ----------
    idx : int
        A unique number to identify the individual.
        
    genotype_meta : GenotypeMeta class instance
        A GenotypeMeta class instance that provide all the information for developing the Genotype. 
        
    score_meta : ScoreMeta class instance
        The meta information of the performance objectives of the individual.
        
    Attributes
    ----------
    idx : int
       See Parameters.
        
    genotype_meta : GenotypeMeta class instance
        See Parameters.
        
    genotype : Genotype class instance
        A Genotype class instance that provide all the information for developing an individual.
        
    live : bool
        True or False. If True the individual is alive, if False individual is dead.
    
    scores : list of floats
        The list containing the performance of this individual.
    
    derivedparams : DerivedParams class instance
        A DerivedParams class instance containing all the derived parameters informaiton.
    
    generation : int
        The generation this individual is borned in.
    
    distance : float
        The crowding distance of this individual. 
    
    rank : int
        The Pareto rank of this individual.
        
    """
    def __init__(self, idx, genotype_meta, score_meta):
        """Initialises the Individual class"""
        self.id = idx
        self.genotype_meta = genotype_meta
        self.genotype = Genotype(self.genotype_meta)
        self.live = True
        self.scores = map(lambda x:None, range(score_meta.get_num_scores()))
        self.derivedparams = DerivedParams()
        self.generation = None
        self.distance = 0.0
        self.rank = None
        
    def randomise(self):
        """This function randomly generates the Genotype values"""
        self.genotype.randomise()
        
    def set_score(self, index, score):
        """
        This function set the score for the individual.
        
        Parameters
        ----------
        index : int
            The index of the score in the score list to be set.
        
        score : float
            The value of the score.
        """
        self.scores[index] = score

    def get_score(self, index):
        """
        This function get the score for the individual.
        
        Parameters
        ----------
        index : int
            The index of the score in the score list to get.
        
        Returns
        -------
        score : float
            The value of the score.
        """
        return self.scores[index]
    
    def is_not_evaluated(self):
        """
        This function checks if the individual has already been evaluated.
        
        Returns
        -------
        is not evaluated : bool
            True or False, if True the individual is not evaluated, if False the individual is evaluated.
        """
        score_list = self.scores
        N_count = score_list.count(None)
        if len(score_list) == N_count:
            return True
        else:
            return False
        
    def add_derivedparams(self, derivedparams):
        """
        This function adds derived parameter values to the individual.
        
        Parameters
        ----------
        derivedparams : list of floats/ints
            The list of derived parameter values to be added to the individual.
            
        """
        dp = self.derivedparams
        dp.values = derivedparams

    def add_generation(self, generation):
        """
        This function adds the generation this individual is borned in to the individual.
        
        Parameters
        ----------
        generation : int
            The generation this individual is borned in.
            
        """
        self.generation = generation
        
    def xml(self):
        """
        This function writes the individual to an xml format.
        
        Returns
        ----------
        xml individual : str
            The xml string of the individual.
            
        """
        doc = Document()
        if self.live:
            status = "true"
        else:
            status = "false"
            
        xml_doc = analyse_xml.create_xml_individual(doc, self.id, self.generation, status, self.genotype, self.derivedparams, self.scores)
        return xml_doc.toxml()
        
    def __repr__(self):
        return str(self.id) + "," + str(self.generation) + "," + str(self.genotype) + "," + str(self.derivedparams) + "," + ",".join(map(str,self.scores)) + "\n"
    
#================================================================================
class ScoreMeta(object):
    """
    An object that contains all the information of the scores of an individual.
    
    Parameters
    ----------
    score_names : list of str
        A list of the names of the score.
    
    scores_min_max : list of int
        A list of int. The int can only be either 0 or 1. O indicates the score has to be minimise, 1 to be maximised.
    
    Attributes
    ----------        
    See Parameters.
    """
    MIN = 0
    MAX = 1
    def __init__(self, score_names, scores_min_max):
        """Initialises the ScoreMeta class"""
        self.score_names = score_names
        self.scores_min_max = scores_min_max

    def get_num_scores(self):
        """
        This function count the number of scores.
        
        Returns
        ----------
        number of scores : int
            The number of scores. 
        """
        return len(self.scores_min_max)

#================================================================================
class Population(object):
    """
    An object that contains all the information and methods for optimising a population of individuals.
    
    Parameters
    ----------
    size : int
        The population size.
        
    genotype_meta : GenotypeMeta class instance
        A GenotypeMeta class instance that provide all the information for developing the Genotype.
        
    score_meta : ScoreMeta class instance
        The meta information of the performance objectives of the individual.
    
    live_xml_filepath : str
        The file path of the XML file that documents all the living individuals.
    
    dead_xml_filepath : str
        The file path of the XML file that documents all the dead individuals.
        
    mutation_prob : float
        The mutation probability, the probability is between 0 to 1. The usual mutation probability is about 0.01.
    
    crossover_rate : float
        The crossover rate, the rate is between 0 to 1. The usual crossover rate is about 0.8.
        
    Attributes
    ----------
    size : int
        See Parameters.
        
    genotype_meta : GenotypeMeta class instance
        See Parameters.
    
    individuals : list of Individuals class instances
        List of individuals of the population.
        
    live_xml_filepath : str
        See Parameters.
    
    dead_xml_filepath : str
        See Parameters.
        
    score_meta : ScoreMeta class instance
        See Parameters.
        
    mutation_prob : float
        See Parameters.
    
    crossover_rate : float
        See Parameters.
        
    num_archived_individuals : int
        The number of individuals on the dead xml file.
    """
    def __init__(self, size, genotype_meta, score_meta, live_xml_filepath, dead_xml_filepath, mutation_prob, crossover_rate):
        """Initialises the Population class"""
        self.size = size
        self.genotype_meta = genotype_meta
        self.individuals = []
        self.live_xml_filepath = live_xml_filepath
        self.dead_xml_filepath = dead_xml_filepath
        self.score_meta = score_meta
        self.mutation_prob = mutation_prob
        self.crossover_rate = crossover_rate
        self.num_archived_individuals = 0

    def select_random_inds(self, num_inds):
        """
        This function randomly selects a number of individuals.
        
        Parameters
        ----------
        num_inds : int
            The number of individuals to select.
        
        Returns
        -------
        selected individuals : list of Individual class instances
            The list of randomly chosen individuals.
        """
        copy_inds = self.individuals[:]
        random.shuffle(copy_inds)
        chosen_inds = copy_inds[:num_inds]
        return chosen_inds
    
    #functions for pareto ranking
    def _dominates(self, ind1, ind2):
        """
        This function determines if ind1 dominates ind2.
        
        Parameters
        ----------
        ind1 : Individual class instance
            Check if this Individual dominates the other individual.
            
        ind2 : Individual class instance
            Individual 2.
        
        Returns
        -------
        dominates : bool
            True or False, if True ind1 dominates ind2, if false ind1 does not dominate ind2.
        """
        equal = True
        score_meta = self.score_meta
        num_scores = score_meta.get_num_scores()
        for i in range(num_scores):
            val1 = ind1.get_score(i)
            val2 = ind2.get_score(i)
            if val1 != val2: equal = False
            if score_meta.scores_min_max[i] == 0:
                if val2 < val1:
                    return False
            elif val2>val1:
                return False
        if equal: return False
        return True

    def _on_pareto_front(self, ind, inds):
        """
        This function determines if ind is on the pareto front.
        
        Parameters
        ----------
        ind : Individual class instance
            Check if this Individual is on the Pareto front.
            
        inds : list of Individual class instances
            The list of individuals.
        
        Returns
        -------
        on pareto : bool
            True or False, if True ind is on the Pareto front, if False ind is not on the Pareto front.
        """
        for ind2 in inds:
            if self._dominates(ind2, ind):
                return False
        return True
    
    def _extract_pareto_front(self, inds):
        """
        This function extract the Pareto front from the list of inds.
        
        Parameters
        ----------            
        inds : list of Individual class instances
            The list of individuals' Pareto front to be extracted.
        
        Returns
        -------
        pareto front : list of Individual class instances
            The list of individuals on the Pareto front.
        
        non pareto front : list of Individual class instances
            The list of individuals not on the Pareto front.
        """
        pareto_front = []
        non_pareto_front = []
        for ind in inds:    
            if self._on_pareto_front(ind, inds):
                pareto_front.append(ind)
            else:
                non_pareto_front.append(ind)
        return pareto_front, non_pareto_front
    
    def rank(self, inds):
        """
        This function Pareto ranks the individuals.
        
        Parameters
        ----------            
        inds : list of Individual class instances
            The list of individuals' to be ranked.
        
        Returns
        -------
        ranked individuals : 2d list of Individual class instances
            Each list of list of individuals are ranked accordingly. The first list of individuals in the 2d list has the best Pareto rankings.
        """
        rank = 1
        cnt = 0
        ranked = []        
        
        while len(inds) > 0:
            pareto_front, non_pareto_front = self._extract_pareto_front(inds)
            ranked.append([])
            for ind in pareto_front:
                ind.rank = rank
                ranked[-1].append(ind)
            inds = non_pareto_front
            cnt +=1
            rank += 1
        return ranked
    
    def crowd_distance_assignment(self, individuals):
        """
        This function calculates and assigns the crowding distance for the individuals.
        
        Parameters
        ----------            
        individuals : list of Individual class instances
            The list of individuals' to be assigned their crowding distance.
        
        Returns
        -------
        assigned individuals : list of Individual class instances
            Each individual is assigned a crowding distance.
        """
        num_inds = len(individuals)
        num_score = self.score_meta.get_num_scores()
        #for each objective 
        for i in range(num_score):
            individuals = self.sort_objectives(individuals, i)
            individuals[0].distance = float("inf")
            individuals[num_inds-1].distance = float("inf")
            norm = individuals[num_inds-1].scores[i] - individuals[0].scores[i]
            #print individuals[num_inds-1].scores[i], individuals[0].scores[i]
            for j in range(1, num_inds -1):
                #for fronts that have all scores that are 0
                if norm == 0:
                    individuals[j].distance += 0
                else:
                    individuals[j].distance += (individuals[j+1].scores[i] - individuals[j-1].scores[i])/norm
        return individuals
    
    def crowded_comparison(self, ind1, ind2):
        """
        This function compare the two individuals based on crowded comparison.
        
        Parameters
        ----------            
        ind1 : Individual class instance
            Check if this Individual is better than the other individual.
            
        ind2 : Individual class instance
            Individual 2.
        
        Returns
        -------
        comparison : int
            If 1 ind1 is better than ind2, if -1 ind2 is better than ind1, if 0 means both individuals are the same.
        """
        
        if ind1.rank < ind2.rank:
            return 1
            
        elif ind1.rank > ind2.rank:
            return -1
            
        elif ind1.distance > ind2.distance:
            return 1
            
        elif ind1.distance < ind2.distance:
            return -1
            
        else:
            return 0
    
    def sort_objectives(self, individuals, obj_idx):
        """
        This function arranges the individuals in ascending orders according to a chosen performance objective.
        
        Parameters
        ----------            
        individuals : list of Individual class instances
            The list of individuals' to arranged.
            
        obj_idx : int
            The index of the chosen objective for arranging the individuals.
        
        Returns
        -------
        sorted individuals : list of Individual class instances
            The sorted list of individuals in ascending orders according to the chosen objective.
        """
        #arrange in ascending order
        for i in range(len(individuals) - 1, -1, -1):
            for j in range(1, i + 1):
                s1 = individuals[j - 1]
                s2 = individuals[j]
                if s1.scores[obj_idx] > s2.scores[obj_idx]:
                    individuals[j-1] = s2
                    individuals[j] = s1
        return individuals
    
    #=========================================================================
    def crossover(self, ind1, ind2, generation):
        """
        This function performs crossover between two individuals.
        
        Parameters
        ----------            
        ind1 : Individual class instance
            The parent individual.
            
        ind2 : Individual class instance
            The parent individual.
            
        genertaion : int
            The generation of the child individual.
        
        Returns
        -------
        child individual : Individual class instance
            The child individual from the crossover.
        """
        g1 = Genotype(self.genotype_meta)
        genotype_length = self.genotype_meta.length()
        if genotype_length == 2:
            z = 1
        else:
            z = random.randint(1, genotype_length-2)
        
        g1.values.extend(ind1.genotype.values[0:z])
        g1.values.extend(ind2.genotype.values[z:])

        child_ind1 = Individual(self.get_max_id()+1,self.genotype_meta,self.score_meta)
        child_ind1.genotype = g1
        #add the generation
        child_ind1.add_generation(generation)
        return child_ind1
        
    def reproduce(self, individuals, generation):
        """
        This function performs reproduction for the current generation of individuals, kills of the current population and replace them with the reproduced population.
        
        Parameters
        ----------            
        individuals : list of Individual class instances
            The list of individuals' for reproduction.
            
        genertaion : int
            The generation of the new reproduced population.
        """
        new_pop = []
        for ind in individuals:
            ind.live = False
            
        fronts = self.rank(individuals)
        dist_fronts = []
        for front in fronts:
            dist_front = self.crowd_distance_assignment(front)
            dist_fronts.extend(dist_front)
            
        while len(new_pop) != len(dist_fronts):
            selected_solutions = [None, None]
            
            while selected_solutions[0] == selected_solutions[1]:
                for i in range(2):
                    s1 = random.choice(dist_fronts)
                    s2 = s1
                    while s1 == s2:
                        s2 = random.choice(dist_fronts)

                    if self.crowded_comparison(s1, s2) > 0:
                        selected_solutions[i] = s1
                        
                    else:
                        selected_solutions[i] = s2

            #individuals reproduce according to crossover rates
            if random.random() < self.crossover_rate:
                child_solution1 = self.crossover(selected_solutions[0], selected_solutions[1], generation)
                
                #mutation occurs when new individual is born
                child_solution1.genotype.mutate(self.mutation_prob)
                    
                new_pop.append(child_solution1)
                self.individuals.append(child_solution1)

    def get_max_id(self):
        """
        This function gets total number of individuals.
        
        Returns
        -------
        total number of individuals : int
            The total number of individuals.
        """
        #read the dead xml and count the number of individuals in it
        deaddoc = xml.dom.minidom.parse(self.dead_xml_filepath)
        dead_individuals = deaddoc.getElementsByTagName("individual")
        self.num_archived_individuals = len(dead_individuals)
        return self.num_archived_individuals + len(self.individuals) - 1
        
    def randomise(self):
        """This function randomly generates a population of individuals."""
        
        for i in range(self.size):
            individual = Individual(i, self.genotype_meta, self.score_meta)
            individual.randomise()
            self.individuals.append(individual)
            
    def write(self):
        """This function writes all the individuals into xml, the living individuals into the live xml file, the dead ones in the dead xml file."""
        #check if the dead xml file is empty or not
        if os.stat(self.dead_xml_filepath)[6] == 0:
            deaddoc = Document()
            dead_root_node = deaddoc.createElement("data")
            deaddoc.appendChild(dead_root_node)
            dead_population = deaddoc.createElement("population")
            dead_root_node.appendChild(dead_population)
            
        #the xml file is not empty so do not need to reconstruct the whole xml file     
        else:
            #read the whole xml file and append all the neccessary data into it 
            deaddoc = xml.dom.minidom.parse(self.dead_xml_filepath)

        #always overwrite the live xml file
        doc = Document()
        root_node = doc.createElement("data")
        doc.appendChild(root_node)
        population = doc.createElement("population")
        root_node.appendChild(population)
            
        for ind in self.individuals:
            if ind.live:
                doc = analyse_xml.create_xml_file(doc, ind, "true")
            else:
                #create the status
                deaddoc = analyse_xml.create_xml_file(deaddoc, ind, "false") 
                
        f = open(self.live_xml_filepath,"w")
        f.write(doc.toxml())
        f.close()

        df = open(self.dead_xml_filepath,"w")
        df.write(deaddoc.toxml())
        df.close()
    
    def read(self):
        """This function reads the xml files into Python objects."""
        #read all the individuals that is alive
        doc = xml.dom.minidom.parse(self.live_xml_filepath)
        #get all the individuals
        for individual in doc.getElementsByTagName("individual"):
            identity = analyse_xml.get_childnode_value("identity", individual)
            ind = Individual(int(identity),self.genotype_meta, self.score_meta)
            #add the generation of the individual
            generation = analyse_xml.get_childnode_value("generation", individual)
            ind.add_generation(int(generation))
            #read all the genes and put it into the class
            gene_list = self.genotype_meta.gene_list
            genotype_list  = analyse_xml.get_childnode_values("inputparam", individual)
            genotype_list_converted = []
            print genotype_list, identity
            for cnt in range(len(genotype_list)):
                gene_type = None
                for gene in gene_list:
                    if gene.position == cnt:
                        gene_type = gene.gene_type
                if gene_type == "float_range":
                    genotype_list_converted.append(float(genotype_list[cnt]))
                
                if gene_type == "float_choice":
                    genotype_list_converted.append(float(genotype_list[cnt]))
                
                if gene_type == "int_range":
                    genotype_list_converted.append(int(genotype_list[cnt]))
            
                if gene_type == "int_choice":
                    genotype_list_converted.append(int(genotype_list[cnt]))
                    
            ind.genotype.values = genotype_list_converted
            #read all the derived parameters and put it into the class
            if len(individual.getElementsByTagName("derivedparam"))!=0:
                derived_params = analyse_xml.get_childnode_values("derivedparam", individual)
                derived_params_converted = []
                for dp in derived_params:
                    derived_params_converted.append(float(dp))
                ind.add_derivedparams(derived_params_converted)
            #read all the scores and put it into the class
            if len(individual.getElementsByTagName("score"))!=0:
                scores = analyse_xml.get_childnode_values("score", individual)
                for score_count in range(self.score_meta.get_num_scores()):
                    score_str = scores[score_count]
                    if score_str != "None":
                        ind.set_score(score_count, float(score_str))
                
            self.individuals.append(ind)
                
        #read the dead xml and count the number of individuals in it
        deaddoc = xml.dom.minidom.parse(self.dead_xml_filepath)
        dead_individuals = deaddoc.getElementsByTagName("individual")
        self.num_archived_individuals = len(dead_individuals)
        
    def __repr__(self):
        string = ""
        for ind in self.individuals:
            string = string + str(ind) + "\n"
        return string