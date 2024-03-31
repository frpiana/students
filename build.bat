@echo off

rem Percorso del tuo script principale
set main_script="src\students\main.py"

rem Nome dell'eseguibile da generare
set exe_name="students"

rem Comando per la build
pyinstaller --onefile -n %exe_name% %font_options% %main_script%
