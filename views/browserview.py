""" Browser view for Subject Browser 
"""

###########
# Imports #
###########
# Import GUI packages
import tkinter as tk
from tkinter import ttk

# Import plotting packages
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import custom modules
from models.constants import FieldTypes as FT


#########
# BEGIN #
#########
class BrowserView(ttk.Frame):
    """ Browsing view for 'Browse' tab of notebook
    """

    # Define data types
    var_types = {
        FT.string: tk.StringVar,
        FT.string_list: tk.StringVar,
        FT.short_string_list: tk.StringVar,
        FT.iso_date_string: tk.StringVar,
        FT.long_string: tk.StringVar,
        FT.decimal: tk.DoubleVar,
        FT.integer: tk.IntVar,
        FT.boolean: tk.BooleanVar
    }


    def __init__(self, parent, database, dbmodel, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Assign variables
        self.db = database
        self.dbmodel = dbmodel
        fields = self.dbmodel.fields
        
        self._vars = {
            key: self.var_types[spec['type']]()
            for key, spec in fields.items()
        }

        # Change weights so widgets "float" in the center
        # of the frame
        for ii in [0, 1, 5, 10, 15]:
            self.columnconfigure(ii, weight=1)
            self.rowconfigure(ii, weight=1)


        #################
        # Create Frames #
        #################
        style = ttk.Style()
        style.configure("rec.TLabel", foreground='green')
        style.configure("new.Treeview", highlightthickness=5, bd=4)
        style.configure("new.Treeview.Heading", font=('TkDefaultFont', 10, 'bold'))

        options = {'padx':10, 'pady':10}
        label_options = {'padx': 10, 'pady': (0, 10)}

        # Main container
        self.frm_main = ttk.Frame(self)
        self.frm_main.grid(row=5, column=5, **options)
        for ii in range(0, 50):
            self.frm_main.columnconfigure(ii, weight=1)
            self.frm_main.rowconfigure(ii, weight=1)
        
        # Subject info
        lfrm_data = ttk.LabelFrame(self.frm_main, text="Subject Data")
        lfrm_data.grid(row=5, column=10, **label_options, sticky='nsew')
        
        # Left device info
        lfrm_left = ttk.LabelFrame(self.frm_main, text="Left Side")
        lfrm_left.grid(row=10, column=10, **label_options, sticky='nsew')

        # Right device info
        lfrm_right = ttk.LabelFrame(self.frm_main, text="Right Side")
        lfrm_right.grid(row=15, column=10, **label_options, sticky='nsew')


        ################
        # Subject Info #
        ################
        # Age
        ttk.Label(lfrm_data, text="Age:").grid(row=0, column=0, sticky='e')
        ttk.Label(lfrm_data, textvariable=self._vars['age']).grid(row=0, 
            column=1, sticky='w')
        
        # Miles away
        #ttk.Label(lfrm_data, text="Miles Away:").grid(row=1, column=0, 
        # sticky='e')
        #ttk.Label(lfrm_data, textvariable=self._vars['miles_away']).grid(
        # row=1, column=1, sticky='w', **data_options)

        # Smartphone
        ttk.Label(lfrm_data, text="Smartphone:").grid(row=2, column=0, 
            sticky='e')
        ttk.Label(lfrm_data, textvariable=self._vars['smartphone_type']).grid(
            row=2, column=1, sticky='w')

        # Last study
        # Study info
        ttk.Label(lfrm_data, text="Study Info:").grid(row=3, column=0, 
            sticky='e')
        lbl_studyinfo = ttk.Label(lfrm_data, width=30,
            textvariable=self._vars['study_info'])
        lbl_studyinfo.grid(row=3, column=1, sticky='w')
        lbl_studyinfo.grid_propagate(False)
        
        # Study dates
        ttk.Label(lfrm_data, text="Study Dates:").grid(row=4, column=0, 
            sticky='e')
        ttk.Label(lfrm_data, textvariable=self._vars['study_dates']).grid(
            row=4, column=1, sticky='w')
        
        # Will not wear
        ttk.Label(lfrm_data, text="Will Not Wear:").grid(row=5, column=0, 
            sticky='e')
        ttk.Label(lfrm_data, textvariable=self._vars['will_not_wear']).grid(
            row=5, column=1, sticky='w')


        ####################
        # LEFT Device Info #
        ####################
        # Device
        ttk.Label(lfrm_left, text="Device:").grid(row=0, column=0, sticky='e')
        ttk.Label(lfrm_left, textvariable=self._vars['l_style'], 
            width=30).grid(row=0, column=1, sticky='w')
        
        # Receiver length
        ttk.Label(lfrm_left, text="Receiver Length:").grid(row=1, column=0, 
            sticky='e')
        ttk.Label(lfrm_left, textvariable=self._vars['l_receiver']).grid(
            row=1, column=1, sticky='w')
        
        # Coupling
        ttk.Label(lfrm_left, text="Current Coupling:").grid(row=2, column=0, 
            sticky='e')
        ttk.Label(lfrm_left, textvariable=self._vars['l_coupling']).grid(
            row=2, column=1, sticky='w')
        
        # Pro Fit suggested coupling
        ttk.Label(lfrm_left, text="Pro Fit Coupling:", 
            style='rec.TLabel').grid(row=3, column=0, sticky='e')
        ttk.Label(lfrm_left, textvariable=self._vars['l_rec_coupling'], 
            style='rec.TLabel').grid(row=3, column=1, sticky='w')
        
        # Pro Fit suggested vent size
        ttk.Label(lfrm_left, text="Pro Fit Vent Size:", 
            style='rec.TLabel').grid(row=4, column=0, sticky='e')
        ttk.Label(lfrm_left, textvariable=self._vars['l_rec_vent'], 
            style='rec.TLabel').grid(row=4, column=1, sticky='w')
        
        # Pro Fit suggested matrix
        ttk.Label(lfrm_left, text="Pro Fit Matrix:", 
            style='rec.TLabel').grid(row=5, column=0, sticky='e')
        ttk.Label(lfrm_left, textvariable=self._vars['l_matrix'], 
            style='rec.TLabel').grid(row=5, column=1, sticky='w')


        #####################
        # RIGHT Device Info #
        #####################
        # Device
        ttk.Label(lfrm_right, text="Device:").grid(row=0, column=0, 
            sticky='e')
        ttk.Label(lfrm_right, textvariable=self._vars['r_style']).grid(
            row=0, column=1, sticky='w')
        
        # Receiver length
        ttk.Label(lfrm_right, text="Receiver Length:").grid(row=1, column=0, 
            sticky='e')
        ttk.Label(lfrm_right, textvariable=self._vars['r_receiver']).grid(
            row=1, column=1, sticky='w')
        
        # Coupling
        ttk.Label(lfrm_right, text="Current Coupling:").grid(row=2, column=0, 
            sticky='e')
        ttk.Label(lfrm_right, textvariable=self._vars['r_coupling']).grid(
            row=2, column=1, sticky='w')
        
        # ProFit suggested coupling
        ttk.Label(lfrm_right, text="Pro Fit Coupling:", 
            style='rec.TLabel').grid(row=3, column=0, sticky='e')
        ttk.Label(lfrm_right, textvariable=self._vars['r_rec_coupling'], 
            style='rec.TLabel').grid(row=3, column=1, sticky='w')
        
        # ProFit suggested vent size
        ttk.Label(lfrm_right, text="Pro Fit Vent Size:", 
            style='rec.TLabel').grid(row=4, column=0, sticky='e')
        ttk.Label(lfrm_right, textvariable=self._vars['r_rec_vent'], 
            style='rec.TLabel').grid(row=4, column=1, sticky='w')
        
        # Pro Fit suggested matrix
        ttk.Label(lfrm_right, text="Pro Fit Matrix:", 
            style='rec.TLabel').grid(row=5, column=0, sticky='e')
        ttk.Label(lfrm_right, textvariable=self._vars['r_matrix'], 
            style='rec.TLabel').grid(row=5, column=1, sticky='w')

        # Call audio plot
        self.plot_audio()


        ####################
        # Subject Treeview #
        ####################
        columns = ('subject_id')
        self.tree = ttk.Treeview(self.frm_main, columns=columns, 
            show='headings')

        # Headings
        self.tree.heading('subject_id', text='Subject ID')

        # Columns
        self.tree.column("subject_id", width=100, anchor=tk.CENTER)

        # Populate tree with data
        self.load_tree()

        # Bind function to tree
        self.tree.bind('<<TreeviewSelect>>', self._item_selected)

        # Display tree
        self.tree.grid(row=5, column=0, rowspan=20, sticky='ns')

        # Add vertical scrollbar
        self.scrollbar = ttk.Scrollbar(self.frm_main, orient=tk.VERTICAL,
            command=self.tree.yview)
        self.tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.grid(row=5, rowspan=20, column=1, sticky='ns')


    def load_tree(self):
        """ Delete existing records, then populate with new
            records.
        """
        # Delete current tree records
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Populate new tree records
        subjects = self.db.data['Subject Id']
        for subject in subjects:
            self.tree.insert('', tk.END, values=subject)


    #############
    # Functions #
    #############
    def plot_audio(self):
        """ Create figure axis for audiogram plot
        """
        figure = Figure(figsize=(5, 4), dpi=100)
        figure_canvas = FigureCanvasTkAgg(figure, self.frm_main)
        ax1 = figure.add_subplot()
        ax1.set_title("Audiogram")
        ax1.set_ylabel("Threshold (dB HL)")
        figure_canvas.get_tk_widget().grid(row=5, rowspan=20, column=15)
        return ax1


    def _item_selected(self, *args):
        """ Trigger event that tree item was selected """
        for selected_item in self.tree.selection():
            item = self.tree.item(selected_item)
            record = int(item['values'][0])

            # Update label textvariables with record data
            self.db.update_label_vars(self._vars, record)

            # Call audio display function
            self._show_audio(record)


    def _show_audio(self, record):
        """ Retrieve figure axis handle and plot audio 
        """
        ax1 = self.plot_audio()
        self.db.audio_ac(record, ax1)
