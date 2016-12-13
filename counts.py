# -*- coding: utf-8 -*-


from collections import defaultdict


import io

def count_dict(dct, sorted_list = False):
    count = {}
    for key in dct:
        count[key] = len(dct[key])
    if sorted_list:
        count = sorted(count.items(), key=lambda x: x[1], reverse=True)
    
    return count

def count_constructions_quantitative(sentences, verb_list, adj_list, adv_list):
    construction = defaultdict(list)
    function = defaultdict(list)
    function_construction = defaultdict(list)
    
    verb_before = False
    adjective_before = False

    for sentence in sentences:
        verb_before = ""
        adj_before = ""
        adv_before = ""
        pre_before = ""
        sentence_words = [word for lemma,tag,word in sentence]
        sentence_string = " ".join(sentence_words)
        for pos in range(0,len(sentence)):
            lemma,tag,word = sentence[pos]
            lemma_cmp=lemma.encode('utf-8')
            
            ### Functions
            # Match verb
            if (tag[0] == "s"):
                if lemma_cmp in verb_list:
                    verb_before = word
            
            # Match adjective (nom or acc)
            if (tag[0] == "l" and (tag[3]=="n" or tag[3]=="o")):
                if lemma_cmp in adj_list:
                    adj_before = word
            
            # Match adverb
            if (tag.startswith("aa")):
                if lemma_cmp in adv_list:
                    adv_before = word
            
            # TODO: Match prepositions
            
            ### Constructions
            # Now, look which constructions occur after a certain function
            
            # Preposition
            if ((tag == u"aþ"
            or tag == u"aþe"
            or tag == u"aþm")
            and (word in [u"til",u"í",u"á",u"af",u"frá",u"hjá",u"að"])):
                if len(verb_before) or len(adj_before) or len(adv_before):
                    construction["pre"].append(word)
                    if len(verb_before):
                        function["verb"].append(verb_before)
                        function_construction[("verb","pre")].append((verb_before,word, sentence_words))
                        verb_before = ""
                    elif len(adj_before):
                        function["adj"].append(adj_before)
                        function_construction[("adj","pre")].append((adj_before,word, sentence_words))
                        adj_before = ""
                    elif len(adv_before):
                        function["adv"].append(adv_before)
                        function_construction[("adv","pre")].append((adv_before,word, sentence_words))
                        adv_before = ""
            
            # Genitive noun
            elif (len(tag) > 3 and tag[0] == "n" and tag[3]=="e"):
                if (len(verb_before) or len(adj_before) or len(adv_before) or len(pre_before)):
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
                    gen_category = "gen-" + ending
                    construction[gen_category].append(word)
                    if len(verb_before):
                        function["verb"].append(verb_before)
                        function_construction[("verb",gen_category)].append((verb_before,word, sentence_words))
                        verb_before = ""
                    elif len(adj_before):
                        function["adj"].append(adj_before)
                        function_construction[("adj",gen_category)].append((adj_before,word, sentence_words))
                        adj_before = ""
                    elif len(adv_before):
                        function["adv"].append(adv_before)
                        function_construction[("adv",gen_category)].append((adv_before,word, sentence_words))
                        adv_before = ""
                    elif len(pre_before):
                        function["pre"].append(pre_before)
                        function_construction[("pre",gen_category)].append((pre_before,word, sentence_words))
                        pre_before = ""
            
            # Dative noun
            elif ((len(tag) > 3) and (tag[0]== "n") and (tag[3] == u"þ")):
                if (len(verb_before) or len(adj_before) or len(adv_before) or len(pre_before)):
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
                    dat_category = "dat-" + ending
                    construction[dat_category].append(word)
                    if len(verb_before):
                        function["verb"].append(verb_before)
                        function_construction[("verb",dat_category)].append((verb_before,word, sentence_words))
                        verb_before = ""
                    elif len(adj_before):
                        function["adj"].append(adj_before)
                        function_construction[("adj",dat_category)].append((adj_before,word, sentence_words))
                        adj_before = ""
                    elif len(adv_before):
                        function["adv"].append(adv_before)
                        function_construction[("adv",dat_category)].append((adv_before,word, sentence_words))
                        adv_before = ""
                    elif len(pre_before):
                        function["pre"].append(pre_before)
                        function_construction[("pre",dat_category)].append((pre_before,word, sentence_words))
                        pre_before = ""
    
    counts_function = count_dict(function, sorted_list = True)
    counts_construction = count_dict(construction, sorted_list = True)
    counts_f_c = count_dict(function_construction, sorted_list = True)
    
    print "FUNCTION"
    print counts_function
    print
    print "CONSTRUCTION"
    print counts_construction
    print
    print "FUNCTION,CONSTRUCTION"
    print counts_f_c
    print
    for f,c in function_construction:
        label = f + "," + c
        io.write_construction_pdf(function_construction[(f,c)], label)
            

