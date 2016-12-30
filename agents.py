


import cPickle as pickle
from collections import defaultdict
import numpy as np

from Agent import Agent
from Exemplar import Exemplar
import utility

import scipy.stats
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

N_AGENTS = 100
N_EXEMPLARS = 100
N_ITERATIONS = 100000
RANDOM_CONSTRUCTION_PROBABILITY = 0.1
PLOT_THRESHOLD = 0.05

WATCH_FUNCTIONS = [('+A+PN', '-A', '+ali'), ('+A', '-A', '+ali'),('+A', '-A', '-ali'), ('+A', '+A', '-ali'), ('+A', '-A', '-ali'), 'verb','pre-dat','pre-gen', 'adv']

def initialize_agents(lm_file_icelandic, n_agents_icelandic, n_agents_german):
    agents = []
    for a in range(0,n_agents_icelandic):
        # Load probabilities from file and create exemplar set
        exemplar_set, p_f_original, p_joint_original, p_cond_original = create_exemplar_set(lm_file_icelandic, N_EXEMPLARS)
        agents.append(Agent(a, exemplar_set, RANDOM_CONSTRUCTION_PROBABILITY))
    return agents

def run_simulation(agents, n_iterations):
    
    graph_cond_c_f = defaultdict(lambda: defaultdict(list))
    graph_c = defaultdict(list)
    
    for i in range(0,n_iterations):
        if i % 500 == 0:
            _, p_c, _, p_cond_c_f = calculate_statistics(agents)
            # create graph per function, with line per construction
            for watch_function in WATCH_FUNCTIONS:
                for c,f in p_cond_c_f:
                    if f==watch_function:
                        prob = p_cond_c_f[(c,f)]
                        graph_cond_c_f[watch_function][c].append((i,prob))
            # create graph per construction
            for c in p_c:
                prob = p_c[c]
                graph_c[c].append((i, prob))
        if i % 1000 == 0:
            print i
        exemplar = None
        # Pick new sender until sender has been found that sends exemplar
        while (exemplar == None):
            sender = np.random.choice(agents)
            exemplar = sender.send_exemplar()
        receiver = np.random.choice(agents)
        receiver.receive_exemplar(exemplar)
    
    return graph_cond_c_f, graph_c

def calculate_statistics(agents):
    count_construction = defaultdict(int)
    count_function = defaultdict(int)
    count_f_c = defaultdict(int)
    
    for agent in agents:
        agent.count_exemplars(count_construction, count_function, count_f_c)
    
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

def create_exemplar_set(filename, n_exemplars):
    # Read data
    with open(filename,"rb") as lm_pickle:
        p_f, p_c, p_joint_f_c, p_cond_c_f = pickle.load(lm_pickle)
    items = p_joint_f_c.items()
    f_c_list = [x[0] for x in items]
    probs = [x[1] for x in items]
    
    f_c_dict = {}
    for n in np.arange(len(f_c_list)):
        f_c_dict[n] = f_c_list[n]
    
    # Create exemplars
    exemplars = []
    for i in np.arange(n_exemplars):
        f_c_index = np.random.choice(f_c_dict.keys(),p=probs)
        f_c = f_c_dict[f_c_index]
        function = f_c[0]
        construction = f_c[1]
        exemplar = Exemplar(function,construction)
        exemplars.append(exemplar)
    return exemplars, p_f, p_joint_f_c, p_cond_c_f
         

def plot_graphs(graphs_cond_c_f, graphs_c):
    fontP = FontProperties()
    fontP.set_size('small')
    
    fontQ = FontProperties(size=9)
    
    # One plot for every function, with a line per construction p(c|f)
    for function in graphs_cond_c_f:
        plt.title(function)
        legend_info = []
        # One line for every construction
        for construction in graphs_cond_c_f[function]:
            x = [p[0] for p in graphs_cond_c_f[function][construction]]
            y = [p[1] for p in graphs_cond_c_f[function][construction]]
            line, = plt.plot(x,y, label=construction)
            legend_info.append(line)
        plt.legend(handles=legend_info, loc="center left", bbox_to_anchor=(0.85, 0.5), prop=fontP)
        plt.show()
    
    # One plot with all probabilities p(c)
    plt.title("Constructions")
    legend_info = []
    ax  = plt.subplot(111)
    # One line for every construction
    for construction in graphs_c:
        x = [p[0] for p in graphs_c[construction]]
        y = [p[1] for p in graphs_c[construction]]
        if y[-1] > PLOT_THRESHOLD:
            line, = ax.plot(x,y, label=construction)
            legend_info.append(line)

    # Shrink current axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.85, box.height])
    ax.legend(handles=legend_info, loc="center left", bbox_to_anchor=(1.0, 0.5), prop=fontQ)
    plt.show()
    

def test_exemplar_set_sizes(lm_file):
    n_agents = 10000
    for size in [10,20,50,100,200,500,1000]:
        correlations = []
        x2_ps = []
        x2s = []
        for a in np.arange(n_agents):
            exemplar_set, p_f_original, p_joint_original, p_cond_original = create_exemplar_set(lm_file, size)
            agent = Agent(a, exemplar_set, RANDOM_CONSTRUCTION_PROBABILITY)
            p_f_agent, p_c_agent, p_joint_agent, p_cond_agent = agent.calculate_statistics()
            orig = []
            agent = []
            for key in p_joint_original:
                orig.append(p_joint_original[key]*size)
                agent.append(p_joint_agent[key]*size)
            
            r,_ = scipy.stats.pearsonr(agent,orig)
            x2,p = scipy.stats.chisquare(agent,orig, ddof=len(orig)-1)
            correlations.append(r)
            x2s.append(x2)
            x2_ps.append(p)
        correlation_avg = np.average(correlations)
        x2_avg = np.average(x2s)
        x2_p_avg = np.average(x2_ps)
        print "[" + str(size) + "] pearson-r: " + str(correlation_avg) + ", X2,p: " + str(x2_avg) +  "," + str(x2_p_avg)

def main():
    #test_exemplar_set_sizes("lm-icelandic-merged.p")
    # Initialize 100 agents with Old Icelandic language model
    agents = initialize_agents("lm-icelandic-merged.p",N_AGENTS, 0)
    p_f_start, p_c_start, p_joint_start, p_cond_start = calculate_statistics(agents)
    print "Start"
    
    # Run simulation
    graphs_cond_c_f, graphs_c = run_simulation(agents, N_ITERATIONS)
    p_f_end, p_c_end, p_joint_end, p_cond_end = calculate_statistics(agents)
    print
    print "End"
    
    # Plot graphs
    plot_graphs(graphs_cond_c_f, graphs_c)

if __name__ == "__main__":
    main()
