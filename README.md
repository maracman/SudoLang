# Language-aquisition-research-tool
 Tool for developing goal-oriented experimental paradigms for cognitive and neurocognitive research into language-learning, attention, memory and semantic processes.

Files for program:
1. The main .py file for researchers is named 'LART' + version_number
2. Data for analysis saved to data/outputs in the format: username + '_' + time_stamp + '_click_times'
3. Included is .py file 'LART_Survey' + version_number for providing to participants in an experiment, this file will load settings exported to surrvey_settings.pkl
4. files to recall settings are located data/saved_game_states there is one seetingsfile per username. saving settings with an existing username will overwrite the previous file.
5. Do not edit game_input_data.csv without knowing exactly what you are doing. The game will include extra information put in this file but will get confused if you stray from a particular format. 
6. data/animals contains Image files that cohere with labels stored in the input csv. Hi-res files are not useed but included for future redundancy.


Instructions:
The initial settings prompt contains hove over explinations for various settings, contact the developer if you need more clarification.
