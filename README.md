# Language-Aquisition-Research-Tool_(LART)
 Tool for developing goal-oriented experimental paradigms for cognitive and neurocognitive research into language-learning, attention, memory and semantic processes.

Files:
1. The main .py file for researchers is named 'LART' + version_number
2. Data for analysis saved to as .csv in data/outputs as username + '_clicktimes_' + time_stamp  
3. Included is .py file 'LART_Survey' + version_number for providing to participants in an experiment, this file will load settings exported to surrvey_settings.pkl
4. files to recall settings are located data/saved_game_states there is one seetingsfile per username. saving settings with an existing username will overwrite the previous file.
5. Do not edit game_input_data.csv without knowing exactly what you are doing. The game will include extra information put in this file but will get confused if you stray from a particular format. 
6. data/animals contains Image files that cohere with labels stored in the input csv. Hi-res files are not useed but included for future redundancy.

Instructions:
The initial settings prompt contains hove over explinations for various settings, contact the developer if you need more clarification.

Outputs:
(Data points for each object clicked saved to 'clicktimes' file presented chronologically)

click_time - Time between the presentation of the target object and the user's selection click
animal_type -  The label of the target object 
score_for_type - The sum of correctly answered
word_complexity - score (from 1 to 6) given to the target label 
isRepeat - a boolian value, was the same target used in the previous round
isTarget_img - A booleam value, was the target displayed as an image in adition to the label
x_position - the x coordinate for where the clicked object was on the screen
player_energy - the user's energy (out of 100) at the time the object was clicked



