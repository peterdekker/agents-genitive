# -*- coding: utf-8 -*-

#MIT License

#Copyright (c) 2017 Peter Dekker

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

# files.py: Methods for reading/writing files

import os
import errno
import xml.etree.ElementTree as et
from unidecode import unidecode
import cPickle as pickle
import subprocess
import random
random.seed(10)
from collections import defaultdict

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
    
def read_qualitative(path, lang_format):
    entries = []
    with open(path, "r") as qfile:
        l = 0
        for line in qfile:
            l+=1
            # Skip first lines
            if lang_format=="icelandic" and l==1:
                continue
            if lang_format=="german" and l<12:
                continue
            split_line = line.split(",")
            # Remove spaces
            split_line = [x.strip() for x in split_line]
            
            if lang_format=="icelandic":
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
                        construction_details = unicode(split_line[6], "utf-8")
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
                        
                        order = ""
                        if split_line[13].startswith("1"):
                            order = "order1"
                        elif split_line[13].startswith("2"):
                            order = "order2"
                        entry = {
                        "construction" : construction,
                        "construction_details": construction_details,
                        "order": order,
                        "animacy_possessor": animacy_possessor,
                        "animacy_possessee": animacy_possessee,
                        "alienability": alienability
                        }
                        entries.append(entry)
            elif lang_format == "german":
                # Use 'preposition' column to determine construction
                if split_line[4] == "":
                    # If no preposition, construction = "pre"/"dat"
                    construction = split_line[1].lower()
                    # construction_details = declination (equiv. to ending)
                    construction_details = split_line[2].split()[0]
                elif split_line[4] == "Rel PN":
                    construction = "rel-pn"
                    construction_details = ""
                else:
                    # If there is a preposition, construction = "pre"
                    construction = "pre"
                    construction_details = split_line[4]
                order = ""
                if split_line[3].startswith("1"):
                    order = "order1"
                elif split_line[3].startswith("2"):
                    order = "order2"
                # Code for animacy possessor
                if split_line[6] == "Y":
                    animacy_possessor = "+A"
                    if split_line[10] == "+PN":
                        animacy_possessor += "+PN"
                else:
                    animacy_possessor = "-A"
                
                # Code for animacy possessee
                if split_line[7] == "Y":
                    animacy_possessee = "+A"
                else:
                    animacy_possessee = "-A"
                    
                # Code for alienability (possessor)
                if split_line[8] == "Y":
                    alienability = "+ali"
                else:
                    alienability = "-ali"
                entry = {
                "construction" : construction,
                "construction_details": construction_details,
                "order": order,
                "animacy_possessor": animacy_possessor,
                "animacy_possessee": animacy_possessee,
                "alienability": alienability
                }
                entries.append(entry) 
            
            else:
                print "Unknown language format: " + lang_format
                    
    return entries

def write_prob_table(p_f, p_c, p_cond_c_f, filename):
    # Create new p_cond_c_f with inverted keys (f,c) instead of (c,f)
    p_inv = {}
    for c,f in p_cond_c_f:
        p_inv[(f,c)] = p_cond_c_f[(c,f)]
    return write_count_table(p_f,p_c,p_inv, filename)

def write_count_table(count_f, count_c, count_f_c, filename, latex=True):
    delim = ";"
    if latex:
        delim = "&"
    with open(filename,"w") as table_file:
        content_type = type(count_f_c.values()[0])
        dict_per_f = defaultdict(lambda: defaultdict(content_type))
        for f,c in count_f_c:
            dict_per_f[f][c] = count_f_c[(f,c)]
        c_sorted = sorted(count_c.keys(), reverse=True)
        c_list = [":".join(c) for c in c_sorted]
        if latex:
            header_line = "&&"
        else:
            header_line = "F\\C"
        header_line += delim
        header_line += delim.join(c_list)
        header_line += delim + "\n"
        header_line = header_line.encode("utf-8")
        table_file.write(header_line)
        # Write line with construction counts per function
        f_sorted = sorted(dict_per_f.keys())
        for f in f_sorted:
            function_line = "&".join(f)
            # Add count per construction
            for c in c_sorted:
                f_c_string = fmt(dict_per_f[f][c], content_type)
                function_line += delim
                function_line += f_c_string
            # Add function total
            tot_f_string = fmt(count_f[f], content_type)
            function_line += delim
            if latex:
                function_line += "\\textbf{"
            function_line += tot_f_string
            if latex:
                function_line += "}\\\\"
            function_line += "\n"
            table_file.write(function_line)
        # Write construction totals
        total_line = delim
        for c in c_sorted:
            tot_c_string = fmt(count_c[c],content_type)
            if latex:
                total_line += "\\textbf{"
            total_line += tot_c_string
            if latex:
                total_line += "}"
            total_line += delim
        final_total = sum(count_c[c] for c in count_c)
        tot_c_string = fmt(final_total,content_type)
        if latex:
            total_line += "\\textbf{"
        total_line += tot_c_string
        if latex:
            total_line += "}\\\\"
        total_line += "\n"
        table_file.write(total_line)

def fmt(value, content_type):
    if content_type == float:
        value_string = "{:.4f}".format(value)
    else:
        value_string = str(value)
    return value_string

def store(data, filename):
    with open(filename, "wb") as lm_pickle:
        pickle.dump(data, lm_pickle)
    print(filename + " written to file.")

def create_directory(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
