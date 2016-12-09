# -*- coding: utf-8 -*-


from collections import defaultdict


import io

def check_missing(part, complete):
    missing = []
    for entry in complete:
        if entry not in part:
            missing.append(entry)
    
    if len(missing) > 0:
        print "Missing:"
        for m in missing:
            print m
        



def extract_constructions_qualitative(sentences, interesting_list):
    construction = []

    #go through each sentence
    for sentence in sentences:
        preposition_gen_before = False
        preposition_dat_before = False
        sentence_words = [word for lemma,tag,word in sentence]
        possessee_candidates = list(sentence)
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
    interesting_list = io.read_interesting_list("icelandic-interesting-modified.txt") + io.read_interesting_list("icelandic-interesting-names.txt")
    extract_constructions_qualitative(data, interesting_list)
