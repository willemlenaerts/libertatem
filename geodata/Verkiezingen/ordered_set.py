# This function returns unique elements in list, like "list(set())",
# but now in ORDERED form

# Essential because kieskantons_belgie.csv is ordered chronologically
# Older kanton/arrondissement/... more down in list

def ordered_set(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]