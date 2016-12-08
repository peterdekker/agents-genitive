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
        possessor_in_sentence = False
        preposition_before = False
        sentence_words = [word for lemma,tag,word in sentence]
        possessee_candidates = list(sentence)
        sentence_string = " ".join(sentence_words)
        for pos in range(0,len(sentence)):
            lemma,tag,word = sentence[pos]
            lemma_cmp=lemma.encode('utf-8')
            ########## Detect only nouns ###########
            # Detect genitive noun
            if (len(tag) > 3 and tag[0] == "n" and tag[3]=="e"):
                possessor_in_sentence = True
                if lemma_cmp in interesting_list:
                    preceding_string = " ".join(sentence_words[:pos])
                    following_string = " ".join(sentence_words[pos+1:])
                    ending = ""
                    role = "possessor"
                    personal = ""
                    construction_name = "gen"
                    if (word.endswith("innar") or word.endswith("nnar") or word.endswith("nna") or word.endswith("ins") or word.endswith("ns")):
                        ending = "DEF"
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
                    construction.append((lemma,tag,preceding_string,word,following_string, construction_name, ending, role, personal))
            # Detect dative nouns
            elif ((len(tag) > 3) and (tag[0]== "n") and (tag[3] == u"þ")):
                # Only if preposition was before,
                # and no other dative noun has occurred in between
                if preposition_before == True:
                    preposition_before = False
                    if lemma_cmp in interesting_list:
                        preceding_string = " ".join(sentence_words[:pos])
                        following_string = " ".join(sentence_words[pos+1:])
                        ending = ""
                        role = "possessor"
                        personal = ""
                        construction_name = "pre"
                        if (word.endswith("inni") or word.endswith("nni") or word.endswith("num") or word.endswith("nu")):
                            ending = "DEF"
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
                        construction.append((lemma,tag,preceding_string,word,following_string, construction_name, ending, role, personal))
            # Detect preposition
            elif ((tag == "ae"
            or tag == u"aþ"
            or tag == u"aþe"
            or tag == u"aþm")
            and (word in [u"til",u"í",u"á",u"af",u"frá",u"hjá",u"að"])):
                # Store use of preposition, so dative directly after can be captured
                preposition_before = True
                possessor_in_sentence = True
            
        # Re-run over sentence to find possessees, only if there was a possessor in the sentence
        if possessor_in_sentence:
            for pos in range(0,len(sentence)):
                lemma,tag,word = sentence[pos]
                lemma_cmp=lemma.encode('utf-8')
                if lemma_cmp in interesting_list:
                    # Detect nominative or accussative nouns, which are probably possessee
                    if (len(tag) > 3 and tag[0] == "n" and (tag[3]=="n" or tag[3]=="o")):
                        preceding_string = " ".join(sentence_words[:pos])
                        following_string = " ".join(sentence_words[pos+1:])
                        ending = ""
                        role = "possessee"
                        personal = ""
                        construction_name = ""
                        if len(tag) == 6:
                                personal = "+PN"
                        
                        # Detect linking pronoun construction,
                        # with the possessee ('fiets') at the current position
                        
                        # Option 1: 'Jans fiets zijn'
                        # pos+1: linking pronoun
                        # pos-1: personal noun genitive
                        if pos > 0 and pos < len(sentence)-1:
                            prev_lemma, prev_tag, prev_word = sentence[pos-1]
                            next_lemma, next_tag, next_word = sentence[pos+1]
                            if (next_lemma=="hann" and next_tag=="fpkee") or (next_lemma==u"hún" and next_tag=="fpvee"):
                                if (prev_tag[0]=="n" and len(prev_tag)==6 and prev_tag[3]=="e"):
                                    construction_name = "lpn"
                            
                            if pos < len(sentence)-2:
                                # Option 2: 'fiets zijn Jans'
                                # pos+1: linking pronoun
                                # pos+2: personal noun genitive
                                next2_lemma, next2_tag, next2_word = sentence[pos+2]
                                if (next_lemma=="hann" and next_tag=="fpkee") or (next_lemma==u"hún" and next_tag=="fpvee"):
                                    if (next2_tag[0]=="n" and len(next2_tag)==6 and next2_tag[3]=="e"):
                                        construction_name = "lpn"
                            if pos > 1:
                                # Option 3: 'Jans zijn fiets'
                                # pos-1: linking pronoun
                                # pos-2: personal noun genitive
                                prev2_lemma, prev2_tag, prev2_word = sentence[pos-2]
                                if (prev_lemma=="hann" and prev_tag=="fpkee") or (prev_lemma==u"hún" and prev_tag=="fpvee"):
                                    if (prev2_tag[0]=="n" and len(prev2_tag)==6 and prev2_tag[3]=="e"):
                                        construction_name = "lpn"
                            
                        construction.append((lemma,tag,preceding_string,word,following_string, construction_name, ending, role, personal))
    
    # Write to files
    io.write_construction_csv(construction, "qualitative",1000)




if __name__ == "__main__":
    data = io.read_data("Saga")
    interesting_list = io.read_interesting_list("icelandic-interesting-modified.txt")
    extract_constructions_qualitative(data, interesting_list)
