# -*- coding: utf-8 -*-

#MIT License

#Copyright (c) 2017 Peter Dekker, Myrthe Bil

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

# counts.py: Stand-alone script to generate language model probabilities from corpus


from collections import defaultdict
import numpy as np
import os
import argparse
import utility
from utility import print_sorted
import files

QUAL_INTRUDERS = "20170103-qualitative-mlg-justin.csv"
QUAL_ICELANDIC = "20170103-qualitative-icelandic-justin.csv"
OUTPUT_DIR = "pickles"
SAGA_INPUT_DIR = "Saga"

def count_dict(dct):
    count = defaultdict(int)
    for key in dct:
        count[key] = len(dct[key])
    
    return count

def count_quantitative(sentences, verb_list, adj_list, adv_list, order, order_probs=None, write_pdf=False):
    construction = defaultdict(list)
    function = defaultdict(list)
    function_construction = defaultdict(list)
    
    verb_before = False
    adjective_before = False

    for sentence in sentences:
        verb_before = ""
        pos_verb_before = 0
        
        adj_before = ""
        pos_adj_before = 0
        
        adv_before = ""
        pos_adv_before = 0
        
        pre_before = ""
        pos_pre_before = 0
        pre_before_type = ""
        
        sentence_words = [word for lemma,tag,word in sentence]
        sentence_string = " ".join(sentence_words)
        for pos in range(0,len(sentence)):
            lemma,tag,word = sentence[pos]
            lemma_cmp=lemma.encode('utf-8')
            
            ###### Functions
            # Match verb
            if (tag[0] == "s"):
                if lemma_cmp in verb_list:
                    verb_before = word
                    pos_verb_before = pos
            
            # Match adjective (nom or acc)
            if (tag[0] == "l" and (tag[3]=="n" or tag[3]=="o")):
                if lemma_cmp in adj_list:
                    adj_before = word
                    pos_adj_before = pos
            
            # Match adverb
            if (tag.startswith("aa")):
                if lemma_cmp in adv_list:
                    adv_before = word
                    pos_adv_before = pos
            
            # Match prepositions governing dative/genitive
            if (tag == u"aþ"):
                pre_before = word
                pos_pre_before = pos
                pre_before_type = "dat"
            if (tag == u"ae"):
                pre_before = word
                pos_pre_before = pos
                pre_before_type = "gen"
            
            ###### Constructions
            # Now, look which constructions occur after a certain function
            
            # Possessive preposition (all)
            if ((tag == u"aþ"
            or tag == u"ae"
            or tag == u"aþe"
            or tag == u"aþm")
            and (word in [u"til",u"í",u"á",u"af",u"frá",u"hjá",u"að"])):
                if ((len(verb_before) and pos-pos_pre_before<=5)
                or (len(adj_before) and pos-pos_adj_before<=5)
                or (len(adv_before) and pos-pos_adv_before<=5)):
                    if order:
                        # Sample order from qualitative distribution
                        sampled_order = np.random.choice(["order1","order2"], p=order_probs)
                        features_construction = ("pre",word, sampled_order)
                    else:
                        features_construction = ("pre",word)
                    construction[features_construction].append(word)
                    if len(verb_before):
                        function["verb"].append(verb_before)
                        function_construction[("verb",features_construction)].append((verb_before,word, sentence_words))
                        verb_before = ""
                    elif len(adj_before):
                        function["adj"].append(adj_before)
                        function_construction[("adj",features_construction)].append((adj_before,word, sentence_words))
                        adj_before = ""
                    elif len(adv_before):
                        function["adv"].append(adv_before)
                        function_construction[("adv",features_construction)].append((adv_before,word, sentence_words))
                        adv_before = ""
            
            # Genitive noun
            elif (len(tag) > 3 and tag[0] == "n" and tag[3]=="e"):
                if ((len(verb_before) and pos-pos_pre_before<=5)
                or (len(adj_before) and pos-pos_adj_before<=5)
                or (len(adv_before) and pos-pos_adv_before<=5)
                or (len(pre_before) and pos-pos_pre_before<=5)):
                    if (len(tag)==5 and tag[4]=="g"):
                        # ins, ns, innar, nnar, nna
                        if (word.endswith("innar")):
                            ending = "DEF-innar"
                        elif (word.endswith("nnar")):
                            ending = "DEF-nnar"
                        elif (word.endswith("nna")):
                            ending = "DEF-nna"
                        elif (word.endswith("ins")):
                            ending = "DEF-ins"
                        elif (word.endswith("ns")):
                            ending = "DEF-ns"
                        else:
                            ending = "DEF-other"
                    elif (word.endswith(("s"))):
                        ending = "s"
                    elif (word.endswith(("ar"))):
                        ending = "ar"
                    elif (word.endswith(("ur"))):
                        ending = "ur"
                    elif (word.endswith(("na"))):
                        ending = "na"
                    elif (word.endswith(("u"))):
                        ending = "u"
                    elif (word.endswith(("a"))):
                        ending = "a"
                    elif (word.endswith(("i"))):
                        ending = "i"
                    elif (word.endswith(("r"))):
                        ending = "r"
                    else:
                        ending = "EMPTY"
                    if order:
                        # Sample order from qualitative distribution
                        sampled_order = np.random.choice(["order1","order2"], p=order_probs)
                        features_construction = ("gen",ending, sampled_order)
                    else:
                        features_construction = ("gen",ending)
                    construction[features_construction].append(word)
                    if len(verb_before):
                        function["verb"].append(verb_before)
                        function_construction[("verb",features_construction)].append((verb_before,word, sentence_words))
                        verb_before = ""
                    elif len(adj_before):
                        function["adj"].append(adj_before)
                        function_construction[("adj",features_construction)].append((adj_before,word, sentence_words))
                        adj_before = ""
                    elif len(adv_before):
                        function["adv"].append(adv_before)
                        function_construction[("adv",features_construction)].append((adv_before,word, sentence_words))
                        adv_before = ""
                    elif (len(pre_before) and pre_before_type == "dat"):
                        function["pre-dat"].append(pre_before)
                        function_construction[("pre-dat",features_construction)].append((pre_before,word, sentence_words))
                        pre_before = ""
                        pre_before_type = ""
                    elif (len(pre_before) and pre_before_type == "gen"):
                        function["pre-gen"].append(pre_before)
                        function_construction[("pre-gen",features_construction)].append((pre_before,word, sentence_words))
                        pre_before = ""
                        pre_before_type = ""
            
            # Dative noun
            elif ((len(tag) > 3) and (tag[0]== "n") and (tag[3] == u"þ")):
                if ((len(verb_before) and pos-pos_pre_before<=5)
                or (len(adj_before) and pos-pos_adj_before<=5)
                or (len(adv_before) and pos-pos_adv_before<=5)
                or (len(pre_before) and pos-pos_pre_before<=5)):
                    if (len(tag)==5 and tag[4]=="g"):
                        # num, inni, nni, nu
                        if (word.endswith("inni")):
                            ending = "DEF-inni"
                        elif (word.endswith("nni")):
                            ending = "DEF-nni"
                        elif (word.endswith("num")):
                            ending = "DEF-num"
                        elif (word.endswith("nu")):
                            ending = "DEF-nu"
                        else:
                            ending = "DEF-other"
                    elif (word.endswith("um")):
                        ending = "um"
                    elif (word.endswith("u")):
                        ending = "u"
                    elif (word.endswith("i")):
                        ending = "i"
                    elif (word.endswith("a")):
                        ending = "a"
                    else:
                        ending = "EMPTY"
                    if order:
                        # Sample order from qualitative distribution
                        sampled_order = np.random.choice(["order1","order2"], p=order_probs)
                        features_construction = ("dat",ending, sampled_order)
                    else:
                        features_construction = ("dat",ending)
                    construction[features_construction].append(word)
                    if len(verb_before):
                        function["verb"].append(verb_before)
                        function_construction[("verb",features_construction)].append((verb_before,word, sentence_words))
                        verb_before = ""
                    elif len(adj_before):
                        function["adj"].append(adj_before)
                        function_construction[("adj",features_construction)].append((adj_before,word, sentence_words))
                        adj_before = ""
                    elif len(adv_before):
                        function["adv"].append(adv_before)
                        function_construction[("adv",features_construction)].append((adv_before,word, sentence_words))
                        adv_before = ""
                    elif(len(pre_before) and pre_before_type == "dat"):
                        function["pre-dat"].append(pre_before)
                        function_construction[("pre-dat",features_construction)].append((pre_before,word, sentence_words))
                        pre_before = ""
                        pre_before_type = ""
                    elif (len(pre_before) and pre_before_type == "gen"):
                        function["pre-gen"].append(pre_before)
                        function_construction[("pre-gen",features_construction)].append((pre_before,word, sentence_words))
                        pre_before = ""
                        pre_before_type = ""
    
    count_function = count_dict(function)
    count_construction = count_dict(construction)
    count_f_c = count_dict(function_construction)
    
    # Write first 100 examples for every combination to pdf, to check
    if write_pdf:
        for f,c in function_construction:
            label = f + "," + c
            files.write_construction_pdf(function_construction[(f,c)][:100], label)
        files.dir_cleanup()
    return count_function, count_construction, count_f_c
    
            