def extract_constructions_qualitative(sentences, interesting_list):
    construction = []

    #go through each sentence
    for sentence in sentences:
        preposition_gen_before = False
        preposition_dat_before = False
        sentence_words = [word for lemma,tag,word in sentence]
        sentence_string = " ".join(sentence_words)
        for pos in range(0,len(sentence)):
            lemma,tag,word = sentence[pos]
            lemma_cmp=lemma.encode('utf-8')
            ########## Detect only nouns ###########
            # Detect genitive noun
            if (len(tag) > 3 and tag[0] == "n" and tag[3]=="e"):
                if lemma_cmp in interesting_list:
                    preceding_string = " ".join(sentence_words[:pos])
                    following_string = " ".join(sentence_words[pos+1:])
                    ending = ""
                    personal = ""
                    construction_name = "gen"
                    
                    # If this is the first noun after a genitive-governing
                    # preposition, count as prepositional complement
                    if preposition_gen_before == True:
                        preposition_gen_before = False
                        construction_name = "pre-gen"
                        
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
                            # Option 2: 'Jans zijn fiets'
                            # pos+1: linking pronoun
                            # pos+2: noun non-genitive
                            if (next_lemma=="hann" and next_tag=="fpkee") or (next_lemma==u"hún" and next_tag=="fpvee"):
                                if (next2_tag[0]=="n" and next2_tag[3]!="e"):
                                    construction_name = "lpn"
                        
                        if pos >= 2:
                            # Option 3: 'fiets zijn Jans'
                            # pos-1: linking pronoun
                            # pos-2: noun non-genitive
                            prev_lemma, prev_tag, prev_word = sentence[pos-1]
                            prev2_lemma, prev2_tag, prev2_word = sentence[pos-2]
                            if (prev_lemma=="hann" and prev_tag=="fpkee") or (prev_lemma==u"hún" and prev_tag=="fpvee"):
                                if (prev2_tag[0]=="n" and prev2_tag[3]!="e"):
                                    construction_name = "lpn"
                                   
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
                    if len(tag) == 6:
                        personal = "+PN"
                    construction.append((lemma,tag,preceding_string,word,following_string, construction_name, ending, personal))
            # Detect dative nouns
            elif ((len(tag) > 3) and (tag[0]== "n") and (tag[3] == u"þ")):
                # Only if preposition was before,
                # and no other dative noun has occurred in between
                if preposition_dat_before == True:
                    preposition_dat_before = False
                    if lemma_cmp in interesting_list:
                        preceding_string = " ".join(sentence_words[:pos])
                        following_string = " ".join(sentence_words[pos+1:])
                        ending = ""
                        personal = ""
                        construction_name = "pre-dat"
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
                        if len(tag) == 6:
                            personal = "+PN"
                        construction.append((lemma,tag,preceding_string,word,following_string, construction_name, ending, personal))
            # Detect preposition
            elif ((tag == u"aþ"
            or tag == u"aþe"
            or tag == u"aþm")
            and (word in [u"til",u"í",u"á",u"af",u"frá",u"hjá",u"að"])):
                # Store use of preposition, so dative noun directly after can be captured
                preposition_dat_before = True
            elif ((tag == "ae")
            and (word in [u"til",u"í",u"á",u"af",u"frá",u"hjá",u"að"])):
                # Store use of preposition, so genitive noun directly after can be captured
                preposition_gen_before = True
    
    # Write to files
    io.write_construction_csv(construction, "qualitative",2000)




if __name__ == "__main__":
    data = io.read_data("Saga")
    
    # Qualitative analysis: extract occurrences of interesting words in corpus, which can be manually annotated
    #interesting_list = io.read_list("icelandic-interesting-modified.txt") + io.read_list("icelandic-interesting-names.txt")
    #extract_constructions_qualitative(data, interesting_list)
    
    # Quantitative analysis
    verb_list = io.read_list("verbs_automatic.txt")
    adj_list = io.read_list("adjectives_automatic.txt")
    adv_list = io.read_list("adverbs_automatic.txt")
    count_constructions_quantitative(data, verb_list, adj_list, adv_list)
