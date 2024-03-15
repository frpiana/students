from pdfgen import creapdf
from data_import import data_import

if __name__ == "__main__":
        
    print("Insert file name <file.csv>:")
    
    file_name = str(input())
        
    raw_data = data_import(file_name)
    
    student_names = raw_data["Q02_Leader_name"].drop_duplicates()
    
    for student in student_names:
        df = raw_data[raw_data['Q02_Leader_name'] == student]
        data = df.to_dict(orient='list')
        creapdf(data)