def extract_constructions_qualitative(sentences, interesting_list):
    construction = []
    
    # Keep count of total possessive constructions,
    # to calculate later what the fraction of extracted interesting possessive
    # constructions is
    total_possessive = 0
    
    #go through each sentence
    for sentence in sentences:
        preposition_gen_before = ""
        preposition_dat_before = ""
        sentence_words = [word for lemma,tag,word in sentence]
        sentence_string = " ".join(sentence_words)
        for pos in range(0,len(sentence)):
            lemma,tag,word = sentence[pos]
            lemma_cmp=lemma.encode('utf-8')
            ########## Detect only nouns ###########
            # Detect genitive noun
            if (len(tag) > 3 and tag[0] == "n" and tag[3]=="e"):
                total_possessive += 1
                if lemma_cmp in interesting_list:
                    preceding_string = " ".join(sentence_words[:pos])
                    following_string = " ".join(sentence_words[pos+1:])
                    personal = ""
                    construction_name = "gen"
                    construction_details = ""
                    
                    if (len(tag)==5 and tag[4]=="g"):
                        # ins, ns, innar, nnar, nna
                        if (word.endswith("innar")):
                            construction_details = "DEF-innar"
                        elif (word.endswith("nnar")):
                            construction_details = "DEF-nnar"
                        elif (word.endswith("nna")):
                            construction_details = "DEF-nna"
                        elif (word.endswith("ins")):
                            construction_details = "DEF-ins"
                        elif (word.endswith("ns")):
                            construction_details = "DEF-ns"
                        else:
                            construction_details = "DEF-other"
                    elif (word.endswith(("s"))):
                        construction_details = "s"
                    elif (word.endswith(("ar"))):
                        construction_details = "ar"
                    elif (word.endswith(("ur"))):
                        construction_details = "ur"
                    elif (word.endswith(("na"))):
                        construction_details = "na"
                    elif (word.endswith(("u"))):
                        construction_details = "u"
                    elif (word.endswith(("a"))):
                        construction_details = "a"
                    elif (word.endswith(("i"))):
                        construction_details = "i"
                    elif (word.endswith(("r"))):
                        construction_details = "r"
                    if len(tag) == 6:
                        personal = "+PN"
                    
                    # If this is the first noun after a genitive-governing
                    # preposition, count as prepositional complement
                    if len(preposition_gen_before) > 0:
                        construction_name = "pre-gen"
                        construction_details = preposition_gen_before
                        preposition_gen_before = ""
                    
                    if len(tag) ==6:
                        # Detect linking pronoun construction,
                        # with the possessee ('fiets') at the current position
                        
                        
                        if pos < len(sentence)-2:
                            next_lemma, next_tag, next_word = sentence[pos+1]
                            next2_lemma, next2_tag, next2_word = sentence[pos+2]
                            # Option 1: 'Jans fiets zijn'
                            # pos+1: noun non-genitive
                            # pos+2: linking pronoun
                            if (next_tag[0]=="n" and next_tag[3]!="e"):
                                if (next2_lemma=="hann" and next2_tag=="fpkee") or (next2_lemma==u"hún" and next2_tag=="fpvee"):
                                    construction_name = "lpn"
                                    construction_details = ""
                            # Option 2: 'Jans zijn fiets'
                            # pos+1: linking pronoun
                            # pos+2: noun non-genitive
                            if (next_lemma=="hann" and next_tag=="fpkee") or (next_lemma==u"hún" and next_tag=="fpvee"):
                                if (next2_tag[0]=="n" and next2_tag[3]!="e"):
                                    construction_name = "lpn"
                                    construction_details = ""
                        
                        if pos >= 2:
                            # Option 3: 'fiets zijn Jans'
                            # pos-1: linking pronoun
                            # pos-2: noun non-genitive
                            prev_lemma, prev_tag, prev_word = sentence[pos-1]
                            prev2_lemma, prev2_tag, prev2_word = sentence[pos-2]
                            if (prev_lemma=="hann" and prev_tag=="fpkee") or (prev_lemma==u"hún" and prev_tag=="fpvee"):
                                if (prev2_tag[0]=="n" and prev2_tag[3]!="e"):
                                    construction_name = "lpn"
                                    construction_details = ""
                    
                    construction.append((lemma,tag,preceding_string,word,following_string, construction_name, construction_details, personal))
            # Detect dative nouns
            elif ((len(tag) > 3) and (tag[0]== "n") and (tag[3] == u"þ")):
                # Only if preposition was before,
                # and no other dative noun has occurred in between
                if len(preposition_dat_before) > 0:
                    total_possessive += 1
                    if lemma_cmp in interesting_list:
                        preceding_string = " ".join(sentence_words[:pos])
                        following_string = " ".join(sentence_words[pos+1:])
                        construction_details = ""
                        personal = ""
                        construction_name = "pre-dat"
                        construction_details = preposition_dat_before
                        if len(tag) == 6:
                            personal = "+PN"
                        construction.append((lemma,tag,preceding_string,word,following_string, construction_name, construction_details, personal))
                    preposition_dat_before = ""
            # Detect preposition
            elif ((tag == u"aþ"
            or tag == u"aþe"
            or tag == u"aþm")
            and (word in [u"til",u"í",u"á",u"af",u"frá",u"hjá",u"að"])):
                # Store use of preposition, so dative noun directly after can be captured
                preposition_dat_before = word
            elif ((tag == "ae")
            and (word in [u"til",u"í",u"á",u"af",u"frá",u"hjá",u"að"])):
                # Store use of preposition, so genitive noun directly after can be captured
                preposition_gen_before = word
    qualitative_examples = construction
    return qualitative_examples, total_possessive
    

