# Input: 2 lists of teams
# Output: dict with names_one as keys and names_two as values

def crossmatch_names(names_one,names_two):
    import distance
    from fuzzywuzzy import fuzz
    from fuzzywuzzy import process
    import re
    
    output = dict()
    
    for name_one in names_one:
        match = False
        # STEP ONE: LOOK FOR FULL MATCH
        for name_two in names_two:
            if fuzz.ratio(name_one.lower(),name_two.lower()) == 100:
                output[name_one] = name_two
                match = True
                break    
        
        # STEP TWO: LOOK FOR FULL MATCH AFTER SPLITTING #
        if match == False:
            if "#" in name_one:
                for name_two in names_two:
                    if fuzz.ratio(name_one.split("#")[0].lower(),name_two.lower()) == 100:
                        output[name_one] = name_two
                        match = True
                        break              
                    if fuzz.ratio(name_one.split("#")[1].lower(),name_two.lower()) == 100:
                        output[name_one] = name_two
                        match = True
                        break         
    
        # STEP THREE: LOOK FOR FULL MATCH AFTER REMOVING (...)
        if match == False:    
            regex = re.compile(".*?\((.*?)\)")
            text_between_parentheses_name_one = re.findall(regex, name_one)
            
            for name_two in names_two:
                text_between_parentheses_name_two = re.findall(regex, name_two)
                if text_between_parentheses_name_one != [] or text_between_parentheses_name_two != []:
                    try:
                        name_one_no_parentheses = name_one.replace(" (" + text_between_parentheses_name_one[0] + ")","")
                    except:
                        name_one_no_parentheses = name_one
                    
                    try:
                        name_two_no_parentheses = name_two.replace(" (" + text_between_parentheses_name_two[0] + ")","")
                    except:
                        name_two_no_parentheses = name_two
                
                    if fuzz.ratio(name_one_no_parentheses.lower(),name_two_no_parentheses.lower()) == 100:
                        output[name_one] = name_two
                        match = True
                        break        
            
        # STEP FOUR: USE BRUTE FORCE PROCESS
        if match == False:    
            output[name_one] = process.extract(name_one,names_two,limit=1)[0][0]
    
    # # TEST
    # test = dict()
    # for name in output.keys():
    #     if name != output[name]:
    #         test[name] = output[name]

    return output