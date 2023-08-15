""" Model for storing session parameters 
"""

############
# IMPORTS  #
############
# Import system packages
from pathlib import Path
import os

# Import data handling packages
import json


#########
# BEGIN #
#########
class SessionParsModel:
    # Define dictionary items
    fields = {
        # Session variables
        'initial_scrub': {'type': 'int', 'value': 0},

        # Version control variables
        'config_file_status': {'type': 'int', 'value': 0},
        'check_for_updates': {'type': 'str', 'value': 'yes'},
        'version_lib_path': {'type': 'str', 'value': r'\\starfile\Public\Temp\MooreT\Custom Software\version_library.csv'},
    }


    def __init__(self, _app_info):
        # Assign variables
        self._app_info = _app_info

        # Create session parameters file name
        filename = 'config.json'

        # Create a folder to store the session parameters file
        # in user's home directory
        directory = Path.home() / self._app_info['name']
        if not os.path.exists(directory):
            print("sessionmodel: No config file directory found " +
                  "- creating it")
            os.makedirs(directory)

        # Path to file
        self.filepath = directory / filename

        # Attempt to load session parameters file
        self.load()


    def load(self):
        """ Attempt to load session parameters from file
        """
        # If the file doesn't exist, abort
        print("\nsessionmodel: Checking for parameter file...")
        if not self.filepath.exists():
            print("sessionmodel: No session parameters file found; " +
                  "using default values")
            return

        # Open the file and read in the raw values
        print("sessionmodel: File found - reading raw values from " +
            "parameter file...")
        with open(self.filepath, 'r') as fh:
            raw_values = json.load(fh)

        # Don't implicitly trust the raw values: only get known keys
        print("sessionmodel: Loading vals into sessionpars model " +
            "if they match model keys")
        # Populate session parameter dictionary
        for key in self.fields:
            if key in raw_values and 'value' in raw_values[key]:
                # update config file status here
                if key == 'config_file_status':
                    raw_value = 1
                else:
                    raw_value = raw_values[key]['value']
                self.fields[key]['value'] = raw_value


    def save(self):
        """ Save current session parameters to file 
        """
        # Write to JSON file
        #print("sessionmodel: Writing session pars from model to file...")
        with open(self.filepath, 'w') as fh:
            json.dump(self.fields, fh)


    def set(self, key, value):
        """ Set a variable value.
        """
        if (
            key in self.fields and 
            type(value).__name__ == self.fields[key]['type']
        ):
            self.fields[key]['value'] = value
        else:
            raise ValueError("sessionmodel: Bad key or wrong variable type")
