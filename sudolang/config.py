import os
import sys
import pickle
import pandas as pd


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

operating_system = sys.platform
if operating_system == "darwin":
    dir_path = os.path.sep.join(sys.argv[0].split(os.path.sep)[:-1])
    if not os.path.exists(os.path.join(dir_path, 'SL_data')):
        parent_dir = os.path.split(dir_path)[0]
        for i in range(4):
            print("searching parent directories for program data")
            if os.path.exists(os.path.join(parent_dir, 'SL_data')):
                dir_path = parent_dir
                break
            else:
                parent_dir = os.path.split(parent_dir)[0]
else:
    dir_path = os.getcwd()

data_path = os.path.join(dir_path, 'SL_data/')
settings_default_path = os.path.join(data_path, 'current_settings.pkl')
survey_settings_path = os.path.join(data_path, 'survey_settings.pkl')
font_location = os.path.join(data_path, 'freesansbold.ttf')
outputs_path = os.path.join(dir_path, 'outputs/')
previous_data_sets_path = os.path.join(data_path, 'saved_game_states/')

# Load input CSV
inputData = pd.read_csv(os.path.join(data_path, 'game_input_data.csv'))


# ---------------------------------------------------------------------------
# Settings class — replaces the 24+ global variables
# ---------------------------------------------------------------------------

# Default output variable definitions
DEFAULT_OUTPUT_CHECKBOXES = pd.DataFrame(
    [['click_time', True, "'click_time': Timestamp for click"],
     ['since_last_click', True, "'since_last_click': Time since last response click "],
     ['since_stimulus', True, "'since_stimulus': Time since last matching response"],
     ['score_for_clicked', True, "'score_for_clicked': No. of prior matches for clicked object"],
     ['score_for_target', True, "'score_for_target': No. of prior matches for target object"],
     ['clicked_word_category', True, "'clicked_word_category': Numerical category of the clicked's label"],
     ['target_word_category', True, "'target_word_category': Numerical category of the target's label"],
     ['target_object_category', True, "'target_object_category': Category of the target object"],
     ['clicked_object_category', True, "'clicked_object_category': Category of the clicked object"],
     ['isRepeat', True, "'isRepeat': Was the same target shown for the prior stimulus"],
     ['isMatch', True, "'isMatch': Did the response match the target"],
     ['x_position', True, "'x_position': Horizontal position of the response click "],
     ['player_energy', True, "'player_energy': player's energy at time of response"],
     ['user_ID', True, "'user_ID': Tag each response with the user_ID"],
     ['isDisplayed', True, "'isDisplayed': is target object image represented as stimulus"],
     ['clicked_label', True, "clicked_label: The label for the object clicked"],
     ['clicked_img', True, "'clicked_img': The image name for the object clicked"],
     ['target_label', True, "target_label: The label for the target object"],
     ['target_img', True, "'target_img': The image name of the target object"],
     ['vocab_size', True, "'vocab_size': size of player vocabulary at click"],
     ['time_date', False, "'time_date': time stamp of the start of the session"],
     ['feedback_type', True, "'feedback_type': correct (+1) or incorrect (-1) sound played on click"],
     ['coord_file_name', False, "'coord_file_name': file name of mouse track data for click"],
     ['objects_on_screen', False, "'objects_on_screen': the number of objects on screen"],
     ['scroll_speed', False, "'scroll_speed': the speed objects are progressing down the screen"]],
    columns=pd.Index(['variable_name', 'boolean_value', 'description'])
)


class Settings:
    """Holds all experiment settings that were previously global variables.

    These are the 24 values serialised to/from pickle files, plus a few
    non-persisted flags used at runtime.
    """

    # The ordered key names used for pickle serialisation.
    PICKLE_KEYS = [
        'word_slider_values', 'object_slider_values', 'energy_mean', 'impact_max',
        'impact_min', 'output_checkboxes', 'id_name', 'lives', 'starting_vocabulary',
        'bg_matchingness', 'energy', 'thresh', 'isEnergy_linear', 'load_previous',
        'isMousetrack', 'rareness', 'fps', 'increase_scroll', 'isFixed',
        'scroll_speed_value', 'diff_successive', 'isLabel_audio',
        'feedback_random_value', 'isFeedback',
    ]

    def __init__(self):
        # Persisted settings (saved to / loaded from pickle)
        self.word_slider_values = [5, 20, 45, 35, 15, 10]
        self.object_slider_values = [50, 50, 0]
        self.energy_mean = 30
        self.impact_max = 6
        self.impact_min = 3
        self.output_checkboxes = DEFAULT_OUTPUT_CHECKBOXES.copy()
        self.id_name = '_'
        self.lives = -1
        self.starting_vocabulary = 3
        self.bg_matchingness = 0
        self.energy = 50
        self.thresh = 4
        self.isEnergy_linear = False
        self.load_previous = False
        self.isMousetrack = False
        self.rareness = True
        self.fps = 50
        self.increase_scroll = True
        self.isFixed = False
        self.scroll_speed_value = 3
        self.diff_successive = True
        self.isLabel_audio = True
        self.feedback_random_value = 0
        self.isFeedback = True

        # Runtime-only flags (not persisted)
        self.isEnergy_overlay = False
        self.isAnimate_energy = False
        self.feedback_delay_value = 10
        self.export_settings = False

    # ------------------------------------------------------------------
    # Pickle I/O
    # ------------------------------------------------------------------

    def save(self, file_path):
        values = [getattr(self, k) for k in self.PICKLE_KEYS]
        with open(file_path, 'wb') as f:
            pickle.dump(values, f)

    def load(self, file_path):
        with open(file_path, 'rb') as f:
            values = pickle.load(f)
        for key, val in zip(self.PICKLE_KEYS, values):
            setattr(self, key, val)

    def load_and_save_to_default(self, file_path):
        self.load(file_path)
        self.save(settings_default_path)


def load_or_create_settings():
    """Load settings from disk, or create defaults if not found."""
    settings = Settings()
    if not os.path.isfile(settings_default_path):
        print("default settings file not found, initialising settings")
        settings.save(settings_default_path)
    else:
        try:
            settings.load(settings_default_path)
        except IOError:
            print("could not load latest settings")
            settings.save(settings_default_path)
    return settings
