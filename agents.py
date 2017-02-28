

import dill as pickle
from collections import defaultdict
import numpy as np
import os

from Agent import Agent
from Exemplar import Exemplar
import utility
import files

import argparse
import scipy.stats
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties


# Default parameter settings. Can be overridden using command line arguments.
N_SIMULATIONS = 5
N_ITERATIONS = 300000
N_AGENTS_ICELANDIC = 100
N_EXEMPLARS = 50
RANDOM_CONSTRUCTION_PROBABILITY = 0.01

GRAPH_FREQUENCY = 500
PRINT_FREQUENCY = 5000
PLOT_THRESHOLD = 0.05

USE_INTRUDERS = False
N_INTRUDERS = 50
INTRUSION_ITERATION = 50000
INTRUSION_N_BATCHES = 1
INTRUSION_BATCH_INTERVAL = 10000

ALL_FUNCTIONS = ['pre', 'adv', ('+A', '-A', '+ali'), ('+A', '+A', '-ali'), ('+A+PN', '-A', '+ali'), ('-A', '-A', '-ali'), ('-A', '+A', '-ali'), ('-A', '-A', '+ali'), ('+A+PN', '-A', '-ali'), ('+A', '+A', '+ali'), 'verb', ('+A', '-A', '-ali'), ('+A+PN', '+A', '+ali'), ('+A+PN', '+A', '-ali')]

WATCH_FUNCTIONS = ALL_FUNCTIONS

def print_flags(FLAGS):
    """
    Prints all entries in FLAGS variable.
    """
    for key, value in vars(FLAGS).items():
        print(key + ' : ' + str(value))

def initialize_agents(lm_file, n_agents, n_exemplars, random_construction_probability):
    agents = []
    for a in range(0,n_agents):
        # Load probabilities from file and create exemplar set
        exemplar_set, p_f_original, p_joint_original, p_cond_original = create_exemplar_set(lm_file, n_exemplars)
        agents.append(Agent(a, exemplar_set, random_construction_probability))
    return agents

def run_simulation(agents, n_iterations, intruders=None, intrusion_iteration=-1,
    intrusion_n_batches=-1, intrusion_batch_interval=-1):
    
    graph_cond_c_f = defaultdict(lambda: defaultdict(list))
    graph_c = defaultdict(list)
    
    for i in range(0,n_iterations):
        if i % GRAPH_FREQUENCY == 0:
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
        if i % PRINT_FREQUENCY == 0:
            print i
            
        if intruders and intrusion_n_batches > 0:
            if i>=intrusion_iteration and (i - intrusion_iteration) % intrusion_batch_interval == 0:
                print str(len(intruders)) + " Middle Low-German intruders added"
                agents = agents + intruders
                intrusion_n_batches -= 1
        
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
         

def plot_graphs_cond(graphs_cond_c_f, FLAGS):
    fontP = FontProperties()
    fontP.set_size('small')
    
    fontQ = FontProperties(size=9)
    
    filename= "constructions-" + str(FLAGS.n_iterations) + "x" + str(FLAGS.n_simulations)
    if FLAGS.use_intruders:
        filename+= "-intruders" + str(FLAGS.n_intruders) + "@" + str(FLAGS.intrusion_iteration)
    filename+= "-" + "random" + str(FLAGS.random_construction_probability)
    
    # One plot for every function, with a line per construction p(c|f)
    for function in graphs_cond_c_f:
        plt.figure()
        plt.title(function)
        legend_info = []
        # One line for every construction
        for construction in graphs_cond_c_f[function]:
            x = [p[0] for p in graphs_cond_c_f[function][construction]]
            y = [p[1] for p in graphs_cond_c_f[function][construction]]
            if y[0] > PLOT_THRESHOLD or y[-1] > PLOT_THRESHOLD:
                line, = plt.plot(x,y, label=construction)
                legend_info.append(line)
        plt.legend(handles=legend_info, loc="center left", bbox_to_anchor=(0.85, 0.5), prop=fontP)
        if isinstance(function, basestring):
            function_string = function
        else:
            function_string = " ".join(function)
        function_dir = os.path.join("plots", function_string)
        files.create_directory(function_dir)
        plt.savefig(os.path.join(function_dir,filename) + ".png")

def plot_graph_c(graph_c, FLAGS):
    label = "Constructions"
    fontP = FontProperties()
    fontP.set_size('small')
    
    fontQ = FontProperties(size=9)
    # One plot with all probabilities p(c)
    plt.title(label)
    legend_info = []
    ax  = plt.subplot(111)
    # One line for every construction
    for construction in graph_c:
        x = [p[0] for p in graph_c[construction]]
        y = [p[1] for p in graph_c[construction]]
        if y[0] > PLOT_THRESHOLD or y[-1] > PLOT_THRESHOLD:
            line, = ax.plot(x,y, label=construction)
            legend_info.append(line)

    # Shrink current axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.80, box.height])
    ax.legend(handles=legend_info, loc="center left", bbox_to_anchor=(1.0, 0.5), prop=fontQ)
    
    filename= "plots/constructions-" + str(FLAGS.n_iterations) + "x" + str(FLAGS.n_simulations)
    if FLAGS.use_intruders:
        filename+= "-intruders" + str(FLAGS.n_intruders) + "x" + str(FLAGS.intrusion_n_batches) + "@" + str(FLAGS.intrusion_iteration)
        if FLAGS.intrusion_n_batches > 1:
            filename += ">" + str(FLAGS.intrusion_batch_interval)
    filename+= "-" + "random" + str(FLAGS.random_construction_probability)
    plt.savefig(filename + ".png")
    