def count_qualitative(qual_entries, order, drop_details):
    construction = defaultdict(int)
    function = defaultdict(int)
    function_construction = defaultdict(int)
    count_order1 = 0
    count_order2 = 0
    annotated_possessive = 0
    for e in qual_entries:
        if e["order"] =="order1":
            count_order1 +=1
        elif e["order"]=="order2":
            count_order2 +=2
        else:
            if order:
                # Drop entries without order, when order
                continue
        
        if order and drop_details:
            features_construction = (e["construction"],e["order"])
        elif order:
            features_construction = (e["construction"],e["construction_details"],e["order"])
        else:
            features_construction = (e["construction"],e["construction_details"])
        features_function = (e["animacy_possessor"], e["animacy_possessee"], e["alienability"])
        
        construction[features_construction] += 1
        function[features_function] +=1
        function_construction[(features_function, features_construction)] +=1
        annotated_possessive += 1
    
    count_order_tot = count_order1+count_order2
    order_probs = [count_order1/float(count_order_tot), count_order2/float(count_order_tot)]
    
    return function, construction, function_construction, annotated_possessive, order_probs

def compute_probabilities_combined(count_function_quant, count_construction_quant, count_f_c_quant, count_function_qual, count_construction_qual, count_f_c_qual, total_possessive, annotated_possessive, smoothing=None):
    
    # Scale qualitative counts, based on fraction of total
    fraction_annotated_possessive = annotated_possessive/float(total_possessive)
    # (dicts are float, because scaled counts are floating point numbers)
    count_function_qual_scaled = defaultdict(float)
    count_construction_qual_scaled = defaultdict(float)
    count_f_c_qual_scaled = defaultdict(float)
    for f in count_function_qual:
        count_function_qual_scaled[f] = count_function_qual[f] / float(fraction_annotated_possessive)
    for c in count_construction_qual:
        count_construction_qual_scaled[c] = count_construction_qual[c] / float(fraction_annotated_possessive)
    for f,c in count_f_c_qual:
        count_f_c_qual_scaled[(f,c)] = count_f_c_qual[(f,c)] / float(fraction_annotated_possessive)
    
    # Combine dictionaries of quantative counts and scaled qualitative counts
    count_function = {}
    count_construction = {}
    count_f_c = {}
    
    combined_function_keys = count_function_quant.keys() + count_function_qual_scaled.keys()
    for f in combined_function_keys:
        count_function[f] = count_function_quant[f] + count_function_qual_scaled[f]
    combined_construction_keys = count_construction_quant.keys() + count_construction_qual_scaled.keys()
    for c in combined_construction_keys:
        count_construction[c] = count_construction_quant[c] + count_construction_qual_scaled[c]
    combined_f_c_keys = count_f_c_quant.keys() + count_f_c_qual_scaled.keys()
    for f,c in combined_f_c_keys:
        count_f_c[(f,c)] = count_f_c_quant[(f,c)] + count_f_c_qual_scaled[(f,c)]
    
    return compute_probabilities(count_function, count_construction, count_f_c, smoothing=None)

