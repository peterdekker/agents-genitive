

def print_sorted(dct):
    print sorted(dct.items(), key=lambda x: x[1], reverse=True)
    print

def print_table_p_cond(p_cond):
    c_list = []
    f_list = []
    for c,f in p_cond:
        c_list.append(c)
        f_list.append(f)
    header = ""
    for c in c_list:
        header+="&"+str(c)
    header += "\n"
    print header
    
    for f in f_list:
        line = f
        for c in c_list:
            line += "&" + str(p_cond[(c,f)])
        line += "\n"
        print line
        
        
        
