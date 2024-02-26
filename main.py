from pdfgen import creapdf
from data_elaboration import data_elaboration
from data_import import data_import


if __name__ == "__main__":
    raw_data = data_import("Discussion_Leading_Feedback_Participant_Adar_.csv")
    student_names = raw_data["Q02_Leader_name"].drop_duplicates()

    for student in student_names:
        df = raw_data[raw_data['Q02_Leader_name'] == student]
        data = df.to_dict(orient='list')
        creapdf(data)
        

    #for riga in raw_data.itertuples():
    #    data = data_elaboration(riga)
    #    creapdf(data)