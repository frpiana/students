from pdfgen import creapdf
from data_import import data_import
import os

if __name__ == "__main__":
    position = str(os.getcwd)
    print("Insert file name <file.csv>:")
    file_name = str(input())
    full_path = os.path.join(position, file_name)
    output_directory = os.path.join(position, "pdf")
    raw_data = data_import(file_name)
    student_names = raw_data["Q02_Leader_name"].drop_duplicates()
    for student in student_names:
        df = raw_data[raw_data['Q02_Leader_name'] == student]
        data = df.to_dict(orient='list')
        creapdf(data)