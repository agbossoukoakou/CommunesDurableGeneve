# Dechets par habitant 

# Import de librairie
import pandas as pd
annees = [str(annee) for annee in range(2003, 2022)]

Data_dechets= []
for annee in annees:
    data_d = pd.read_excel(
        "Dechet_par_habitant.xls",
        sheet_name=annee,        
        skiprows=1,              
        usecols="A:B",          
        header=None,             
        names=["Commune", "Dechet_par_habitant_kg"]
    )
    data_d["Année"] = int(annee)     
    Data_dechets.append(data_d) 

Data_dechets_final = pd.concat(Data_dechets, ignore_index=True)

print(Data_dechets_final)
print(type(Data_dechets_final))



Data_dechets_final = Data_dechets_final [["Commune", "Année", "Dechet_par_habitant_kg"]]
Data_dechets_final = Data_dechets_final.sort_values(by=["Commune", "Année"])

Data_dechets_final = Data_dechets_final.reset_index(drop=True)
Data_dechets_final.to_csv("donnees_dechet_par_habitant.csv")





