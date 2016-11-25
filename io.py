# -*- coding: utf-8 -*-
# File containing file input/output methods

import os
import xml.etree.ElementTree as et
from unidecode import unidecode
import cPickle as pickle
import subprocess

def read_interesting_list(path):
    interesting = []
    with open(path, "r") as interesting_file:
        for line in interesting_file:
            interesting.append(line.strip())
    return interesting

def write_word_csv(tokens_list, label, cutoff=None):
    filename = label.lower() + ".csv"
    file_output = "LEMMA,TAG,SENTENCE,,\n"
    if cutoff is not None:
        tokens_list = tokens_list[:cutoff]
    for lemma,tag,preceding,word,following in tokens_list:
        file_output += lemma + "," + tag + "," + preceding + "," + word + "," + following + "\n"
    with open(filename,"w") as construction_file:
        construction_file.write(file_output)

def write_construction_csv(tokens_list, label, cutoff=None):
    filename = label.lower() + ".csv"
    file_output = "," + label.upper()+ ",\n"
    if cutoff is not None:
        tokens_list = tokens_list[:cutoff]
    for preceding,construction,following in tokens_list:
        file_output += preceding + "," + construction + "," + following + "\n"
    with open(filename,"w") as construction_file:
        construction_file.write(file_output)
        
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
        tokens_list = tokens_list[:cutoff]
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
    

def write_interesting_words_csv(qualitative_constr, label):
    filename = label.lower() + ".csv"
    qual_constr_count = {}
    for lemma in qualitative_constr:
        qual_constr_count[lemma] = len(qualitative_constr[lemma])
    sorted_list = sorted(qual_constr_count.items(), key=lambda x: x[1], reverse=True)
    
    file_output = "LEMMA,TOTAL_COUNT,TAG,SENTENCE\n"
    for lemma,count in sorted_list:
        divisor = count/20
        i = 1
        for tag,sentence_words in qualitative_constr[lemma]:
            if i % divisor == 0:
                file_output += lemma + "," + str(count) + "," + tag + "," + sentence_words + "\n"
            i+=1
    with open(filename,"w") as interesting_output_file:
        interesting_output_file.write(file_output)

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
                    lemma = word.get("lemma").encode('utf-8')
                    tag = word.get("type").encode('utf-8')
                    word_surface = word.text.encode('utf-8')
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
