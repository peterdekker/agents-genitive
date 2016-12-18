# -*- coding: utf-8 -*-
# File containing file input/output methods

import os
import xml.etree.ElementTree as et
from unidecode import unidecode
import cPickle as pickle
import subprocess
import random
random.seed(10)

def read_list(path):
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
        file_output = "LEMMA,TAG,PRECEDING,CONSTRUCTION,FOLLOWING,CONSTRUCTION_NAME,CONSTRUCTION_DETAILS,PERSONAL_NAME,ANIMACY,ALIENABILITY\n"
        construction_file.write(file_output.encode('utf-8'))
        for lemma,tag,preceding_string,word,following_string, construction_name, ending, personal in tokens_list:
            file_output = lemma + "," + tag + "," + preceding_string + "," + word + "," + following_string + "," + construction_name + "," + ending + "," + personal + ",,\n"
        
            construction_file.write(file_output.encode('utf-8'))

def write_construction_pdf(tokens_list, label, cutoff=None):
    filename = "pdf/" + label.lower() + ".tex"
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
    for function,construction,sentence in tokens_list:
        file_output += str(i) + "&"
        for word in sentence:
            if word == function or word == construction:
                file_output += " \\textbf{" + word + "} "
            else:
                file_output += " " + word + " "
        file_output += "\\\\\n"
        file_output += "\\hline\n"
        i+=1
    file_output += "\\end{longtable}\n"
    file_output += "\\end{document}\n"
    file_output = file_output.encode('utf-8')
    with open(filename,"w") as construction_file:
        construction_file.write(file_output)
    call_string = ["texfot","pdflatex", "-output-directory", "pdf", filename]
    subprocess.call(call_string)

def dir_cleanup():
    subprocess.call("rm pdf/*.aux pdf/*.log pdf/*.tex", shell=True)

def read_corpus(corpus_directory):
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
    
def read_qualitative(path):
    entries = []
    with open(path, "r") as qfile:
        l = 0
        for line in qfile:
            l+=1
            if l==1:
                continue
            split_line = line.split(",")
            # Remove spaces
            split_line = [x.strip() for x in split_line]
            # lines with X not taken into account
            if split_line[11] != "X":
                # Remove entries which have not been filled in
                if (split_line[8] != ""
                and split_line[9] != ""
                and split_line[10] != ""):
                    # If preposition: drop case (dat/gen) in construction name
                    if split_line[5].startswith("pre"):
                        construction = "pre"
                    else:
                        construction = split_line[5]
                    construction_details = split_line[6]
                    
                    # Code for animacy possessor
                    if split_line[8] == "Y":
                        animacy_possessor = "+A"
                        if split_line[7] == "+PN":
                            animacy_possessor += "+PN"
                    else:
                        animacy_possessor = "-A"
                    
                    # Code for animacy possessee
                    if split_line[9] == "Y":
                        animacy_possessee = "+A"
                    else:
                        animacy_possessee = "-A"
                        
                    # Code for alienability (possessor)
                    if split_line[10] == "Y":
                        alienability = "+ali"
                    else:
                        alienability = "-ali"
                    entry = {
                    "construction" : construction,
                    "construction_details": construction_details,
                    "animacy_possessor": animacy_possessor,
                    "animacy_possessee": animacy_possessee,
                    "alienability": alienability
                    }
                    entries.append(entry)
        print "# lines: " + str(l)
        print "# entries: " + str(len(entries))
    return entries
    
    def merge_and_store(dict1,dict2):
        merged_dict = dict(dict1, **dict2)
        with open("lm.p", as lm_pickle):
            pickle.dump(merged_dict, lm_pickle)