def compute_probabilities(count_function, count_construction, count_f_c, smoothing=None):
    # Validity check. total counts should be the same
    count_function_total = sum(count_function[x] for x in count_function)
    count_construction_total = sum(count_construction[x] for x in count_construction)
    count_f_c_total = sum(count_f_c[x] for x in count_f_c)
    assert (abs(count_function_total - count_construction_total) < 0.001 and
    abs(count_function_total - count_f_c_total) < 0.001)
    
    # Compute probabilities
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
    
    # Check validity of probabilities in p_cond_c_f. For every f, should sum to 1.
    for check_function in count_function:
        summed_prob = 0.0
        for construction,function in p_cond_c_f:
            if function == check_function:
                summed_prob+= p_cond_c_f[(construction,function)]
        assert abs(summed_prob - 1.0) < 0.001
            
    
    return p_f, p_c, p_joint_f_c, p_cond_c_f

# Function currently not in use, just for diagnostic purposes
def compare_files():
    with open("qualitative-icelandic-justin.csv","r") as old:
        with open("qualitative-new-2000.csv","r") as new:
            old_lines = old.readlines()
            new_lines = new.readlines()
            assert len(old_lines) == len(new_lines)
            for i in range(0,len(old_lines)):
                old_line_split = old_lines[i].split(",")
                new_line_split = new_lines[i].split(",")
                if old_line_split[0] != new_line_split[0]:
                    print i, old_line_split[0], new_line_split[0]

