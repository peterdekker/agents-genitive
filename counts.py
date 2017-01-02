# -*- coding: utf-8 -*-


from collections import defaultdict

import utility
from utility import print_sorted
import files

def count_dict(dct):
    count = defaultdict(int)
    for key in dct:
        count[key] = len(dct[key])
    
    return count

def count_quantitative(sentences, verb_list, adj_list, adv_list, write_pdf=False):
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
                    features_construction = ("gen", ending)
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
    

def count_qualitative(qual_entries):
    construction = defaultdict(int)
    function = defaultdict(int)
    function_construction = defaultdict(int)
    
    for e in qual_entries:
        if "order" in e:
            features_construction = (e["construction"], e["order"])
        else:
            features_construction = (e["construction"],e["construction_details"])
        features_function = (e["animacy_possessor"], e["animacy_possessee"], e["alienability"])
        
        construction[features_construction] += 1
        function[features_function] +=1
        function_construction[(features_function, features_construction)] +=1
    annotated_possessive = len(qual_entries)
    return function, construction, function_construction, annotated_possessive

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

def merge_categories(count_function, count_construction, count_f_c):
    count_function_merged = defaultdict(int)
    count_construction_merged = defaultdict(int)
    count_f_c_merged = defaultdict(int)
    
    
    visited_constructions = set()
    visited_functions = set()
    # Merge f,c
    for function,construction in count_f_c:
        new_construction = construction
        new_function = function
        if isinstance(function,basestring) and function.startswith("pre"):
            new_function = "pre"
        
        if construction[0] == "gen":
            # Redivide gen endings in -s/-r/OTHER
            if construction[1].endswith("s"):
                new_construction = (construction[0],"s")
            elif construction[1].endswith("r"):
                new_construction = (construction[0],"r")
            else:
                new_construction = (construction[0],"OTHER")
        
        if construction[0] == "dat":
            # Redivide dat endings in -i/EMPTY/OTHER
            if construction[1].endswith("i"):
                new_construction = (construction[0],"i")
            elif construction[1] == "EMPTY":
                new_construction = (construction[0],"EMPTY")
            else:
                new_construction = (construction[0],"OTHER")
        
        if function not in visited_functions:
            count_function_merged[new_function] += count_function[function]
            visited_functions.add(function)
        if construction not in visited_constructions:
            count_construction_merged[new_construction] += count_construction[construction]
            visited_constructions.add(construction)
        count_f_c_merged[(new_function,new_construction)] += count_f_c[(function,construction)]
    return count_function_merged, count_construction_merged, count_f_c_merged

def create_lm_german():
    # Count qualitative, manually annotated, constructions
    qual_entries = files.read_qualitative("mlg-stats.csv", lang_format="german")
    count_function_qual, count_construction_qual, count_f_c_qual, annotated_possessive = count_qualitative(qual_entries)
    
    print_sorted(count_function_qual)
    print_sorted(count_construction_qual)
    print_sorted(count_f_c_qual)
    files.write_count_table(count_function_qual, count_construction_qual, count_f_c_qual,"table_fc_german.csv")
    
    
    print "PROBS:"
    p_f, p_c, p_joint_f_c, p_cond_c_f = compute_probabilities(count_function_qual, count_construction_qual, count_f_c_qual)
    print_sorted(p_f)
    print_sorted(p_c)
    print_sorted(p_cond_c_f)
    files.write_prob_table(p_f, p_c, p_cond_c_f,"table_prob_german.csv")
def create_lm_icelandic():
    
    ### Icelandic
    data = files.read_corpus("Saga")
    
    # Qualitative analysis: extract occurrences of interesting words in corpus, which can be manually annotated
    interesting_list = files.read_list("icelandic-interesting-modified.txt") + files.read_list("icelandic-interesting-names.txt")
    qualitative_examples, total_possessive = extract_constructions_qualitative(data, interesting_list)
    files.write_construction_csv(qualitative_examples, "qualitative-new",2000)
    
    # Quantitative analysis
    verb_list = files.read_list("verbs_automatic.txt")
    adj_list = files.read_list("adjectives_automatic.txt")
    adv_list = files.read_list("adverbs_automatic.txt")
    count_function_quant, count_construction_quant, count_f_c_quant = count_quantitative(data, verb_list, adj_list, adv_list)
    
    
    
    # Count qualitative, manually annotated, constructions
    qual_entries = files.read_qualitative("qualitative-icelandic-justin.csv", lang_format="icelandic")
    count_function_qual, count_construction_qual, count_f_c_qual, annotated_possessive = count_qualitative(qual_entries)

    
    ## Regular Icelandic language model
    # Compute probabilities 
    p_f, p_c, p_joint_f_c, p_cond_c_f = compute_probabilities_combined(count_function_quant, count_construction_quant, count_f_c_quant, count_function_qual, count_construction_qual, count_f_c_qual, total_possessive, annotated_possessive)

    
    
    ## Store as pickle
    files.store((p_f, p_c, p_joint_f_c, p_cond_c_f), "lm-icelandic.p")
    
    
    ## Merged Icelandic language model
    # Merge categories for qualitative and quantitative counts
    mcount_function_quant, mcount_construction_quant, mcount_f_c_quant = merge_categories(count_function_quant,                                                                 count_construction_quant, count_f_c_quant)
    
    mcount_function_qual, mcount_construction_qual, mcount_f_c_qual = merge_categories(count_function_qual,                                                                 count_construction_qual, count_f_c_qual)
    # Compute probabilities 
    mp_f, mp_c, mp_joint_f_c, mp_cond_c_f = compute_probabilities_combined(mcount_function_quant, mcount_construction_quant, mcount_f_c_quant, mcount_function_qual, mcount_construction_qual, mcount_f_c_qual, total_possessive, annotated_possessive)
    
    print_sorted(mcount_construction_qual)
    print_sorted(mcount_construction_quant)
    print_sorted(mp_c)
    # Store as pickle
    files.store((mp_f, mp_c, mp_joint_f_c, mp_cond_c_f), "lm-icelandic-merged.p")
    
    
if __name__ == "__main__":
    #create_lm_icelandic()
    create_lm_german()
