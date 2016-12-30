
import numpy as np
from collections import defaultdict

from Exemplar import Exemplar

class Agent(object):
    
    def send_exemplar(self):
        if len(self.exemplar_set) > 0:
            # Choose exemplar, with equal probability
            exemplar = np.random.choice(self.exemplar_set)
            exemplar_function = exemplar.get_function()
            
            # Calculate statistics of own agent
            p_f, p_c, p_joint_f_c, p_cond_c_f = self.calculate_statistics()
            possible_constructions = []
            probs = []
            # With probability self.random_construction_probability, sample from p_c
            if np.random.random() < self.random_construction_probability:
                for c in p_c:
                    possible_constructions.append(c)
                    probs.append(p_c[c])
            else:
                # Otherwise, use p_cond_c_f of own agent to decide which construction to use
                for c,f in p_cond_c_f:
                    if f == exemplar_function:
                        possible_constructions.append(c)
                        prob = p_cond_c_f[(c,f)]
                        probs.append(prob)
            constr_indices = np.arange(len(possible_constructions))
            construction_index = np.random.choice(constr_indices,p=probs)
            construction = possible_constructions[construction_index]
            # Create new exemplar, with function from own exemplar, and chosen construction
            new_exemplar = Exemplar(exemplar_function,construction)
            # Remove own exemplar
            self.exemplar_set.remove(exemplar)
        
        else:
            new_exemplar = None
        # Return new exemplar
        return new_exemplar
    
    def receive_exemplar(self, exemplar):
        self.exemplar_set.append(exemplar)
    
    def count_exemplars(self, count_construction, count_function, count_f_c):
        for exemplar in self.exemplar_set:
            function = exemplar.get_function()
            construction = exemplar.get_construction()
            count_construction[construction] += 1
            count_function[function] +=1
            count_f_c[(function,construction)] += 1
    
    def calculate_statistics(self):
        count_construction = defaultdict(int)
        count_function = defaultdict(int)
        count_f_c = defaultdict(int)
        
        self.count_exemplars(count_construction, count_function, count_f_c)
        
        count_construction_total = sum(count_construction.values())
        count_function_total = sum(count_function.values())
        count_f_c_total = sum(count_f_c.values())
        assert count_construction_total == count_function_total == count_f_c_total
        p_f = defaultdict(float)
        p_c = defaultdict(float)
        p_joint_f_c = defaultdict(float)
        p_cond_c_f = defaultdict(float)
        for function in count_function:
            # p(function) = c(function)/c(total)
            p_f[function] = count_function[function]/float(count_function_total)
        
        for construction in count_construction:
            # p(construction) = c(construction)/c(total)
            p_c[construction] = count_construction[construction]/float(count_construction_total)
        
        for function,construction in count_f_c:
            # p(function,construction) = count(function,construction)/c_total
            p_joint_f_c[(function,construction)] = count_f_c[(function,construction)]/float(count_f_c_total)
            # p(construction|function) = p(construction,function) / p(function)
            p_cond_c_f[(construction,function)] = p_joint_f_c[(function,construction)] / float(p_f[function])

        return p_f, p_c, p_joint_f_c, p_cond_c_f
    
    def __init__(self,a_id, exemplar_set, random_construction_probability):
        self.a_id = str(a_id)
        self.exemplar_set = exemplar_set
        self.random_construction_probability = random_construction_probability
    
    def __str__(self):
        return str(self.a_id)
