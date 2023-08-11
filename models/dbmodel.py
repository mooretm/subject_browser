""" Database model for the Subject Browser 

    Expects a .csv file of the entire 'General Search' tab 
    from the online subject database. 

    Author: Travis M. Moore
    Last edited: Aug 08, 2023
 """

###########
# Imports #
###########
# Import GUI packages
from tkinter import filedialog

# Import data science packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import matplotlib
matplotlib.use('TkAgg')

# Import system packages
from datetime import datetime

# Import custom modules
from models.constants import FieldTypes as FT


#########
# BEGIN #
#########
class SubDB:
    """ Class to hold database info and provide related 
        functions (e.g., get air conduction thresholds)
    """

    def __init__(self, db_path):
        """ Load database .csv file from path
        """
        self.load_db(db_path)


    #################################
    # Import and Clean Raw Database #
    #################################
    def load_db(self, db_path):
        """ Read raw database .csv from Star.
            Select desired columns only.
            Clean: convert to numeric, rename cols, fix max thresholds.
        """
        # Import .csv file of database records
        general_search = pd.read_csv(db_path)

        # Define columns of interest
        desired_cols = [0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 
                        16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 
                        29, 30, 31, 32, 33, 34, 35, 36, 38, 40, 42, 49, 51, 
                        52, 74, 85, 86, 88, 90, 101,102,103,104, 109, 112, 
                        113, 116, 121, 123, 124, 131, 132, 133, 134, 151, 
                        154, 155, 158, 163, 164, 165, 166, 170, 172, 173, 
                        176, 177, 178, 179, 180, 185, 187, 189, 192, 196, 
                        202, 204]

        # New dataframe with columns of interest only
        short_gen = general_search[general_search.columns[desired_cols]].copy()

        # Correct column names
        short_gen.rename(columns = {
            'L Pt Bc 1000':'LeftBC 1000',
            'L Pt Bc 2000':'LeftBC 2000',
            'L Pt Bc 4000':'LeftBC 4000',
            'L Pt Bc 500':'LeftBC 500',
            'RightBC  1000':'RightBC 1000',
            'RightBC  2000':'RightBC 2000',
            'RightBC  4000':'RightBC 4000',
            'Hearing AidUse':'Hearing Aid Use'
            }, inplace = True
        )

        # Calculate age and store in new dataframe column
        short_gen['Age'] = short_gen['Date Of Birth'].apply(
            lambda x: self._calc_age(x))

        # Coerce columns with numerical data to numeric
        cols = [0,8,9,10,11,12,13,14,15,16,17,22,23,24,25,26,27,28,29,
                30,31,36,40,47,48,49,50,51,53,56,57,59,61,62,64,66,67,
                68,69,71,72,85]
        short_gen.iloc[:, cols] = short_gen.iloc[:, cols].apply(
            pd.to_numeric, errors='coerce')

        # Sort dataframe by subject ID
        self.data = short_gen.sort_values(by='Subject Id').reset_index(
            drop=True).copy()

        # Change all audiogram thresholds above 120 to NaN
        # Generate column names
        audio_cols = self._audio_col_names()
        # Replace values
        for col in audio_cols:
            self.data.loc[self.data[col] > 120, col] = np.NaN

        # Convert all '%null' values to '-'
        self.data.replace(to_replace='%null%', value='-', inplace=True)

        # Provide feedback
        print("\ndbmodel: Loaded database.")
        print(f"dbmodel: Remaining candidates: {self.data.shape[0]}")


    def _audio_col_names(self):
        """ Create column names for air and bone conduction
            thresholds.
        """
        audio_cols = []
        # Air conduction
        sides = ['RightAC ', 'LeftAC ']
        freqs = [250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000]
        for side in sides:
            for freq in freqs:
                audio_cols.append(side + str(freq))
        # Bone conduction
        sides = ['RightBC ', 'LeftBC ']
        freqs = [500, 1000, 2000, 4000]
        for side in sides:
            for freq in freqs:
                audio_cols.append(side + str(freq))
        return audio_cols


    def _calc_age(self, birthdate):
        """ Convert birthdate to age.
        """
        today = datetime.now()
        x = str(birthdate).split('/')
        try:
            birth = datetime(int(x[2]), int(x[0]), int(x[1]))
            age = int((today - birth).days / 365.2425)
        except TypeError:
            age = '-'
        except IndexError:
            age = '-'
        except ValueError:
            age = '-'
        return age


    def load_filtered_db(self, db_path):
        """ Import a previously-exported database.
        """
        # Import .csv file of database records
        self.data = pd.read_csv(db_path)

        # Provide feedback
        print("\ndbmodel: Loaded previously exported database.")
        print(f"dbmodel: Remaining candidates: {self.data.shape[0]}")


    # def _initial_scrub(self):
    #     """ Perform perfunctory filtering 
    #     """
    #     # Remove internal employees
    #     self.data = self.data[self.data["Employment Status"] != "Employee"]
    #     print(f"Automatically removed internal Starkey employees")
    #     print(f"Remaining candidates: {self.data.shape[0]}\n")

    #     # Remove inactive records
    #     self.data = self.data[self.data["Status"] == "Active"]
    #     print(f"Automatically removed inactive participants")
    #     print(f"Remaining candidates: {self.data.shape[0]}\n")

    #     # Remove poor candidates
    #     self.data = self.data[self.data["Good Candidate"].isin(["-", 
    #         "Excellent", "Good", "Fair"])]
    #     print(f"Automatically removed poor candidates")
    #     print(f"Remaining candidates: {self.data.shape[0]}\n")


    def write(self):
        """ Save database to .csv"""
        # Generate date stamp
        now = datetime.now()
        date_stamp = now.strftime("%Y_%b_%d_%H%M")

        # Create save file name
        filename = 'filtered_db_' + str(date_stamp)

        # Query user for save path
        try:
            save_path = filedialog.asksaveasfile(
                initialfile= filename,
                defaultextension='.csv').name
        except AttributeError:
            # Do nothing if cancelled
            return

        # Do nothing if cancelled
        if not save_path:
            return

        # Write data to .csv file if a valid save path is given
        self.data.to_csv(save_path, mode='w', index=False)
        print("\ndbmodel: Database successfully written to file!")


    #######################
    # Filtering Functions #
    #######################
    def filter(self, colname, operator, value):
        # Drop "NaNs" and other non-data from column
        #df = self.data.copy()
        #df[colname].dropna()
        #df = df[~df[colname].isin(['-', '%null%', np.NaN])]

        # Filter
        if operator == "equals":
            self.data = self.data[self.data[colname] == value]
        if operator == "does not equal":
            self.data = self.data[self.data[colname] != value]
        if operator == ">":
            self.data = self.data[self.data[colname] > value]
        if operator == ">=":
            self.data = self.data[self.data[colname] >= value]
        if operator == "<":
            self.data = self.data[self.data[colname] < value]
        if operator == "<=":
            self.data = self.data[self.data[colname] <= value]
        if operator == "contains":
            self.data = self.data[self.data[colname].isin(value)]
        print(f"\ndbmodel: Filtered column '{colname}' for '{value}'")
        print(f"dbmodel: Remaining candidates: {self.data.shape[0]}")


    # def ac_thresh_filt(self, thresh_dict):
    #     """ Filter by right/left air conduction thresholds. 
    #         Expects dict of frequencies with tuple of lower
    #         and upper threshold limits.
    #     """
    #     sides = ["RightAC", "LeftAC"]
    #     for side in sides:
    #         for key in thresh_dict:
    #             # Construct column name
    #             colname = side + " " + key
    #             # Remove rows containing "-" (i.e., no data)
    #             self.data = self.data[self.data[colname] != "-"]
    #             # Convert column to int
    #             self.data[colname] = self.data[colname].astype("int")
    #             # Exclude thresholds above dict value 1
    #             self.data = self.data[self.data[colname] <= thresh_dict[key][1]]
    #             # Exclude thresholds below dict value 0
    #             self.data = self.data[self.data[colname] >= thresh_dict[key][0]]

    #     print("Filtered by provided air conduction threshold limits")
    #     print(f"Remaining candidates: {self.data.shape[0]}\n")


    ######################
    # Plotting Functions #
    ######################
    def get_thresholds(self, sub_id):
        """ Make dictionaries for air and bone conduction thresholds.
        """
        # Get AC thresholds
        sides = ["RightAC", "LeftAC"]
        freqs = [250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000]
        ac = {}
        for side in sides:
            for freq in freqs:
                colname = side + " " + str(freq)
                #ac.append(self.data[self.data['Subject Id'] == sub_id][colname].astype(int))
                try:
                    ac[side + ' ' + str(freq)] = int(
                        self.data[self.data['Subject Id'] == sub_id][colname].values[0]
                    )
                    #if ac[side + ' ' + str(freq)] > 120:
                    #    ac[side + ' ' + str(freq)] = None
                except:
                    ac[side + ' ' + str(freq)] = None

        # Get BC thresholds
        sides = ["RightBC", "LeftBC"]
        freqs = [500, 1000, 2000, 4000]
        bc = {}
        for side in sides:
            for freq in freqs:
                colname = side + " " + str(freq)
                try:
                    bc[side + ' ' + str(freq)] = int(
                        self.data[self.data['Subject Id'] == sub_id][colname].values[0])
                except:
                    bc[side + ' ' + str(freq)] = None

        return ac, bc


    def audio_ac(self, sub_id, ax=None):
        if ax is None:
            ax = plt.gca()

        # Get AC and BC thresholds
        ac, bc = self.get_thresholds(sub_id)
        thresholds = (ac, bc)

        # Remove "None" values from thresholds
        for ii in range(0,2):
            for key, value in dict(thresholds[ii]).items():
                if value is None:
                    del thresholds[ii][key]

        # Plot AC thresholds
        x = list(ac.items())
        right_ac_freqs = [int(j[0].split()[1]) for j in x if 'Right' in j[0]]
        right_ac_thresh = [j[1] for j in x if 'Right' in j[0]]
        left_ac_freqs = [int(j[0].split()[1]) for j in x if 'Left' in j[0]]
        left_ac_thresh = [j[1] for j in x if 'Left' in j[0]]
        ax.plot(right_ac_freqs, right_ac_thresh, 'ro-')
        ax.plot(left_ac_freqs, left_ac_thresh, 'bx-')

        # Plot BC thresholds
        x = list(bc.items())
        right_bc_freqs = [int(j[0].split()[1]) for j in x if 'Right' in j[0]]
        right_bc_thresh = [j[1] for j in x if 'Right' in j[0]]
        left_bc_freqs = [int(j[0].split()[1]) for j in x if 'Left' in j[0]]
        left_bc_thresh = [j[1] for j in x if 'Left' in j[0]]
        ax.plot(right_bc_freqs, right_bc_thresh, marker=8, c='red', linestyle='None')
        ax.plot(left_bc_freqs, left_bc_thresh, marker=9, c='blue', linestyle='None')

        # Plot formatting
        ax.set_ylim((-10,120))
        ax.invert_yaxis()
        yticks = range(-10,130,10)
        ax.set_yticks(ticks=yticks)
        ax.set_ylabel("Hearing Threshold (dB HL)")
        ax.semilogx()
        ax.set_xlim((200,9500))
        ax.set_xticks(ticks=[250,500,1000,2000,4000,8000], labels=[
            '250','500','1000','2000','4000','8000'])
        ax.set_xlabel("Frequency (Hz)")
        ax.axhline(y=25, color="black", linestyle='--', linewidth=1)
        ax.grid()
        ax.set_title(f"Audiogram for Participant {sub_id}")

        # Plot color regions
        audio_colors = ["gray", "green", "gold", "orange", "mediumpurple", 
            "lightsalmon"]
        alpha_val = 0.25
        degree_dict={
            'normal': (-10, 25),
            'mild': (25, 40),
            'moderate': (40, 55),
            'moderately-severe': (55, 70),
            'severe': (70, 90),
            'profound': (90, 120)
        }
        for idx, key in enumerate(degree_dict):
            coords = [
                [0,degree_dict[key][0]], 
                [9500,degree_dict[key][0]], 
                [9500,degree_dict[key][1]], 
                [0,degree_dict[key][1]]
            ]
            # Repeat the first point to create a 'closed loop'
            coords.append(coords[0])
            # Create lists of x and y values 
            xs, ys = zip(*coords) 
            # Fill polygon
            ax.fill(xs,ys, edgecolor='none', 
                facecolor=audio_colors[idx], alpha=alpha_val)


    #########################
    # Group Audiogram Plots #
    #########################
    def _get_audio_thresholds(self):
        # Create list of all audiogram column names
        all_audio_cols = self._audio_col_names()
        # Remove bone conduction column names
        air_data = [x for x in all_audio_cols if "B" not in x]
        # Get list of right air conduction column names
        right = [x for x in air_data if "Right" in x]
        # Get list of left air conduction column names
        left = [x for x in air_data if "Left" in x]

        # Create df of right audiogram data
        df_right = self.data[right]
        df_right.columns = [int(x.split()[1]) for x in df_right.columns]
        # Create df of left audiogram data
        df_left = self.data[left]
        df_left.columns = [int(x.split()[1]) for x in df_left.columns]
        # Concatenate left/right audiogram thresholds dfs
        thresholds = pd.concat([df_right, df_left]).reset_index(drop=True)
        
        return thresholds, df_right, df_left


    def plot_group_audio(self):
        """ Plot overlaid audiograms for each subject 
            currently in self.data.
        """
        # Call audiogram plot axis
        ax = self._group_audio_axis()
        thresholds, right, left = self._get_audio_thresholds()
        ax.set_title(f"Audiograms (n={int(thresholds.shape[0]/2)})")

        # Plot individual thresholds
        for ii in range(0, len(thresholds)):
            # Create mask to account for NaNs
            vals = thresholds.iloc[ii,:]
            mask = np.isfinite(vals)
            ax.plot(vals[mask].index, vals[mask], color='dimgrey')

        # Plot average thresholds
        avg = thresholds.mean()
        ax.plot(avg.index, avg, color='red', linestyle='--', linewidth=5)
        plt.show()


    def plot_ear_specific_group_audio(self):
        """ Plot overlaid audiograms for each subject 
            currently in self.data.
        """
        # Call audiogram plot axis
        ax = self._group_audio_axis()
        thresholds, right, left = self._get_audio_thresholds()
        ax.set_title(f"Audiograms (n={int(thresholds.shape[0]/2)})")

        # # Plot individual thresholds
        # for ii in range(0, len(thresholds)):
        #     # Create mask to account for NaNs
        #     vals = thresholds.iloc[ii,:]
        #     mask = np.isfinite(vals)
        #     ax.plot(vals[mask].index, vals[mask], color='dimgrey')

        # Plot individual thresholds
        for row in range(0, left.shape[0]):
            ax.plot(list(left.columns), list(left.iloc[row, :]), color='blue')
            ax.plot(list(right.columns), list(right.iloc[row, :]), color='red')

        # Plot average thresholds
        ax.plot(list(left.columns), thresholds.mean(), marker='o', color='black', 
            markersize=7, linestyle='None')
        plt.show()     


    def _group_audio_axis(self):
        ax = plt.gca()
        # Plot formatting
        ax.set_ylim((-10,120))
        ax.invert_yaxis()
        yticks = range(-10,130,10)
        ax.set_yticks(ticks=yticks)
        ax.set_ylabel("Hearing Threshold (dB HL)")
        ax.semilogx()
        ax.set_xlim((200,9500))
        ax.set_xticks(ticks=[250,500,1000,2000,4000,8000], labels=['250','500','1000','2000','4000','8000'])
        ax.tick_params(axis='x', which='minor', bottom=False)
        ax.set_xlabel("Frequency (Hz)")
        ax.axhline(y=25, color="black", linestyle='--', linewidth=1)
        ax.grid()
        #ax.set_title(f"Study Audiograms (n={n})")
        return ax


    ###############################
    # Acoustic Coupling Functions #
    ###############################
    def coupling(self, sub_id):
        """ Calculate Pro Fit recommended coupling and vent size.
        """
        # Get subject thresholds
        ac, bc = self.get_thresholds(sub_id)

        # RIC coupling logic
        sides = ['RightAC ', 'LeftAC ']
        coupling = {}
        vent_size = {}
        matrix = {}

        for side in sides:
            # RIC matrix selection logic
            # Step 1: determine recommendation threshold
            try:
                if (ac[side + '2000'] >= ac[side + '500']):
                    recommendation_threshold = ac[side + '2000']
                elif (ac[side + '500'] > ac[side + '2000']):
                    recommendation_threshold = ac[side + '500'] + 10
            except TypeError:
                raise TypeError

            # Step 2: choose matrix based on recommendation threshold
            if recommendation_threshold <= 65:
                power = 'M'
                #receiver = 'stock'
            elif (recommendation_threshold <= 75) and (recommendation_threshold > 65):
                power = 'P'
                #receiver = 'stock'
            elif (recommendation_threshold <= 80) and (recommendation_threshold > 75):
                power = 'P'
                #receiver = 'custom cased'
            elif recommendation_threshold > 80:
                power = 'UP'
                #reciever = 'custom cased'

            matrix[side[:-3]] = power

            # RIC acoustic coupling logic
            # This is partly based on the matrix recommendation from above
            try:
                # Open dome
                if (ac[side + '250'] and ac[side + '500'] < 30) \
                    and (ac[side + '1000'] <= 60) \
                    and (matrix[side[:-3]] in ['S', 'M', 'P']):
                        coupling[side[:-3]] = 'Open Dome'

                # Occluded dome
                elif (ac[side + '250'] or ac[side + '500'] > 30) \
                    and (ac[side + '250'] and ac[side + '500'] <= 50) \
                    and (ac[side + '1000'] <= 60) \
                    and (matrix[side[:-3]] in ['S', 'M', 'P']):
                        coupling[side[:-3]] = 'Occluded Dome'

                # Earmolds
                # Dome unless...
                elif (ac[side + '250'] or ac[side + '500'] > 50):
                    coupling[side[:-3]] = 'Earmold'

                # Earmold
                elif (ac[side + '1000'] > 60):
                    coupling[side[:-3]] = 'Earmold'

                # Earmold
                elif matrix == 'UP':
                    coupling[side[:-3]] = 'Earmold'

                # Cannot categorize
                else:
                    coupling[side[:-3]] = 'Error!'

            except TypeError:
                coupling[side[:-3]] = '-'

            # RIC (and custom) vent size
            if coupling[side[:-3]] == 'Earmold':
                # Get average threshold at 500 and 1000 Hz
                avg500_1k = np.mean([ac[side + '500'], ac[side + '1000']])
                if avg500_1k <= 40:
                    vent_size[side[:-3]] = 'Large'
                elif avg500_1k < 55:
                    vent_size[side[:-3]] = 'Medium'
                elif avg500_1k >= 55:
                    vent_size[side[:-3]] = 'Small'
                else:
                    vent_size[side[:-3]] = 'Models_322: Calculation Error!'
            else:
                vent_size[side[:-3]] = 'NA'

        return matrix, coupling, vent_size


    def update_label_vars(self, _vars, record):
        """ Populate _vars with data from provided record number.
        """
        # Assign variables
        self._vars = _vars

        # Attempt to parse study name and dates
        # Multiple pieces of information in a single cell
        latest_study = self.data[self.data['Subject Id'] == record]['Latest Study'].values[0]
        study_dates = [z.split(')')[0] for z in latest_study.split('(') if ')' in z]
        try:
            study_dates = study_dates[0]
        except:
            study_dates = '-'
        study_info = latest_study.split('(')[0]
        self._vars['study_dates'].set(study_dates)
        self._vars['study_info'].set(study_info)

        try:
            matrix, coupling, vent_size = self.coupling(record)
            self._vars['r_rec_coupling'].set(coupling['Right'])
            self._vars['l_rec_coupling'].set(coupling['Left'])
            self._vars['r_rec_vent'].set(vent_size['Right'])
            self._vars['l_rec_vent'].set(vent_size['Left'])
            self._vars['l_matrix'].set(matrix['Left'])
            self._vars['r_matrix'].set(matrix['Right'])
        except TypeError as e:
            print(f"\ndbmodel: {e}")
            print("dbmodel: Failed to calculate coupling type!")

        dict = {
            'age': 'Age',
            'miles_away': 'Miles From Starkey',
            'smartphone_type': 'Smartphone Type',
            'will_not_wear': 'Will Not Wear',
            'r_style': 'RightStyle',
            'l_style': 'LeftStyle',
            'r_coupling': 'Right Earmold Style',
            'l_coupling': 'Left Earmold Style',
            'r_receiver': 'Right Ric Cable Size',
            'l_receiver': 'Left Ric Cable Size',
        }

        for key in dict.keys():
            try:
                if dict[key] in ['Age', 'Miles From Starkey', 'Right Ric Cable Size', 'Left Ric Cable Size']:
                    try:
                        self._vars[key].set(int(self.data[self.data['Subject Id'] == record][dict[key]].values[0]))
                    except ValueError as e:
                        self._vars[key].set('-')
                else:
                    self._vars[key].set(self.data[self.data['Subject Id'] == record][dict[key]].values[0])
            except KeyError as e:
                print(f"dbmodel: KeyError: value not in list{e}")


class DataModel:
    """ Handle subject db record data """
    fields = {
        "age": {'req': True, 'type': FT.string},
        "miles_away": {'req': True, 'type': FT.string},
        "smartphone_type": {'req': True, 'type': FT.string},
        'study_dates': {'req': True, 'type': FT.string},
        'study_info': {'req': True, 'type': FT.string},
        'will_not_wear': {'req': True, 'type': FT.string},
        'r_style': {'req': True, 'type': FT.string},
        'l_style': {'req': True, 'type': FT.string},
        'r_receiver': {'req': True, 'type': FT.string},
        'l_receiver': {'req': True, 'type': FT.string},
        'r_coupling': {'req': True, 'type': FT.string},
        'l_coupling': {'req': True, 'type': FT.string},
        'r_rec_coupling': {'req': True, 'type': FT.string},
        'l_rec_coupling': {'req': True, 'type': FT.string},
        'r_rec_vent': {'req': True, 'type': FT.string},
        'l_rec_vent': {'req': True, 'type': FT.string},
        'r_matrix': {'req': True, 'type': FT.string},
        'l_matrix': {'req': True, 'type': FT.string}
    }
