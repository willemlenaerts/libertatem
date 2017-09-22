# GBR Combine
# Combine wiki/topo/election data to TOPO ADM1 -- ELDATA CONSTITUENCIES csv file
# TO DO: clean "wiki_const_to_eldata_const.csv"
import pandas as pd
import csv
a = pd.read_csv("geodata/ElectionHistory/input/CountryData/GBR/wiki_const_to_eldata_const.csv")
b = pd.read_csv("geodata/ElectionHistory/input/CountryData/GBR/wiki_const_to_wiki_adm1.csv",sep=";")
c = pd.read_csv("geodata/ElectionHistory/input/CountryData/GBR/wiki_adm1_to_topo_adm1.csv")

with open('geodata/ElectionHistory/input/CountryData/' + "GBR" + '/' + "GBR" + '_constituencies.csv', "w", newline='') as fp:
    wr = csv.writer(fp, delimiter=',')
    wr.writerow(["ADM1","Constituency"])
    a_done = []
    for i in range(len(a)):
        el_co = a.eldata_const.iloc[i]
        if el_co not in a_done:
            a_done.append(el_co)
            wiki_consts = a[a.eldata_const == el_co].wiki_const.tolist()
            for wiki_const in wiki_consts:
                wiki_adms = b[b.Constituency == wiki_const].ADM1.tolist()
                for wiki_adm in wiki_adms:
                    topo_adms = c[c.wiki_adm1 == wiki_adm].topo_adm1.tolist()
                    for topo_adm in topo_adms:
                        wr.writerow([topo_adm,el_co])