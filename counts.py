# -*- coding: utf-8 -*-

import os
import xml.etree.ElementTree as et
from unidecode import unidecode
from collections import defaultdict

def read_data(corpus_directory):
    datalist = []
    corpus_paths = []
    # Form paths of corpus files
    corpus_files=os.listdir(corpus_directory)
    for filename in corpus_files:
        if filename[0] == "F":
            corpus_paths.append(os.path.join(corpus_directory,filename))
    corpus_paths.sort()
    
    # Walk through XML structure and collect sentences
    sentences = []
    sentence = []
    for corpus_path in corpus_paths[:1]:
        print corpus_path
        tree = et.parse(corpus_path)
        root = tree.getroot()
        s_instances = root.iter("s")
        s = next(s_instances)
        for word in s.iter():
            if word.tag == "w":
                # Word
                # Add pair (word, tag) to sentence
                sentence.append((word.text.encode('utf-8'), word.get("type").encode('utf-8')))
            elif word.tag == "c":
                # End sentence on every punctuation mark .,-
                # Add sentence to sentences list, and start new sentence
                sentences.append(sentence)
                sentence = []
    return sentences
    
def collect_counts(sentences):
    construction = defaultdict(list)
    function = defaultdict(list)
    constr_func = defaultdict(lambda: defaultdict(list))
    
    genitive = []
    for sentence in sentences:
        sentence_words = " ".join([word for (word,pos) in sentence])
        for word,tag in sentence:
            # Detect genitive
            if ((tag[0] == "n" and tag[3]=="e") # nomen genitive
                or (tag[0] == "f" and tag[4]=="e")    # pronoun genitive
                or (tag[0] == "l" and tag[3]=="e")    # adjective genitive
                or (tag[0] == "g" and tag[3]=="e")    # article genitive
                or (tag[0] == "t" and tag[4]=="e")):    # number genitive
                    # TODO: look at excluding gen. pronoun "hans" from list
                    genitive.append(word)
            else:
                # If a genitive has built up, it is now ended
                if len(genitive) > 0:
                    construction["gen"].append((" ".join(genitive),sentence_words, "genitive"))
                    genitive = []
    
    print "Number of genitives: "
    print construction["gen"][:5]
    

if __name__ == "__main__":
    data = read_data("Saga")
    collect_counts(data)