def merge_categories(count_function, count_construction, count_f_c, lang_format, merged_functions=False, drop_details=False):
    count_function_merged = defaultdict(int)
    count_construction_merged = defaultdict(int)
    count_f_c_merged = defaultdict(int)
    
    
    visited_constructions = set()
    visited_functions = set()
    # Merge f,c
    for function,construction in count_f_c:
        new_construction = construction
        new_function = function
        if isinstance(function,basestring):
            if function.startswith("pre"):
                new_function = "pre"
        else:
            # If tuple (possessor, possessee, alienability):
            if merged_functions:
                # keep only possessor
                new_function = function[0]
        
        if merged_functions:
            # Remove preposition form
            if construction[0] == "pre":
                if len(new_construction)==3:
                    new_construction = (construction[0],"", construction[2])
                else:
                    new_construction = (construction[0],"")
            
        if lang_format == "icelandic":
            if construction[0] == "gen":
                # Redivide gen endings in -s/-r/OTHER
                if construction[1].endswith("s"):
                    if len(new_construction)==3:
                        new_construction = (construction[0],"s", construction[2])
                    else:
                        new_construction = (construction[0],"s")
                elif construction[1].endswith("r"):
                    if len(new_construction)==3:
                        new_construction = (construction[0],"r", construction[2])
                    else:
                        new_construction = (construction[0],"r")
                else:
                    if len(new_construction)==3:
                        new_construction = (construction[0],"OTHER", construction[2])
                    else:
                        new_construction = (construction[0],"OTHER")
            
            if construction[0] == "dat":
                # Redivide dat endings in -i/EMPTY/OTHER
                if construction[1].endswith("i"):
                    if len(new_construction)==3:
                        new_construction = (construction[0],"i", construction[2])
                    else:
                        new_construction = (construction[0],"i")
                elif construction[1] == "EMPTY":
                    if len(new_construction)==3:
                        new_construction = (construction[0],"EMPTY", construction[2])
                    else:
                        new_construction = (construction[0],"EMPTY")
                else:
                    if len(new_construction)==3:
                        new_construction = (construction[0],"OTHER", construction[2])
                    else:
                        new_construction = (construction[0],"OTHER")
            
        
        if lang_format == "german":
            if construction[0] == "gen":
                # Convert 'masc.st' to -s, rest to OTHER
                if construction[1] == "masc.st":
                    if len(new_construction)==3:
                        new_construction = (construction[0],"s", construction[2])
                    else:
                        new_construction = (construction[0],"s")
                else:
                    if len(new_construction)==3:
                        new_construction = (construction[0],"OTHER", construction[2])
                    else:
                        new_construction = (construction[0],"OTHER")
            
            if construction[0] == "dat":
                # All datives have type OTHER
                if len(new_construction)==3:
                    new_construction = (construction[0],"OTHER", construction[2])
                else:
                    new_construction = (construction[0],"OTHER")
        if drop_details:
            new_construction = new_construction[0]
        
        if not merged_functions or (construction[0] != "lpn" and construction[0] != "rel-pn" and function != "adv"):
            count_function_merged[new_function] += count_f_c[(function,construction)]
            count_construction_merged[new_construction] += count_f_c[(function,construction)]
            count_f_c_merged[(new_function,new_construction)] += count_f_c[(function,construction)]
    return count_function_merged, count_construction_merged, count_f_c_merged

