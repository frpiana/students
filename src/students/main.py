from pdfgen import creapdf
from data_import import data_import
from pandas import DataFrame

if __name__ == "__main__":
    
    # The program requests the name of the csv file to convert in PDF
    print("Insert file name <file.csv>:")
    
    # The name of the file is saved in the 'file_name' variable
    file_name = str(input())
    
    # The name of the file is passed to the 'data_import()' function
    # The output is a pandas dataframe saved in the 'raw_data' variable
    raw_data = data_import(file_name)
    
    # The list of student is extracted from the column "Q02_Leader_name"
    # More records could refere to the same student, the methode
    # 'drop_duplicates()' eliminates the names recurring more than once 
    student_names = raw_data["Q02_Leader_name"].drop_duplicates()
    
    # The following 'for' cycle generates the pdf files one for any student
    for student in student_names:
        # A subset dataframe 'df' is created with the records of a single student
        df = raw_data[raw_data['Q02_Leader_name'] == student].drop_duplicates(subset='ID')
        # The dataframe is converted in a dictionary of lists
        data = df.to_dict(orient='list')
        creapdf(data)