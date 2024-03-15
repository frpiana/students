from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph
from styles import title_style_definition, question_style_definition, bullet_style_definition
from os import makedirs
from os.path import exists, join
from numpy import mean

def creapdf(data):
    
    # Formatting stiles definition
    title_style = title_style_definition()
    question_style = question_style_definition()
    bullet_style = bullet_style_definition()

    # Creation of the folder for the building output
    if not exists("pdf"):
        makedirs("pdf")
    
    # File name and file path identification for the building output
    title = data["Q02_Leader_name"][0].strip().replace(" ", "_")+".pdf"
    file_path = join("pdf", title)

    # Creation of the PDF template and the container for the text paragrafs
    documento = SimpleDocTemplate(file_path, pagesizes=A4)
    contenuto = []

    # Filling of the paragraphs
    contenuto.append(Paragraph(
        f"Leader: {data['Q02_Leader_name'][0]}", title_style
        ))
    
    contenuto.append(Paragraph(
        "The group leader...", question_style 
    ))
    contenuto.append(Paragraph(
        f"...was well-prepared for the discussion: {mean(data['Q03_Preparation'])}"
        ))

    contenuto.append(Paragraph(
        f"...opened the session with a clear introduction of the topic: {mean(data['Q04_Introduction'])}"
        ))

    contenuto.append(Paragraph(
        f"...got everyone to participate: {mean(data['Q05_Inclusion'])}"
        ))
    
    contenuto.append(Paragraph(
        "For me, the most interesting question was:", question_style
    ))

    for frase in data["Q06_Fav_question"]:
        contenuto.append(Paragraph(frase, bullet_style))

    contenuto.append(Paragraph(
        "One thing I learned from this discussion:", question_style
    ))

    for frase in data["Q07_What_learned"]:
        contenuto.append(Paragraph(frase, bullet_style))

    contenuto.append(Paragraph(
        "What could be improved in the discussion:", question_style
    ))

    for frase in data["Q08_Negative_feedback"]:
        frase = str(frase)
        if frase != "nan":
            contenuto.append(Paragraph(str(frase), bullet_style))
        
    # Building of the PDF doument writing the container in the template
    documento.build(contenuto)