def create_lm_german(order=True, merged = True, drop_details = False, merged_functions = False):
    filename = "lm-german"
    if order:
        filename += "-order"
    if merged:
        filename += "-merged"
    if merged_functions:
        filename += "-fmerged"
    if drop_details:
        filename += "-dropdetails"
    
    # Count qualitative, manually annotated, constructions
    qual_entries = files.read_qualitative(FLAGS.qual_intruders, lang_format="german")
    count_function_qual, count_construction_qual, count_f_c_qual, _, order_probs = count_qualitative(qual_entries, order, drop_details)
    
    
    if merged:
        # Merge categories
        mcount_function_qual, mcount_construction_qual, mcount_f_c_qual = merge_categories(count_function_qual, count_construction_qual, count_f_c_qual, lang_format="german", merged_functions=merged_functions, drop_details=drop_details)


        mp_f, mp_c, mp_joint_f_c, mp_cond_c_f = compute_probabilities(mcount_function_qual, mcount_construction_qual, mcount_f_c_qual)
        
        # Compute probabilities
        files.write_count_table(mcount_function_qual, mcount_construction_qual, mcount_f_c_qual,os.path.join(FLAGS.output_dir, "table_count_"+filename+".csv"))
        files.write_prob_table(mp_f, mp_c, mp_cond_c_f,os.path.join(FLAGS.output_dir,"table_prob_" + filename +".csv"))
        
        # Store as pickle
        files.store((mp_f, mp_c, mp_joint_f_c, mp_cond_c_f), os.path.join(FLAGS.output_dir,filename+".p"))
    else:
        p_f, p_c, p_joint_f_c, p_cond_c_f = compute_probabilities(count_function_qual, count_construction_qual, count_f_c_qual)
        files.write_count_table(count_function_qual, count_construction_qual, count_f_c_qual,os.path.join(FLAGS.output_dir,"table_count_"+filename+".csv"))
        files.write_prob_table(p_f, p_c, p_cond_c_f,os.path.join(FLAGS.output_dir,"table_prob_" + filename +".csv"))
        
        # Store as pickle
        files.store((p_f, p_c, p_joint_f_c, p_cond_c_f), os.path.join(FLAGS.output_dir,filename+".p"))

