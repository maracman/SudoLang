# Language-Aquisition-Research-Tool_(LART)
 Tool for developing goal-oriented experimental paradigms for cognitive and neurocognitive research into language-learning, attention, memory and semantic processes.

Files:
1. The main .py file for researchers is named 'SudoLang' + version_number
2. Data for analysis saved to as .csv in /outputs as username + '_clicktimes_' + time_stamp  
3. Included is .py file 'SudoLang_Survey' + version_number for providing to participants in an experiment, this file will load settings exported to surrvey_settings.pkl
4. files that recall settings are located data/saved_game_states (and is automatically accessed by the program) there is one seetings file per username. saving settings with an existing username will overwrite the previous file.
5. Do not edit game_input_data.csv without knowing exactly what you are doing. The game will include extra information put in this file but will get confused if you stray from a particular format. 
6. data/obj_images contains Image files that adhere with labels stored in the input csv. Hi-res files are not used but included for future redundancy.

Instructions:
The initial settings prompt contains hover-over explanations for various settings, contact the developer if you need more clarification.

Outputs:

Data points for each object clicked - saved to clicktimes (.csv) file

information explaining each data point can be gained from the outputs tab in settings


IMPORTANT WHEN USING PYINSTALLER

when creating an executable file using pyinstaller, include:

--hidden-import pandas.plotting._matplotlib

to prevent exception "Failed to execute script due to unhandled exception: matplotlib is required for plotting when the default backend "matplotlib" is selected"




