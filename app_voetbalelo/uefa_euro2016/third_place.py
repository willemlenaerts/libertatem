import pickle

third_place_rules = dict()

third_place_rules["ABCD"] = dict()
third_place_rules["ABCD"]["A"] = "C"
third_place_rules["ABCD"]["B"] = "D"
third_place_rules["ABCD"]["C"] = "A"
third_place_rules["ABCD"]["D"] = "B"

third_place_rules["ABCE"] = dict()
third_place_rules["ABCE"]["A"] = "C"
third_place_rules["ABCE"]["B"] = "A"
third_place_rules["ABCE"]["C"] = "B"
third_place_rules["ABCE"]["D"] = "E"

third_place_rules["ABCF"] = dict()
third_place_rules["ABCF"]["A"] = "C"
third_place_rules["ABCF"]["B"] = "A"
third_place_rules["ABCF"]["C"] = "B"
third_place_rules["ABCF"]["D"] = "F"

third_place_rules["ABDE"] = dict()
third_place_rules["ABDE"]["A"] = "D"
third_place_rules["ABDE"]["B"] = "A"
third_place_rules["ABDE"]["C"] = "B"
third_place_rules["ABDE"]["D"] = "E"

third_place_rules["ABDF"] = dict()
third_place_rules["ABDF"]["A"] = "D"
third_place_rules["ABDF"]["B"] = "A"
third_place_rules["ABDF"]["C"] = "B"
third_place_rules["ABDF"]["D"] = "F"

third_place_rules["ABEF"] = dict()
third_place_rules["ABEF"]["A"] = "E"
third_place_rules["ABEF"]["B"] = "A"
third_place_rules["ABEF"]["C"] = "B"
third_place_rules["ABEF"]["D"] = "F"

third_place_rules["ACDE"] = dict()
third_place_rules["ACDE"]["A"] = "C"
third_place_rules["ACDE"]["B"] = "D"
third_place_rules["ACDE"]["C"] = "A"
third_place_rules["ACDE"]["D"] = "E"

third_place_rules["ACDF"] = dict()
third_place_rules["ACDF"]["A"] = "C"
third_place_rules["ACDF"]["B"] = "D"
third_place_rules["ACDF"]["C"] = "A"
third_place_rules["ACDF"]["D"] = "F"

third_place_rules["ACEF"] = dict()
third_place_rules["ACEF"]["A"] = "C"
third_place_rules["ACEF"]["B"] = "A"
third_place_rules["ACEF"]["C"] = "F"
third_place_rules["ACEF"]["D"] = "E"

third_place_rules["ADEF"] = dict()
third_place_rules["ADEF"]["A"] = "D"
third_place_rules["ADEF"]["B"] = "A"
third_place_rules["ADEF"]["C"] = "F"
third_place_rules["ADEF"]["D"] = "E"

third_place_rules["BCDE"] = dict()
third_place_rules["BCDE"]["A"] = "C"
third_place_rules["BCDE"]["B"] = "D"
third_place_rules["BCDE"]["C"] = "B"
third_place_rules["BCDE"]["D"] = "E"

third_place_rules["BCDF"] = dict()
third_place_rules["BCDF"]["A"] = "C"
third_place_rules["BCDF"]["B"] = "D"
third_place_rules["BCDF"]["C"] = "B"
third_place_rules["BCDF"]["D"] = "F"

third_place_rules["BCEF"] = dict()
third_place_rules["BCEF"]["A"] = "E"
third_place_rules["BCEF"]["B"] = "C"
third_place_rules["BCEF"]["C"] = "B"
third_place_rules["BCEF"]["D"] = "F"

third_place_rules["BDEF"] = dict()
third_place_rules["BDEF"]["A"] = "E"
third_place_rules["BDEF"]["B"] = "D"
third_place_rules["BDEF"]["C"] = "B"
third_place_rules["BDEF"]["D"] = "F"

third_place_rules["CDEF"] = dict()
third_place_rules["CDEF"]["A"] = "C"
third_place_rules["CDEF"]["B"] = "D"
third_place_rules["CDEF"]["C"] = "F"
third_place_rules["CDEF"]["D"] = "E"

pickle.dump(third_place_rules,open("app_voetbalelo/uefa_euro2016/data/third_place_rules.p","wb"))