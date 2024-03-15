import pandas as pd

def data_import(file_name):
    data_frame = pd.read_csv(file_name, encoding='utf-8')
    data_frame.columns = ["Odpověď",
                          "Odesláno",
                          "Instituce",
                          "Oddělení",
                          "Kurz",
                          "Skupina",
                          "ID",
                          "Celý_název",
                          "Uživatelské_jméno",
                          "Q01_Group",
                          "Q02_Leader_name",
                          "Q03_Preparation",
                          "Q04_Introduction",
                          "Q05_Inclusion",
                          "Q06_Fav_question",
                          "Q07_What_learned",
                          "Q08_Negative_feedback"]
    
    data_frame = data_frame[["Q02_Leader_name",
                          "Q03_Preparation",
                          "Q04_Introduction",
                          "Q05_Inclusion",
                          "Q06_Fav_question",
                          "Q07_What_learned",
                          "Q08_Negative_feedback"]]
    return data_frame
