import numpy as np
from Agent import Agent
from collections import defaultdict

def initialize_agents(n_agents):
    agents = []
    for a in range(0,n_agents):
        agents.append(Agent(a))
    return agents

def converged(cur_probs, prev_probs):
    converged = True
    for key in cur_probs:
        if key not in prev_probs:
            return False
        if abs(cur_probs[key] - prev_probs[key]) > 0.005:
            converged = False
    return converged

def run_simulation(agents, n_iterations=10000):
    previous_avg_probabilities = {}
    for i in range(0,n_iterations):
        if i % 1000 == 0:
            avg_probabilities = calculate_average_probabilities(agents)
            print str(i) + ": " + str(avg_probabilities)
            conv = converged(avg_probabilities, previous_avg_probabilities)
            previous_avg_probabilities = avg_probabilities
            if conv:
                break
        for agent in agents:
            sender = agent
            receiver = np.random.choice(agents)
            utterance = sender.send_utterance()
            receiver.receive_utterance(utterance)

def calculate_average_probabilities(agents):
    all_probabilities = defaultdict(list)
    average_probabilities = defaultdict(float)
    for agent in agents:
        agent_probs = agent.get_probabilities()
        for key in agent_probs:
            all_probabilities[key].append(agent_probs[key])
    
    for key in all_probabilities:
        average_probabilities[key] = np.average(all_probabilities[key])
    
    return average_probabilities

def main():
    agents = initialize_agents(100)
    run_simulation(agents, 10000)


if __name__ == "__main__":
    main()
