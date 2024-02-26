def data_elaboration(nome, records):
    title = nome.strip().replace(" ", "_")+".pdf"
    data = {"title": title,
            "name": nome,
            "Q1": [""],
            "Q2": [""],
            "Q3": [""],
            "liked": [""],
            "interesting": [""],
            "learned": [""],
            "to_improve":[""]}
    for record in records:        
        data["Q1"].append(record[1])
        data["Q2"].append(record[2])
        data["Q3"].append(record[3])
        data["interesting"].append(record[4])
        data["learned"].append(record[5])
        data["to_improve"].append(record[6])
        
    return data