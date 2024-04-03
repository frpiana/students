@echo off

rem Percorso del tuo script principale
set main_script="src\students\main.py"

rem Nome dell'eseguibile da generare
set exe_name="students_v1-0-0"

rem Comando per la build
pyinstaller --onefile -n %exe_name% %main_script%
