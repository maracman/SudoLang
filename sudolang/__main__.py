"""
SudoLang - Language Acquisition Research Tool

Entry point for the application. Run as:
    python -m sudolang           # Researcher mode (settings UI)
    python -m sudolang --survey  # Survey/participant mode
"""

import argparse
import sys

import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5.QtWidgets import QApplication
from PyQt5 import sip

from sudolang.config import (
    load_or_create_settings,
    settings_default_path,
    survey_settings_path,
)
from sudolang.gui import App, Enter_Name
from sudolang.game import run_game


def main():
    parser = argparse.ArgumentParser(description='SudoLang - Language Acquisition Research Tool')
    parser.add_argument('--survey', action='store_true',
                        help='Run in survey/participant mode (skips settings window, loads exported settings)')
    args = parser.parse_args()

    settings = load_or_create_settings()

    if not args.survey:
        # Researcher mode — show settings window
        while True:
            exit_code = 1
            app = QApplication(sys.argv)
            window = App(settings)
            window.show()
            exit_code = app.exec_()

            if exit_code == App.EXIT_CODE_REBOOT:
                print('restarting settings window')
                sip.delete(app)
                del app
            else:
                break

            try:
                settings.load(settings_default_path)
                print("saved settings found")
            except IOError:
                print("could not load new settings")

        # Reload settings after window closes
        try:
            settings.load(settings_default_path)
        except IOError:
            print("could not load new settings")

        # Export settings for survey app if requested
        if settings.export_settings:
            settings.save(survey_settings_path)

        if window.exit_application:
            sys.exit()

    else:
        # Survey mode — load exported settings, prompt for ID only
        settings.load(survey_settings_path)
        app = QApplication(sys.argv)
        window = Enter_Name(settings)
        window.show()
        app.exec_()

        if window.exit_application:
            sys.exit()

    # Run the game
    run_game(settings)


if __name__ == '__main__':
    main()
