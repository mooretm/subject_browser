""" Subject Browser

    Updated version of original subject_browser using BASE GUI 3.
    Refactored existing code and extended functionality significantly. 

    Written by: Travis M. Moore
    Created: July 26, 2022
"""

###########
# Imports #
###########
# Import GUI packages
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

# Import system packages
import os

# Import misc packages
import webbrowser
import markdown

# Import custom modules
# Menu imports
from menus import mainmenu
# Function imports
from functions import general
# Model imports
from models import sessionmodel
from models import versionmodel
from models import csvmodel
from models import dbmodel
from models.constants import FieldTypes as FT
# View imports
from views import sessionview
from views import filterview
from views import browserview


#########
# BEGIN #
#########
class Application(tk.Tk):
    """ Application root window
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #############
        # Constants #
        #############
        self.NAME = 'Subject Browser'
        self.VERSION = '1.0.0'
        self.EDITED = 'August 15, 2023'

        # Create menu settings dictionary
        self._app_info = {
            'name': self.NAME,
            'version': self.VERSION,
            'last_edited': self.EDITED
        }

        # Define data types
        self.var_types = {
            FT.string: tk.StringVar,
            FT.string_list: tk.StringVar,
            FT.short_string_list: tk.StringVar,
            FT.iso_date_string: tk.StringVar,
            FT.long_string: tk.StringVar,
            FT.decimal: tk.DoubleVar,
            FT.integer: tk.IntVar,
            FT.boolean: tk.BooleanVar
        }

        # Allow widgets to float
        self.columnconfigure(5, weight=1)
        self.rowconfigure(5, weight=1)


        ######################################
        # Initialize Models, Menus and Views #
        ######################################
        # Setup main window
        self.withdraw() # Hide window during setup
        self.resizable(False, False)
        self.title(self.NAME)

        # Assign special quit function on window close
        # Used to close Vulcan session cleanly even if 
        # user closes window via "X"
        self.protocol('WM_DELETE_WINDOW', self._quit)

        # Load current session parameters from file
        # or load defaults if file does not exist yet
        # Check for version updates and destroy if mandatory
        self.sessionpars_model = sessionmodel.SessionParsModel(self._app_info)
        self._load_sessionpars()
        self.sessionpars_model.save()

        # Create filter model
        #self.filtermodel = filtermodel.FilterList()

        # Create sample database model
        self._create_sample_db()

        # Create notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=5, column=5, padx=10, pady=10)

        # Load filter view
        self.filter_view = filterview.FilterView(self.notebook, self.db, self.sessionpars)
        self.filter_view.grid(row=5, column=5)

        # Load browser view
        self.browser_view = browserview.BrowserView(self.notebook, self.db, 
            self.dbmodel)
        self.browser_view.grid(row=5, column=5)

        # Add tabs to notebook
        self.notebook.add(self.filter_view, text='Filter')
        self.notebook.add(self.browser_view, text='Browse')

        # Load CSV writer model
        self.csvmodel = csvmodel.CSVModel(self.sessionpars)

        # Load menus
        self.menu = mainmenu.MainMenu(self, self._app_info)
        self.config(menu=self.menu)

        # Create callback dictionary
        event_callbacks = {
            # File menu
            #'<<FileSession>>': lambda _: self._show_session_dialog(),
            '<<FileImportFullDB>>': lambda _: self._import_full(),
            '<<FileImportFilteredDB>>': lambda _: self._import_filtered(),
            '<<FileExportDB>>': lambda _: self.db.write(), #self._export_db(),
            '<<FileImportFilterVals>>': lambda _: self._import_csv_filter_vals(),
            '<<FileExportFilterVals>>': lambda _: self._export_filter_vals(),
            '<<FileQuit>>': lambda _: self._quit(),

            # Tools menu
            '<<ToolsReset>>': lambda _: self.filter_view.clear_filters(),
            '<<ToolsPlotGroupAudio>>': lambda _: self.db.plot_group_audio(),
            '<<ToolsPlotEarSpecificGroupAudio>>': lambda _: self.db.plot_ear_specific_group_audio(),

            # Help menu
            '<<Help>>': lambda _: self._show_help(),

            # Session dialog commands
            '<<SessionSubmit>>': lambda _: self._save_sessionpars(),

            # Filter view
            '<<FilterviewFilter>>': lambda _: self._get_filterview_vals(),
            '<<FilterviewScrubToggled>>': lambda _: self._save_sessionpars(), #self.save_pars(), #self.sessionpars_model.save()
        }

        # Bind callbacks to sequences
        for sequence, callback in event_callbacks.items():
            self.bind(sequence, callback)

        # Center main window
        self.center_window()

        # Check for updates
        if (self.sessionpars['check_for_updates'].get() == 'yes') and \
        (self.sessionpars['config_file_status'].get() == 1):
            _filepath = self.sessionpars['version_lib_path'].get()
            u = versionmodel.VersionChecker(_filepath, self.NAME, self.VERSION)
            if u.status == 'mandatory':
                messagebox.showerror(
                    title="New Version Available",
                    message="A mandatory update is available. Please install " +
                        f"version {u.new_version} to continue.",
                    detail=f"You are using version {u.app_version}, but " +
                        f"version {u.new_version} is available."
                )
                self.destroy()
            elif u.status == 'optional':
                messagebox.showwarning(
                    title="New Version Available",
                    message="An update is available.",
                    detail=f"You are using version {u.app_version}, but " +
                        f"version {u.new_version} is available."
                )
            elif u.status == 'current':
                pass
            elif u.status == 'app_not_found':
                messagebox.showerror(
                    title="Update Check Failed",
                    message="Cannot retrieve version number!",
                    detail=f"'{self.NAME}' does not exist in the version library."
                 )
            elif u.status == 'library_inaccessible':
                messagebox.showerror(
                    title="Update Check Failed",
                    message="The version library is unreachable!",
                    detail="Please check that you have access to Starfile."
                )


    #####################
    # General Functions #
    #####################
    def center_window(self):
        """ Center the root window 
        """
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
        x = screen_width/2 - size[0]/2
        y = screen_height/2 - size[1]/2
        self.geometry("+%d+%d" % (x, y))
        self.deiconify()


    def _create_sample_db(self):
        """ Load in default database and create dbmodel.
        """
        # If running from compiled, look in compiled temp location
        print('controller: Looking for compiled default database...')
        db_path = general.resource_path('sample_data.csv')
        file_exists = os.access(db_path, os.F_OK)
        if not file_exists:
            print("controller: Not found! Checking local folder...")
            self.db = dbmodel.SubDB(".\\assets\\sample_data.csv")
        else:
            self.db = dbmodel.SubDB(db_path)

        # Load in dict fields for displaying records
        self.dbmodel = dbmodel.DataModel()
        fields = self.dbmodel.fields
        self._vars = {
            key: self.var_types[spec['type']]()
            for key, spec in fields.items()
        }


    def save_pars(self):
        self.sessionpars_model.set()
        self.sessionpars_model.save()


    ###################
    # File Menu Funcs #
    ###################
    def _import_full(self):
        """ Load FULL database .csv file (i.e., not previously
            imported)
        """
        # Query user for database .csv file
        filename = filedialog.askopenfilename()
        # Do nothing if cancelled
        if not filename:
            return

        # If a valid filename is found, load it
        self.db.load_db(filename)

        # Get 'initial scrub' checkbox state
        if self.sessionpars['initial_scrub'].get() == 1:
            self._initial_scrub()
        else:
            # Clear any previous output from textbox
            self.filter_view.clear_output()
            # Show total record count
            self.filter_view.txt_output.insert(tk.END,
                f"Candidates before filtering: {str(self.db.data.shape[0])}\n\n")

        # Reload the treeview with imported database
        self.browser_view.load_tree()


    def _import_filtered(self):
        """ Load previously-imported database .csv file
            (i.e., an file exported from this app)
        """
        # Query user for database .csv file
        filename = filedialog.askopenfilename()
        # Do nothing if cancelled
        if not filename:
            return
        # If a valid filename is found, load it
        self.db.load_filtered_db(filename)

        # Clear any previous output from textbox
        self.filter_view.clear_output()
        # Show total record count
        self.filter_view.txt_output.insert(tk.END,
            f"Candidates before filtering: {str(self.db.data.shape[0])}\n\n")       

        # Reload the treeview with imported database
        self.browser_view.load_tree()


    def _import_csv_filter_vals(self):
        """ Read external filter values list and update filterview
            comboboxes with values
        """
        # Get imported filter values as dict
        #filter_dict = self.filtermodel.import_filter_dict()
        filter_dict = self.csvmodel.import_filter_dict()
        self.on_filter(filter_dict)


    def _export_filter_vals(self):
        """ Write filterview combobox values to .csv file
        """
        filter_dict = self.filter_view._make_filter_dict()
        self.csvmodel.export_filters(filter_dict)


    def _quit(self):
        """ Exit the application.
        """
        self.destroy()


    ##########################
    # Filter View Functions #
    ##########################
    def _get_filterview_vals(self):
        # Get current filter values
        filter_dict = self.filter_view._make_filter_dict()
        filter_dict = self._format_filter_vals(filter_dict)
        self.on_filter(filter_dict)


    def _format_filter_vals(self, filter_dict):
        """ Convert filter values to float, where possible.

            Returns: new filter dictionary with updated data types.
        """
        for key in filter_dict:
            if (filter_dict[key][1] == 'contains') or \
                (filter_dict[key][1] == 'not in'):
                try:
                    # Split string of filter values into list
                    vals = filter_dict[key][2].split()
                    # Iterate through list converting to float
                    filter_dict[key][2] = [float(x) for x in vals]
                except ValueError:
                    # Cannot convert string to float
                    filter_dict[key][2] = vals
            else:
                try:
                    filter_dict[key][2] = float(filter_dict[key][2])
                except ValueError:
                    # Cannot convert string to float
                    pass

        # print(f"\ncontroller: key = {key} \
        #         \nsearch term = {filter_dict[key][0]} \
        #         \noperater = {filter_dict[key][1]} \
        #         \nvalue = {filter_dict[key][2]}, type = {type(filter_dict[key][2])} \
        # ")

        return filter_dict                


    def on_filter(self, filter_dict):
        """ Called from filterview 'Filter Records' button event. 
            Call filter method of dbmodel.
            Update tree widget after filtering. 
        """
        # Clear any previous output from textbox
        self.filter_view.clear_output()

        # Remind user what the previous record count was
        self.filter_view.txt_output.insert(tk.END,
            f"Candidates before filtering: {str(self.db.data.shape[0])}\n\n")

        print(f"\ncontroller: Filter dict: {filter_dict.items()}")

        # Extract filter dict values and pass to db filter function
        try:
            for val in filter_dict:
                self.db.filter(
                    filter_dict[val][0],
                    filter_dict[val][1],
                    filter_dict[val][2]
                )
                self.filter_view.txt_output.insert(tk.END, 
                    f"Filtering by: {filter_dict[val][0]} " +
                    f"{filter_dict[val][1]} {filter_dict[val][2]}...\n" +
                    f"Remaining Candidates: {str(self.db.data.shape[0])}\n\n")
                # Scroll to bottom of text box
                self.filter_view.txt_output.yview(tk.END)
        except TypeError as e:
            print(e)
            messagebox.showerror(title="Filtering Error",
                message="Cannot compare different data types!",
                detail="The search term data type does not match the " +
                    "database data type. This can happen when importing " +
                    "a filtered database, or faulty filtering code. " +
                    "Aborting.")

        # Update tree widget after filtering
        self.browser_view.load_tree()


    def _initial_scrub(self):
        """ Perform perfunctory junk record removal
        """
        # Create dictionary of filtering values
        filter_dict = {
            1: ("Status", "equals", "Active"),
            2: ("Good Candidate", "does not equal", "Poor"),
            3: ("Employment Status", "does not equal", "Employee"),
            #4: ("Miles From Starkey", "<=", 60)
        }

        # Call filter function
        self.on_filter(filter_dict)


    #########################
    # Browse View Functions #
    #########################
    def _show_audio(self, record):
        """ Retrieve figure axis handle and plot audio 
        """
        ax1 = self.browser_view.plot_audio()
        self.db.audio_ac(record, ax1)


    ########################
    # Tools Menu Functions #
    ########################


    ############################
    # Session Dialog Functions #
    ############################
    def _show_session_dialog(self):
        """ Show session parameter dialog
        """
        print("\ncontroller: Calling session dialog...")
        sessionview.SessionDialog(self, self.sessionpars)


    def _load_sessionpars(self):
        """ Load parameters into self.sessionpars dict 
        """
        vartypes = {
        'bool': tk.BooleanVar,
        'str': tk.StringVar,
        'int': tk.IntVar,
        'float': tk.DoubleVar
        }

        # Create runtime dict from session model fields
        self.sessionpars = dict()
        for key, data in self.sessionpars_model.fields.items():
            vartype = vartypes.get(data['type'], tk.StringVar)
            self.sessionpars[key] = vartype(value=data['value'])
        print("\ncontroller: Loaded sessionpars model fields into " +
            "running sessionpars dict")


    def _save_sessionpars(self, *_):
        """ Save current runtime parameters to file 
        """
        for key, variable in self.sessionpars.items():
            self.sessionpars_model.set(key, variable.get())
            self.sessionpars_model.save()
        print("\ncontroller: Saved variables to config file")


    #######################
    # Help Menu Functions #
    #######################
    def _show_help(self):
        """ Create html help file and display in default browser
        """
        print("controller: Looking for help file in compiled " +
            "version temp location...")
        help_file = general.resource_path('README\\README.html')
        file_exists = os.access(help_file, os.F_OK)
        if not file_exists:
            print('controller: Not found!\nChecking for help file in ' +
                'local script version location')
            # Read markdown file and convert to html
            with open('README.md', 'r') as f:
                text = f.read()
                html = markdown.markdown(text)

            # Create html file for display
            with open('.\\assets\\README\\README.html', 'w') as f:
                f.write(html)

            # Open README in default web browser
            webbrowser.open('.\\assets\\README\\README.html')
        else:
            webbrowser.open(help_file)


if __name__ == "__main__":
    app = Application()
    app.mainloop()
