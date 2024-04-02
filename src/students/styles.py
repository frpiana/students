from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

pdfmetrics.registerFont(TTFont("Garamond_regular", "GARA.ttf"))
pdfmetrics.registerFont(TTFont("Garamond_bold", "GARABD.ttf"))

def title_style_definition() -> ParagraphStyle:
    title_style_set = ParagraphStyle(
        name='TitleStyle',
        fontSize = 14,                        # Dimensione del carattere
        leading = 16,                         # Spaziatura tra le righe
        spaceBefore = 20,                     # Spaziatura prima del paragrafo
        spaceAfter = 20,                      # Spaziatura dopo il paragrafo
        fontName = 'Garamond_Bold'            # Tipo di carattere in grassetto
        )
    return title_style_set

def question_style_definition() -> ParagraphStyle:
    question_style_set = ParagraphStyle(
        name='QuestionStyle',
        fontSize = 12,                        # Dimensione del carattere
        leading = 8,                          # Spaziatura tra le righe
        spaceBefore = 12,                     # Spaziatura prima del paragrafo
        spaceAfter = 12,                      # Spaziatura dopo il paragrafo
        fontName = 'Garamond_Bold'            # Tipo di carattere in grassetto
        )
    return question_style_set

def bullet_style_definition() -> ParagraphStyle:
    bullet_style_set = ParagraphStyle(
        name='BulletStyle',
        fontName = 'Garamond_regular',
        bulletFontName = 'Garamond_regular',  # Tipo di carattere del punto
        bulletText = '-',                     # Simbolo del punto d'elenco (trattino)
        bulletFontSize = 12,                  # Dimensione del simbolo
        bulletIndent = 10,                    # Indentazione del bullet rispetto al margine sinistro
        leftIndent = 22,                      # Indentazione del testo rispetto al bullet
        spaceBefore = 5,                      # Spaziatura prima del paragrafo
        spaceAfter = 5                        # Spaziatura dopo il paragrafo
        )
    return bullet_style_set

def regular_style_definition() -> ParagraphStyle:
    regular_style_set = ParagraphStyle(
        name = 'RegularStyle',
        fontName = 'Garamond_regular',        # Tipo di carattere
        leftIndent = 22,                      # Indentazione del testo rispetto al bullet
        spaceBefore = 5,                      # Spaziatura prima del paragrafo
        spaceAfter = 5                        # Spaziatura dopo il paragrafo
        )
    return regular_style_set