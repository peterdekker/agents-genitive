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
        
    
def collect_counts(sentences, interesting_list):
    construction = defaultdict(list)
    function = defaultdict(list)
    constr_func = defaultdict(lambda: defaultdict(list))
    qualitative_constr = defaultdict(list)
     
    genitive = []
    dative = []
    for sentence in sentences:
        sentence_words = [word for lemma,tag,word in sentence]
        sentence_string = " ".join(sentence_words)
        for pos in range(0,len(sentence)):
            lemma,tag,word = sentence[pos]
            # Detect genitive nouns
            if len(tag) > 3:
                if (tag[0] == "n" and tag[3]=="e"):
                    preceding_string = " ".join(sentence_words[:pos])
                    following_string = " ".join(sentence_words[pos+1:])
                    construction["gen_common_noun"].append((lemma,tag,preceding_string,word,following_string))
                elif ((tag [0]== "n") and ((tag[3] == "þ"))):
                    preceding_string = " ".join(sentence_words[:pos])
                    following_string = " ".join(sentence_words[pos+1:])
                    construction["dat_common_noun"].append((lemma,tag,preceding_string,word,following_string))
                    
            
            # Detect genitive
            if len(tag) > 3 :
                if ((tag [0]== "n") and (tag[3]=="e") # noun genitive
                    or (tag[0] == "f" and tag[4]=="e")    # pronoun genitive
                    or (tag[0] == "l" and tag[3]=="e")    # adjective genitive
                    or (tag[0] == "g" and tag[3]=="e")    # article genitive
                    or (tag[0] == "t" and tag[4]=="e")    # number genitive
                    or (word == "og" and len(genitive) >0)): # 'og' may occur in genitive, as second or later
                        # TODO: look at excluding gen. pronoun "hans" from list
                        genitive.append((word,pos))
                elif ((tag [0]== "n") and ((tag[3] == "þ")) # noun dative
                    or (tag[0] == "f" and tag[4]=="þ")    # pronoun dative
                    or (tag[0] == "l" and tag[3]=="þ")    # adjective dative
                    or (tag[0] == "g" and tag[3]=="þ")    # article dative
                    or (tag[0] == "t" and tag[4]=="þ")    # number dative
                    or (word == "og" and len(dative) >0)): # 'og' may occur in dative, as second or later
                        # TODO: look at excluding gen. pronoun "hans" from list
                        dative.append((word,pos))
                else:
                    # If a genitive has built up, it is now ended
                    if len(genitive) > 0:
                        start_pos = genitive[0][1]
                        end_pos = genitive[-1][1]
                        genitive_string = " ".join([word for word,pos in genitive])
                        preceding_string = " ".join(sentence_words[:start_pos])
                        following_string = " ".join(sentence_words[end_pos+1:])
                        construction["gen"].append((preceding_string,genitive_string,following_string))
                        genitive = []
                    # If a genitive has built up, it is now ended
                    elif len(dative) > 0:
                        start_pos = dative[0][1]
                        end_pos = dative[-1][1]
                        dative_string = " ".join([word for word,pos in genitive])
                        preceding_string = " ".join(sentence_words[:start_pos])
                        following_string = " ".join(sentence_words[end_pos+1:])
                        construction["dat"].append((preceding_string,dative_string,following_string))
                        dative = []
            
            # Detect interesting words
            if lemma in interesting_list:
                qualitative_constr[lemma].append((tag, sentence_string))
    
    # Write to files
    io.write_interesting_words_csv(qualitative_constr, "interesting_output")
    io.write_word_csv(construction["gen_common_noun"], "genitive_common_noun",1000)
    io.write_word_csv(construction["dat_common_noun"], "dative_common_noun",1000)
    io.write_construction_csv(construction["gen"], "Genitive",1000)
    io.write_construction_csv(construction["dat"], "Dative",1000)
    #io.write_construction_pdf(construction["gen"], "Genitive",1000)
    
    # Output entries from interesting list that have not been found in corpus
    check_missing(qualitative_constr, interesting_list)

if __name__ == "__main__":
    data = io.read_data("Saga")
    interesting_list = io.read_interesting_list("icelandic-interesting-modified.txt")
    collect_counts(data, interesting_list)
