""" Class to write data to .csv
"""

############
# IMPORTS  #
############
# Import data science packages
import pandas as pd

# Import GUI packages
from tkinter import filedialog

# Import system packages
import csv
from pathlib import Path
from datetime import datetime
import os

# Import misc packages
import ast


#########
# MODEL #
#########
class CSVModel:
    """ Write provided dictionary to .csv
    """
    def __init__(self, sessionpars):
        self.sessionpars = sessionpars

        # Generate date stamp
        self.datestamp = datetime.now().strftime("%Y_%b_%d_%H%M")


    def export_filters(self, filter_dict):
        """ Save filters to .csv
        """
        # Convert dict to dataframe for writing to .csv
        filter_df = pd.DataFrame.from_dict(filter_dict)

        # Generate date stamp
        now = datetime.now()
        date_stamp = now.strftime("%Y_%b_%d_%H%M")

        # Create save file name
        filename = 'filters_' + str(date_stamp)

        # Attempt to write filters .csv file
        try:
            # Query user for save path
            save_path = filedialog.asksaveasfile(
                initialfile= filename,
                defaultextension='.csv').name

            # Write data to .csv file if a valid save path is given
            filter_df.to_csv(save_path, mode='w', index=False)
            print("\ncsvmodel: Filters successfully written to file.")
        except AttributeError:
            # Do nothing if cancelled
            return


    def import_filter_dict(self):
        # Query user for filter .csv file
        filename = filedialog.askopenfilename()
        # Do nothing if cancelled
        if not filename:
            return
        # If a valid filename is found, load it
        filter_df = pd.read_csv(filename)

        # Create filter dict
        keys = list(filter_df.columns)
        filter_dict = {}
        for key in keys:
            # Check for lists
            if (filter_df.loc[1,key] == 'contains') or \
                (filter_df.loc[1,key] == 'not in'):
                value = ast.literal_eval(filter_df.loc[2,key])
                try:
                    value = [float(x) for x in value]
                except ValueError:
                    # Cannot convert string to float
                    pass
            else:
                value = filter_df.loc[2,key]
                # Convert value to float, if possible
                try:
                    value = float(value)
                except ValueError:
                    # Cannot convert string to float
                    pass
            # Assign values to dict
            filter_dict[key] = (filter_df.loc[0,key],
                        filter_df.loc[1,key],
                        value
            )

        return filter_dict








    def save_record(self, data):
        """ Save a dictionary of data to .csv file 
        """
        # Check for existing data folder
        data_directory = "Data"
        data_dir_exists = os.access(data_directory, os.F_OK)
        if not data_dir_exists:
            print(f"\ncsvmodel: {data_directory} directory not found! " + 
                "Creating it...")
            os.mkdir(data_directory)
            print(f"csvmodel: Successfully created {data_directory} " +
                  "directory!")

        # Create file name and path
        filename = f"{self.sessionpars['subject'].get()}_{self.sessionpars['condition'].get()}_{self.datestamp}.csv"
        self.file = Path(os.path.join(data_directory, filename))

        # Check for write access to store csv
        file_exists = os.access(self.file, os.F_OK)
        parent_writable = os.access(self.file.parent, os.W_OK)
        file_writable = os.access(self.file, os.W_OK)
        if (
            (not file_exists and not parent_writable) or
            (file_exists and not file_writable)
        ):
            msg = f"\ncsvmodel: Permission denied accessing file: {filename}"
            raise PermissionError(msg)

        # Write file
        newfile = not self.file.exists()
        with open(self.file, 'a', newline='') as fh:
            csvwriter = csv.DictWriter(fh, fieldnames=data.keys())
            if newfile:
                csvwriter.writeheader()
            csvwriter.writerow(data)
        print("\ncsvmodel: Record successfully saved!")
