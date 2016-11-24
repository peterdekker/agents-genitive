# -*- coding: utf-8 -*-

import os
import xml.etree.ElementTree as et
from unidecode import unidecode
from collections import defaultdict
import cPickle as pickle

def check_missing(part, complete):
    missing = []
    for entry in complete:
        if entry not in part:
            missing.append(entry)
    
    if len(missing) > 0:
        print "Missing:"
        for m in missing:
            print m
        

def read_interesting_list(path):
    interesting = []
    with open(path, "r") as interesting_file:
        for line in interesting_file:
            interesting.append(line.strip())
    return interesting

def write_construction(tokens_list, filename, cutoff=None):
    file_output = "WORD,LEMMA,TAG,SENTENCE\n"
    if cutoff is not None:
        tokens_list = tokens_list[:cutoff]
    for word,lemma,tag,sentence in tokens_list:
        file_output += word + "," + lemma + "," + tag + "," + sentence + "\n"
    with open(filename,"w") as construction_file:
        construction_file.write(file_output)

def write_interesting_words(qualitative_constr, filename):
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
    
def collect_counts(sentences, interesting_list):
    construction = defaultdict(list)
    function = defaultdict(list)
    constr_func = defaultdict(lambda: defaultdict(list))
    qualitative_constr = defaultdict(list)
     
    genitive = []
    for sentence in sentences:
        sentence_words = " ".join([word for lemma,tag,word in sentence])
        for pos in range(0,len(sentence)):
            lemma,tag,word = sentence[pos]
            # Detect genitive nouns
            if len(tag) > 3:
                if (tag[0] == "n" and tag[3]=="e"):
                    construction["gen_common_noun"].append((word,lemma,tag,sentence_words))
            
            # Detect genitive
            if len(tag) > 3:
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
                        construction["gen"].append((" ".join(genitive),lemma,tag,sentence_words))
                        genitive = []
            
            # Detect interesting words
            if lemma in interesting_list:
                qualitative_constr[lemma].append((tag, sentence_words))
    
    # Write to files
    write_interesting_words(qualitative_constr, "interesting_output.csv")
    write_construction(construction["gen_common_noun"], "genitive_common_noun.csv",1000)
    write_construction(construction["gen"], "genitive.csv",1000)
    
    # Output entries from interesting list that have not been found in corpus
    check_missing(qualitative_constr, interesting_list)

if __name__ == "__main__":
    data = read_data("Saga")
    interesting_list = read_interesting_list("icelandic-interesting-modified.txt")
    collect_counts(data, interesting_list)
