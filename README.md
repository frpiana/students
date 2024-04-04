# Program for the conversion of csv files in prose PDF

## Target of the program
The program is designed specifically for CSV files produced by the Moodle study manangement system as survey results, in Czech langauge.

The columns of the original table should be the following:

1. Odpověď
2. Odesláno:
3. Instituce
4. Oddělení
5. Kurz
6. Skupina
7. ID
8. "Celý název"
9. "Uživatelské jméno"
10. Q01_Group
11. "Q02_Leader name"
12. "Q03_Preparation->1 – do not agree at all| 5 – strongly agree"
13. "Q04_Introduction->1 – do not agree at all| 5 – strongly agree"
14. "Q05_Inclusion->1 – do not agree at all 5 – strongly agree"
15. "Q06_Fav question"
16. "Q07_What learned"
17. "Q08_Negative feedback"

## How to install the program
The file _student.exe_ is in the _dist_ folder of the repository. Copy it in a folder of the hard disk, in example: _"C:\Users\user_name\Documents\executables"_. The folder names of the path should not contain any spaces.

From the start menú search for "Edit the system enviroment variables for you account".

In the table "User variables" select the variable _Path_ and clic on _Edit_.

In the window "Edit enviroment variable" click on _New_ and paste the path of the folder of the file _students.exe_.

## How to use the program
In the folder where the _file.csv_ is saved click with the right button of the mouse and select "Open in terminal". Also these folder names of the path should not contain any spaces to prevent bugs.

In the terminal type the program name:
```bash
students
```
The program will now require the file input:
```bash
Insert file name <file.csv>:
```
Paste the file name with the extention .csv and press _enter_.

The program will create in the same folder of the CSV file a folder named **pdf** where it will save the PDF files.
