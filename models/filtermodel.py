""" Model for list of filter settings
"""

###########
# Imports #
###########
# Import GUI packages
from tkinter import filedialog
from tkinter import messagebox

# Import data science packages
import pandas as pd

# Import system packages
from datetime import datetime

# Import misc packages
import ast


#########
# BEGIN #
#########
class FilterList:
    """ Class to handle importing/exporting the 
        filter combobox values
    """

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
            if filter_df.loc[1,key] == 'contains':
                #filter_list = ast.literal_eval(filter_df.loc[2,key])
                #value = ' '.join(filter_list)
                value = ast.literal_eval(filter_df.loc[2,key])
            else:
                value = filter_df.loc[2,key]
            # Assign values to dict
            filter_dict[key] = (filter_df.loc[0,key],
                        filter_df.loc[1,key],
                        value
            )

        return filter_dict


    # def import_filter_dict(self):
    #     # Query user for filter .csv file
    #     filename = filedialog.askopenfilename()
    #     # Do nothing if cancelled
    #     if not filename:
    #         return
    #     # If a valid filename is found, load it
    #     filter_df = pd.read_csv(filename)

    #     # Create filter dict
    #     keys = list(filter_df.columns)
    #     filter_dict = {}
    #     for key in keys:
    #         # Check for lists
    #         if filter_df.loc[1,key] == 'contains':
    #             value = ast.literal_eval(filter_df.loc[2,key])
    #         else:
    #             value = filter_df.loc[2,key]
    #         # Assign remaining values to dict
    #         filter_dict[key] = (filter_df.loc[0,key],
    #                     filter_df.loc[1,key],
    #                     value
    #         )
    #     return filter_dict


    def export_filters(self, filter_dict):
        """ Save filters to .csv
        """
        if not filter_dict:
            messagebox.showerror(title="Empty List",
                message="No filter values to save!",
                detail="Cannot export an empty filter list. If you have " +
                    "provided at least one filter, you " +
                    "must click the FILTER RECORDS button before " +
                    "exporting a filter list.")
            return

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
            print("Filters successfully written to file!")
        except AttributeError:
            # Do nothing if cancelled
            return
