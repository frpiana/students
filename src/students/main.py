from pdfgen import creapdf
from data_import import data_import
from data_cleaning import clean_leader_names
from file_analysis import analyze_file
from pandas import DataFrame
from notifications import credits, termination
from file_request import file_validation
import sys

if __name__ == "__main__":

    # Print of the credits
    credits()

    # Optional --output-dir argument (used by test runner)
    output_dir: str = "pdf"
    for i, arg in enumerate(sys.argv):
        if arg == "--output-dir" and i + 1 < len(sys.argv):
            output_dir = sys.argv[i + 1]

    # The name of the file is saved in the 'file_name' variable after validation
    file_name: str = file_validation()

    # Structural analysis of the input file
    report = analyze_file(file_name)
    report.print_report()

    if not report.is_valid:
        print("Impossibile procedere: correggere gli errori segnalati.")
        sys.exit(1)

    # The name of the file is passed to the 'data_import()' function
    # Using encoding and delimiter detected by file_analysis
    raw_data: DataFrame = data_import(
        file_name,
        encoding=report.encoding,
        delimiter=report.delimiter
    )

    # Data cleaning: normalization and deduplication of leader names
    raw_data = clean_leader_names(raw_data)

    # The list of student is extracted from the column "Q02_Leader_name"
    # 'drop_duplicates()' eliminates the leader names recurring more than once
    # 'dropna()' removes rows where the leader name is missing
    student_names: DataFrame = raw_data["Q02_Leader_name"].drop_duplicates().dropna()

    # The following 'for' cycle generates the pdf files one for any student
    for student in student_names:
        # A subset dataframe 'df' is created with the records of a single student
        df: DataFrame = raw_data[raw_data['Q02_Leader_name'] == student].drop_duplicates(subset='ID')
        # The dataframe is converted in a dictionary of lists
        data: DataFrame = df.to_dict(orient='list')

        creapdf(data, output_dir=output_dir)

    termination()
