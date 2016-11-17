
import numpy as np
from collections import defaultdict

LEARNING_RATE = 1.0

class Agent(object):
    
    def send_utterance(self):
        utt_options = self.probability.keys()
        probs = self.probability.values()
        return np.random.choice(utt_options,p=probs)
    
    def receive_utterance(self, utterance):
        self.seen[utterance] += 1
        self.seen_total += 1
        
        for utt in self.probability:
            observed_probability_utterance = float(self.seen[utt])/self.seen_total
            self.probability[utt] = (1-LEARNING_RATE)*self.probability[utt] + LEARNING_RATE * observed_probability_utterance
        
    
    def get_probabilities(self):
        return self.probability
    
    def __init__(self,a_id):
        self.a_id = str(a_id)
        a_id = 0
    
        self.probability = {"A":0.7, "B": 0.3}
        self.seen = defaultdict(int)
        self.seen_total = 0
    
    def __str__(self):
        return str(self.a_id)