def create_lm_icelandic(merged=True, merged_functions=False, order=True, drop_details=False):
    filename = "lm-icelandic"
    if order:
        filename += "-order"
    if merged:
        filename += "-merged"
    if merged_functions:
        filename += "-fmerged"
    if drop_details:
        filename += "-dropdetails"
    
    data = files.read_corpus(FLAGS.saga_input_dir)
    
    # Qualitative analysis: extract occurrences of interesting words in corpus, which can be manually annotated
    #NOTE: We have already extracted this file in the past, and manually annotated it, that file is used in the
    # next step. We however still perform this step to get the total number of possessives in the qualitative sample.
    interesting_list = files.read_list("corpus/icelandic-interesting-modified.txt") + files.read_list("corpus/icelandic-interesting-names.txt")
    qualitative_examples, total_possessive = extract_constructions_qualitative(data, interesting_list)
    files.write_construction_csv(qualitative_examples, "qualitative-new",2000)
    
    # Count qualitative, manually annotated, constructions
    qual_entries = files.read_qualitative(FLAGS.qual_icelandic, lang_format="icelandic")
    count_function_qual, count_construction_qual, count_f_c_qual, annotated_possessive, order_probs = count_qualitative(qual_entries, order, drop_details)
    
    # Quantitative analysis
    verb_list = files.read_list("corpus/verbs_automatic.txt")
    adj_list = files.read_list("corpus/adjectives_automatic.txt")
    adv_list = files.read_list("corpus/adverbs_automatic.txt")
    count_function_quant, count_construction_quant, count_f_c_quant = count_quantitative(data, verb_list, adj_list, adv_list, order, order_probs)
    
    if merged:
        ## Merged Icelandic language model
        # Merge categories for qualitative and quantitative counts
        mcount_function_quant, mcount_construction_quant, mcount_f_c_quant = merge_categories(count_function_quant,count_construction_quant, count_f_c_quant, lang_format="icelandic", merged_functions=merged_functions, drop_details = drop_details)
        
        mcount_function_qual, mcount_construction_qual, mcount_f_c_qual = merge_categories(count_function_qual,                                                                 count_construction_qual, count_f_c_qual, lang_format="icelandic", merged_functions=merged_functions, drop_details = drop_details)
        # Compute probabilities 
        mp_f, mp_c, mp_joint_f_c, mp_cond_c_f = compute_probabilities_combined(mcount_function_quant, mcount_construction_quant, mcount_f_c_quant, mcount_function_qual, mcount_construction_qual, mcount_f_c_qual, total_possessive, annotated_possessive)
        
        # Write human-readable count and probability tables
        files.write_count_table(mcount_function_quant, mcount_construction_quant, mcount_f_c_quant,os.path.join(FLAGS.output_dir,"table_count_quant_"+filename+".csv"))
        files.write_count_table(mcount_function_qual, mcount_construction_qual, mcount_f_c_qual,os.path.join(FLAGS.output_dir,"table_count_qual_"+filename+".csv"))
        files.write_prob_table(mp_f, mp_c, mp_cond_c_f,os.path.join(FLAGS.output_dir,"table_prob_" + filename +".csv"))
        # Store as pickle
        files.store((mp_f, mp_c, mp_joint_f_c, mp_cond_c_f), os.path.join(FLAGS.output_dir,filename+".p"))
    else:
        # Compute probabilities 
        p_f, p_c, p_joint_f_c, p_cond_c_f = compute_probabilities_combined(count_function_quant, count_construction_quant, count_f_c_quant, count_function_qual, count_construction_qual, count_f_c_qual, total_possessive, annotated_possessive)
        # Write human-readable count and probability tables
        files.write_count_table(count_function_quant, count_construction_quant, count_f_c_quant,os.path.join(FLAGS.output_dir,"table_count_quant_"+filename+".csv"))
        files.write_count_table(count_function_qual, count_construction_qual, count_f_c_qual,os.path.join(FLAGS.output_dir,"table_count_qual_"+filename+".csv"))
        files.write_prob_table(p_f, p_c, p_cond_c_f,os.path.join(FLAGS.output_dir,"table_prob_" + filename +".csv"))
        
        ## Store as pickle
        files.store((p_f, p_c, p_joint_f_c, p_cond_c_f), os.path.join(FLAGS.output_dir,filename+".p"))

def main():
    # Create output dir, if it does not yet exist
    try: 
        os.makedirs(FLAGS.output_dir)
    except OSError:
        if not os.path.isdir(FLAGS.output_dir):
            raise
    
    choice = [False, True]
    for order in choice:
        for drop_details in choice:
            for merged_functions in choice:
                create_lm_icelandic(merged=True, order=order, drop_details=drop_details, merged_functions=merged_functions)
                if len(FLAGS.qual_intruders)>0:
                    create_lm_german(merged=True, order=order, drop_details=drop_details, merged_functions=merged_functions)
    
if __name__ == "__main__":
    # Command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--saga_input_dir', type = str, default=SAGA_INPUT_DIR)
    parser.add_argument('--qual_icelandic', type = str, required=True)
    parser.add_argument('--qual_intruders', type = str, default="")
    parser.add_argument('--output_dir', type = str, default=OUTPUT_DIR)
    FLAGS, unparsed = parser.parse_known_args()
    utility.print_flags(FLAGS)
    main()
