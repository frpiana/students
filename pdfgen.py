from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import ParagraphStyle
import os
import numpy as np

def creapdf(data):

    title_style = ParagraphStyle(
    name='TitleStyle',
    fontSize=14,
    leading=16,  # Spaziatura tra le righe
    spaceBefore=20,  # Spaziatura prima del paragrafo
    spaceAfter=20,   # Spaziatura dopo il paragrafo
    fontName='Helvetica-Bold'  # Tipo di carattere in grassetto
    )

    question_style = ParagraphStyle(
    name='QuestionStyle',
    fontSize=12,
    leading=8,  # Spaziatura tra le righe
    spaceBefore=12,  # Spaziatura prima del paragrafo
    spaceAfter=12,   # Spaziatura dopo il paragrafo
    fontName='Helvetica-Bold'  # Tipo di carattere in grassetto
    )

    bullet_style = ParagraphStyle(
    name='BulletStyle',
    bulletFontName='Helvetica',
    bulletText='-',   # Simbolo del bullet (trattino)
    bulletFontSize=12,
    bulletIndent=10,  # Indentazione del bullet rispetto al margine sinistro
    leftIndent=22,    # Indentazione del testo rispetto al bullet
    spaceBefore=5,    # Spaziatura prima del paragrafo
    spaceAfter=5      # Spaziatura dopo il paragrafo
)

    if not os.path.exists("pdf"):
        os.makedirs("pdf")
    
    title = data["Q02_Leader_name"][0].strip().replace(" ", "_")+".pdf"
    file_path = os.path.join("pdf", title)

    documento = SimpleDocTemplate(file_path, pagesizes=A4)
    contenuto = []

    contenuto.append(Paragraph(
        f"Leader: {data["Q02_Leader_name"][0]}", title_style
        ))
    
    contenuto.append(Paragraph(
        "The group leader...", question_style 
    ))
    contenuto.append(Paragraph(
        f"...was well-prepared for the discussion: {np.mean(data["Q03_Preparation"])}"
        ))

    contenuto.append(Paragraph(
        f"...opened the session with a clear introduction of the topic: {np.mean(data["Q04_Introduction"])}"
        ))

    contenuto.append(Paragraph(
        f"...got everyone to participate: {np.mean(data["Q05_Inclusion"])}"
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
        

    documento.build(contenuto)