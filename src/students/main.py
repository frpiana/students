from pdfgen import creapdf
from data_import import data_import
from pandas import DataFrame
from notifications import credits, termination
from file_request import file_validation

if __name__ == "__main__":
    
    # Print of the credits
    credits()
    
    # The name of the file is saved in the 'file_name' variable after validation
    file_name: str = file_validation()

    # The name of the file is passed to the 'data_import()' function
    # The output is a pandas dataframe saved in the 'raw_data' variable
    raw_data: DataFrame = data_import(file_name)
    
    # The list of student is extracted from the column "Q02_Leader_name"
    # 'drop_duplicates()' eliminates the leader names recurring more than once 
    student_names: DataFrame = raw_data["Q02_Leader_name"].drop_duplicates()
    
    # The following 'for' cycle generates the pdf files one for any student
    for student in student_names:
        # A subset dataframe 'df' is created with the records of a single student
        df: DataFrame = raw_data[raw_data['Q02_Leader_name'] == student].drop_duplicates(subset='ID')
        # The dataframe is converted in a dictionary of lists
        data: DataFrame = df.to_dict(orient='list')

        creapdf(data)
    
    termination()