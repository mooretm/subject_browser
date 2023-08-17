""" Database model for the Subject Browser 

    Expects a .csv file of the entire 'General Search' tab 
    from the online subject database. 

    Author: Travis M. Moore
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
        """ Apply filters to data.
        """
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
        if operator == "not in":
            self.data = self.data[~self.data[colname].isin(value)]
        print(f"\ndbmodel: Filtered column '{colname}' for {value}")
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


    ##########################
    # Descriptive Statistics #
    ##########################
    def descriptive_stats(self):
        dstats = {}

        # Number of subjects
        dstats['n'] = int(self.data.shape[0])

        # 3-frequency PTA: 0.5, 1, 2 kHz
        # Right
        r_pta3_all = self.data[['RightAC 500', 'RightAC 1000', 
                                'RightAC 2000']].mean(axis=1)
        dstats['r_pta3'] = np.round(r_pta3_all.mean(), 1)
        # Left
        l_pta3_all = self.data[['LeftAC 500', 'LeftAC 1000', 
                                'LeftAC 2000']].mean(axis=1)
        dstats['l_pta3'] = np.round(l_pta3_all.mean(), 1)

        # 4-frequency PTA: 0.5, 1, 2, 4 kHz
        # Right
        r_pta4_all = self.data[['RightAC 500', 'RightAC 1000', 
                                'RightAC 2000', 'RightAC 4000']].mean(axis=1)
        dstats['r_pta4'] = np.round(r_pta4_all.mean(), 1)
        # Left
        l_pta4_all = self.data[['LeftAC 500', 'LeftAC 1000', 
                                'LeftAC 2000', 'LeftAC 4000']].mean(axis=1)
        dstats['l_pta4'] = np.round(l_pta4_all.mean(), 1)

        # Age
        dstats['age_mean'] = np.round(self.data['Age'].mean(axis=0), 1)
        dstats['age_max'] = int(self.data['Age'].max())
        dstats['age_min'] = int(self.data['Age'].min())

        # MoCA Total Score
        dstats['moca_mean'] = np.round(
            self.data['MoCA Total Score'].mean(axis=0), 1)
        dstats['moca_min'] = int(self.data['MoCA Total Score'].min())
        dstats['moca_max'] = int(self.data['MoCA Total Score'].max())

        return dstats


    ######################
    # Plotting Functions #
    ######################
    def get_thresholds(self, sub_id):
        """ Make dictionaries of air and bone conduction thresholds.
        """
        # Get AC thresholds
        sides = ["RightAC", "LeftAC"]
        freqs = [250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000]
        ac = {}
        for side in sides:
            for freq in freqs:
                colname = side + " " + str(freq)
                try:
                    ac[side + ' ' + str(freq)] = int(
                        self.data[self.data['Subject Id'] == sub_id][colname].values[0]
                    )
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

        # Plot (collapsed) average thresholds
        #avg = thresholds.mean()
        #ax.plot(avg.index, avg, color='black', linestyle='--', linewidth=5)
        
        # Plot (ear-specific) average thresholds
        ax.plot(right.columns, right.mean(), c='red', lw=4)
        ax.plot(left.columns, left.mean(), c='blue', lw=4)

        plt.show()


    def plot_ear_specific_group_audio(self):
        """ Plot overlaid audiograms for each subject 
            currently in self.data.
        """
        # Call audiogram plot axis
        ax = self._group_audio_axis()
        thresholds, right, left = self._get_audio_thresholds()
        ax.set_title(f"Audiograms (n={int(thresholds.shape[0]/2)})")

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
        return ax


    ###############################
    # Acoustic Coupling Functions #
    ###############################
    def coupling(self, sub_id):
        """ Calculate Pro Fit recommended coupling, receiver gain, 
            and vent size. Based on logic from Pro Fit provided by 
            Laura Woodworth. 
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
        # Multiple pieces of information in a single cell...
        latest_study = self.data[self.data['Subject Id'] == record]['Latest Study'].values[0]
        study_dates = [z.split(')')[0] for z in latest_study.split('(') if ')' in z]
        try:
            study_dates = study_dates[0]
        except:
            study_dates = '-'
        study_info = latest_study.split('(')[0]
        self._vars['study_dates'].set(study_dates)
        self._vars['study_info'].set(study_info)

        # Add matrix, coupling and vent size to _vars
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

        # Add fields from dict to _vars, and update those values.
        # This updates the labels on the GUI due to use of tk.StringVars
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