def test_exemplar_set_sizes(lm_file, random_construction_probability):
    n_agents = 10000
    for size in [10,20,50,100,200,500,1000]:
        correlations = []
        x2_ps = []
        x2s = []
        for a in np.arange(n_agents):
            exemplar_set, p_f_original, p_joint_original, p_cond_original = create_exemplar_set(lm_file, size)
            agent = Agent(a, exemplar_set, random_construction_probability)
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

def average_graphs(simulation_graphs, n_iterations):
    avg_graph_c = defaultdict(list)
    avg_cond_graphs = defaultdict(lambda: defaultdict(list))
    iterations = np.arange(0,n_iterations,GRAPH_FREQUENCY)
    for iteration in iterations:
        c_per_iteration = defaultdict(list)
        cond_per_iteration = defaultdict(lambda: defaultdict(list))
        for cond_graphs, graph_c in simulation_graphs:
            for c in graph_c:
                # Search value for this iteration
                # if not found, value = 0.0
                value = 0.0
                for i,v in graph_c[c]:
                    if i==iteration:
                        value = v
                c_per_iteration[c].append(value)
            for f in cond_graphs:
                function_graph = cond_graphs[f]
                for c in function_graph:
                    # Search value for this iteration
                    # if not found, value = 0.0
                    value = 0.0
                    for i,v in function_graph[c]:
                        if i==iteration:
                            value = v
                    cond_per_iteration[f][c].append(value)
        for c in c_per_iteration:
            avg_value = np.average(c_per_iteration[c])
            avg_graph_c[c].append((iteration,avg_value))
        for f in cond_per_iteration:
            for c in cond_per_iteration[f]:
                avg_value = np.average(cond_per_iteration[f][c])
                avg_cond_graphs[f][c].append((iteration,avg_value))
    return avg_graph_c, avg_cond_graphs

def main(FLAGS):
    
    #test_exemplar_set_sizes("lm-icelandic-merged.p", FLAGS.random_construction_probability)
    simulation_graphs = []
    
    # Perform N_SIMULATIONS simulations with new initialization
    for sim in np.arange(1,FLAGS.n_simulations+1):
        icelandic_agents = initialize_agents("lm-icelandic-merged-fmerged-dropdetails.p",FLAGS.n_agents_icelandic, FLAGS.n_exemplars, FLAGS.random_construction_probability)
        if FLAGS.use_intruders:
            intrusive_agents = initialize_agents("lm-german-merged-fmerged-dropdetails.p",FLAGS.n_intruders, FLAGS.n_exemplars, FLAGS.random_construction_probability)
        else:
            intrusive_agents = None
        print "SIMULATION " + str(sim)
        # Run simulation
        graphs_cond_c_f, graph_c = run_simulation(icelandic_agents, FLAGS.n_iterations, intruders=intrusive_agents, intrusion_iteration = FLAGS.intrusion_iteration, intrusion_n_batches = FLAGS.intrusion_n_batches, intrusion_batch_interval = FLAGS.intrusion_batch_interval)
        simulation_graphs.append((graphs_cond_c_f, graph_c))
    
    avg_graph_c, avg_cond_graphs = average_graphs(simulation_graphs, FLAGS.n_iterations)
    plot_graph_c(avg_graph_c, FLAGS)
    with open("graphs.p", "wb") as graph_p:
        pickle.dump(avg_cond_graphs, graph_p)
    plot_graphs_cond(avg_cond_graphs, FLAGS)

if __name__ == "__main__":
    # Command line arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('--n_simulations', type = int, default = N_SIMULATIONS)
    parser.add_argument('--n_iterations', type = int, default = N_ITERATIONS)
    parser.add_argument('--n_agents_icelandic', type = int, default = N_AGENTS_ICELANDIC)
    parser.add_argument('--n_exemplars', type = int, default = N_EXEMPLARS)
    parser.add_argument('--random_construction_probability', type = float, default = RANDOM_CONSTRUCTION_PROBABILITY)
    parser.add_argument('--use_intruders', action='store_true', default=USE_INTRUDERS)
    parser.add_argument('--n_intruders', type = int, default = N_INTRUDERS)
    parser.add_argument('--intrusion_iteration', type = int, default = INTRUSION_ITERATION)
    parser.add_argument('--intrusion_n_batches', type = int, default = INTRUSION_N_BATCHES)
    parser.add_argument('--intrusion_batch_interval', type = int, default = INTRUSION_BATCH_INTERVAL)
    FLAGS, unparsed = parser.parse_known_args()
    print_flags(FLAGS)
    main(FLAGS)
