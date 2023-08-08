""" Subject Browser

    Updated version of original subject_browser. Rebuilt within the 
    newest BASE GUI 3. 

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
from models import filtermodel
from models.constants import FieldTypes as FT
# View imports
from views import mainview
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
        self.EDITED = 'July 26, 2023'

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


        # UGH
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

        # Create filter settings dict
        self.filter_dict = {}

        # Create filter model
        self.filtermodel = filtermodel.FilterList()

        # Create sample database model
        self._create_sample_db()

        # Create notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=5, column=5, padx=10, pady=10)

        # Load filter view
        self.filter_view = filterview.FilterView(self.notebook, self.db, self.filter_dict)
        self.filter_view.grid(row=5, column=5)

        # Load browser view
        self.browser_view = browserview.BrowserView(self.notebook, self.db, self.dbmodel)
        self.browser_view.grid(row=5, column=5)

        # Add tabs to notebook
        self.notebook.add(self.filter_view, text='Filter')
        self.notebook.add(self.browser_view, text='Browse')

        # Load current session parameters from file
        # or load defaults if file does not exist yet
        # Check for version updates and destroy if mandatory
        self.sessionpars_model = sessionmodel.SessionParsModel(self._app_info)
        self._load_sessionpars()

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
            '<<FileExportDB>>': lambda _: self._export_db(),
            '<<FileImportList>>': lambda _: self._import_filter_list(),
            '<<FileExportList>>': lambda _: self._export_filter_list(),
            '<<FileQuit>>': lambda _: self._quit(),

            # Tools menu
            '<<ToolsReset>>': lambda _: self._reset_filters(),

            # Help menu
            '<<Help>>': lambda _: self._show_help(),

            # Session dialog commands
            '<<SessionSubmit>>': lambda _: self._save_sessionpars(),

            # Filter view
            '<<Filter>>': lambda _: self._on_filter(),
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
        print('controller: Looking for default database file...')
        db_path = general.resource_path('sample_data.csv')
        file_exists = os.access(db_path, os.F_OK)
        if not file_exists:
            print("controller: Checking local folder...")
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


    def _initial_scrub(self):
        """ Perform perfunctory junk record removal
        """
        # Clear any previous output from textbox
        self.filter_view.txt_output.delete('1.0', tk.END)
        # Provide feedback
        self.filter_view.txt_output.insert(tk.END, 
                f"controller: Loaded database records" +
                f"controller: Remaining Candidates: {str(self.db.data.shape[0])}")
        
        # Scroll to bottom of text box
        self.filter_view.txt_output.yview(tk.END)

        # Create dictionary of filtering values
        scrub_dict = {
            1: ("Status", "equals", "Active"),
            2: ("Good Candidate", "does not equal", "Poor"),
            3: ("Employment Status", "does not equal", "Employee"),
            4: ("Miles From Starkey", "<=", "60")
        }
        # Call filtering function
        self._filter(scrub_dict)
        # Update tree widget after filtering
        self.browser_view.load_tree()


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

        if self.filter_view.scrub_var.get() == 1:
            # Remove junk records
            self._initial_scrub()
        else:
            # Clear any previous output from textbox
            self.filter_view.txt_output.delete('1.0', tk.END)
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

        # Reload the treeview with imported database
        self.browser_view.load_tree()


    def _export_db(self):
        """ Write current database object to .csv file
        """
        self.db.write()


    def _import_filter_list(self):
        """ Read external filter values list and update filterview
            comboboxes with values
        """
        # Get updated filter values dict
        self.filter_dict = self.filtermodel.import_filter_dict()
        self._filter(self.filter_dict)


    def _export_filter_list(self):
        """ Write filterview combobox values to .csv file
        """
        self.filtermodel.export_filters(self.filter_view.filter_dict)
    

    def _quit(self):
        """ Exit the application.
        """
        self.destroy()


    ##########################
    # Filter View Functions #
    ##########################
    def _on_filter(self):
        """ Called from filterview 'Filter Records' button event. 
            Update filter dict and pass to filter func.
        """
        # Update local filter dict with values from filterview
        self.filter_dict = self.filter_view.filter_dict
        # Call filter func using updated filter dict
        self._filter(self.filter_dict)


    def _filter(self, filter_val_dict):
        """ Call filter method of dbmodel to subset database.
            Update tree widget after filtering. 
        """
        if not filter_val_dict:
            messagebox.showwarning(title="No Filters Found",
                message="No filters have been set!")
            return

        # For DEBUG:
        # print(filter_val_dict)
        # keys = filter_val_dict.keys()
        # for key in keys:
        #     print(type(filter_val_dict[key][2]))
        # print("Column data type for miles from starkey")
        # print(self.db.data.dtypes['Miles From Starkey'])

        # Clear any previous output from textbox
        self.filter_view.txt_output.delete('1.0', tk.END)

        # Remind user what the previous record count was
        self.filter_view.txt_output.insert(tk.END,
            f"Candidates before filtering: {str(self.db.data.shape[0])}\n\n")

        try:
            for val in filter_val_dict:
                self.db.filter(
                    filter_val_dict[val][0],
                    filter_val_dict[val][1],
                    filter_val_dict[val][2]
                )
                self.filter_view.txt_output.insert(tk.END, 
                    f"Filtering by: {filter_val_dict[val][0]} " +
                    f"{filter_val_dict[val][1]} {filter_val_dict[val][2]}...\n" +
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


    #########################
    # Browse View Functions #
    #########################
    def _show_audio(self, record):
        """ Retrieve figure axis handle and plot audio 
        """
        ax1 = self.browser_view.plot_audio()
        self.db.audio_ac(record, ax1)


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
        print("\ncontroller: Calling sessionpars model set and save funcs")
        for key, variable in self.sessionpars.items():
            self.sessionpars_model.set(key, variable.get())
            self.sessionpars_model.save()


    ########################
    # Tools Menu Functions #
    ########################
    def _reset_filters(self):
        self.filter_view._clear_filters()


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
