# -*- coding: utf-8 -*-
# File containing file input/output methods

import os
import xml.etree.ElementTree as et
from unidecode import unidecode
import cPickle as pickle
import subprocess
import random
random.seed(10)

def read_interesting_list(path):
    interesting = []
    with open(path, "r") as interesting_file:
        for line in interesting_file:
            interesting.append(line.strip())
    return interesting

def write_construction_csv(tokens_list, label, cutoff=None):
    cutoff_text = ""
    if cutoff is not None:
        cutoff_text = "-" + str(cutoff)
        if cutoff < len(tokens_list):
            tokens_list = random.sample(tokens_list,cutoff)
    filename = label.lower() + cutoff_text + ".csv"
    
    # lemma,tag,preceding_string,word,following_string, construction_name, ending, personal
    with open(filename,"w") as construction_file:
        file_output = "LEMMA,TAG,PRECEDING,CONSTRUCTION,FOLLOWING,CONSTRUCTION_NAME,ENDING,PERSONAL_NAME,ANIMACY,ALIENABILITY\n"
        construction_file.write(file_output.encode('utf-8'))
        for lemma,tag,preceding_string,word,following_string, construction_name, ending, personal in tokens_list:
            file_output = lemma + "," + tag + "," + preceding_string + "," + word + "," + following_string + "," + construction_name + "," + ending + "," + personal + ",,\n"
        
            construction_file.write(file_output.encode('utf-8'))

def write_construction_pdf(tokens_list, label, cutoff=None):
    filename = label.lower() + ".tex"
    file_output =  "\\documentclass{article}\n"
    file_output += "\\usepackage[T1]{fontenc}\n"
    file_output += "\\usepackage[utf8x]{inputenc}\n"
    file_output += "\\usepackage{longtable}\n"
    file_output += "\\usepackage[left=3cm, right=3cm]{geometry}"
    file_output += "\\title{" + label + "}\n"
    file_output += "\\date{}\n"
    file_output += "\\begin{document}\n"
    file_output += "\\maketitle\n"
    file_output += "\\noindent\n"
    file_output += "\\begin{longtable}{p{1cm}|p{15cm}}\n"
    file_output += "ID&Sentence\\\\\n"
    file_output += "\\hline\n"
    if cutoff is not None:
        tokens_list = random.sample(tokens_list,cutoff)
    i=2
    for preceding,construction,following in tokens_list:
        file_output += str(i) + "&" + preceding + " \\textbf{" + construction + "} " + following + "\\\\\n"
        file_output += "\\hline\n"
        i+=1
    file_output += "\\end{longtable}\n"
    file_output += "\\end{document}\n"
    with open(filename,"w") as construction_file:
        construction_file.write(file_output)
    call_string = ["xelatex",filename]
    subprocess.call(call_string)

def read_data(corpus_directory):
    if(os.path.isfile('saga_sentences.p')):
        with open('saga_sentences.p', 'rb') as saga_pickle:
            sentences = pickle.load(saga_pickle)
        print "Pickle loaded."
    else:
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
        for corpus_path in corpus_paths:
            print corpus_path
            tree = et.parse(corpus_path)
            root = tree.getroot()
            s_instances = root.iter("s")
            s = next(s_instances)
            for word in s.iter():
                if word.tag == "w":
                    # Word
                    # Add pair (word, tag) to sentence
                    lemma = word.get("lemma")
                    tag = word.get("type")
                    word_surface = word.text
                    sentence.append((lemma,tag,word_surface))
                    
                elif word.tag == "c":
                    # End sentence on every punctuation mark .,-
                    # Add sentence to sentences list, and start new sentence
                    sentences.append(sentence)
                    sentence = []
        print "Dumping pickle."
        with open("saga_sentences.p","wb") as saga_pickle:
            pickle.dump(sentences, saga_pickle)
    return sentences
