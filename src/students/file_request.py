from os.path import isfile

def file_validation():
    while True:
        try:
            nome_file = input("\nInsert file name <file.csv>: ")

            if not nome_file:
                raise ValueError("The file name can not be empty.")
            
            # Verifica se il file esiste
            if not isfile(nome_file):
                raise FileNotFoundError(f"The file '{nome_file}' does not exists.")
            
            # Verifica se il file ha estensione .csv
            if not nome_file.endswith('.csv'):
                raise Exception("The file extention must be .csv.")
            
            # Se tutto è andato bene, ritorna il nome del file
            return nome_file
        
        except ValueError as ve:
            print(f"\nError: {ve}")
        except FileNotFoundError as fe:
            print(f"\nError: {fe}")
        except Exception as e:
            print(f"\nError: {e}")

