""" Filter view for Subject Browser 
"""

###########
# Imports #
###########
# Import GUI packages
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# Import misc packages
import uuid


#########
# BEGIN #
#########
class FilterView(ttk.Frame):
    """ Filter view for 'Filter' tab of notebook
    """

    def __init__(self, parent, database, sessionpars, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        ##############
        # Initialize #
        ##############
        # Assign constructor arguments to class variables
        self.db = database
        self.sessionpars = sessionpars

        self.sessionpars['initial_scrub'].trace_add('write', self._save_scrub_state)

        # Create list of database columns
        self.attributes = list(self.db.data.columns)
        self.attributes.sort()

        # Create list of operators
        self.operators = ["equals", "does not equal", "contains", "not in", 
                          ">", ">=", "<", "<="]

        self._draw_widgets()


    def _draw_widgets(self):
        #################
        # Create Frames #
        #################
        # Custom widget styles
        style = ttk.Style()
        style.configure("rec.TLabel", foreground='green')


        #################
        # Create Frames #
        #################
        # Main frame
        frm_filter = ttk.Frame(self)
        frm_filter.pack(fill="both", expand=True, side="left")
        #frm_filter.grid(row=0, column=0, sticky='nsew')
        # Set columns to expand
        #frm_filter.columnconfigure(index=1, weight=1)
        #frm_filter.columnconfigure(index=2, weight=1)
        #frm_filter.columnconfigure(index=3, weight=1)

        # Options frame
        frm_options = ttk.LabelFrame(frm_filter, text="Options")
        frm_options.grid(row=2, column=1, padx=10, pady=(10,0),
           sticky='nsew')
        # Set columns to expand
        #frm_options.columnconfigure(index=1, weight=1)
        
        # Output textbox frame
        frm_output = ttk.Frame(self)
        frm_output.pack(fill="both", expand=True, side="right", pady=10, padx=(0,10))
        # frm_output.grid(row=21, column=0, **options, 
        #     sticky='nsew')
        # # Set columns to expand
        # frm_output.columnconfigure(index=1, weight=1)


        ############
        # Controls #
        ############
        # Initial scrub checkbutton
        ttk.Checkbutton(frm_options, text="Initial Scrub",
            takefocus=0, variable=self.sessionpars['initial_scrub']).grid(
                row=0, column=0, sticky='w', padx=5, pady=5)

        # Filter box labels
        label_text = ['Attribute', 'Operator', 'Value']
        for idx, label in enumerate(label_text, start=1):
            ttk.Label(frm_filter, text=label).grid(
                row=5, column=idx, pady=10, sticky='n')

        # Filter button
        ttk.Button(frm_filter, text="Filter Records", 
            command=self._on_filter).grid(row=20, column=2, sticky='ew', 
                                          pady=20)

        # Text widget for displaying filtering results
        ttk.Label(frm_output, text='Filtering Results').pack()
        self.txt_output = tk.Text(frm_output, width=50)
        self.txt_output.pack(side='left', fill="both", anchor="w", 
                             expand=True)

        # Scrollbar for text widget
        scroll = ttk.Scrollbar(frm_output, orient='vertical', 
            command=self.txt_output.yview)
        scroll.pack(side='right', anchor="e", fill='y')
        #scroll.grid(row=1, column=2, sticky='ns')
        self.txt_output['yscrollcommand'] = scroll.set


        ###############################
        # Create Filtering Comboboxes #
        ###############################
        # Specify number of filter rows
        num_fields = 9

        # Attribute combobox
        self.attrib_vars = []
        self.attrib_cbs = []

        # Operator combobox
        self.op_vars = []
        self.op_cbs = []

        # Value combobox
        self.value_vars = []
        self.value_cbs = []

        # Create all comboboxes
        for ii in range(0, num_fields):
            # Database attribute comboboxes
            # Append next unique ID to list
            self.attrib_vars.append(uuid.uuid4())
            # Assign unique ID to string variable
            self.attrib_vars[ii] = tk.StringVar()
            # Create combobox with above variable
            cb_attrib = ttk.Combobox(frm_filter, 
                textvariable=self.attrib_vars[ii], takefocus=0)
            # Show combobox
            cb_attrib.grid(row=6+ii, column=1, pady=(0,10), padx=10,
                sticky='nsew')
            # Populate combobox
            cb_attrib['values'] = self.attributes
            # Append combobox to list
            self.attrib_cbs.append(cb_attrib)

            # Operator comboboxes:
            # Append next unique ID to list
            self.op_vars.append(uuid.uuid4())
            # Assign unique ID to string variable
            self.op_vars[ii] = tk.StringVar()
            # Create combobox with above variable
            cb_op = ttk.Combobox(frm_filter, 
                textvariable=self.op_vars[ii], takefocus=0)
            # Show combobox
            cb_op.grid(row=6+ii, column=2, pady=(0,10), sticky='nsew')
            # Populate combobox
            cb_op['values'] = self.operators
            # Append combobox to list
            self.op_cbs.append(cb_op)

            # Database value comboboxes:
            # Append next unique ID to list
            self.value_vars.append(uuid.uuid4())
            # Assign unique ID to string variable
            self.value_vars[ii] = tk.StringVar()
            # Create combobox with above variable
            cb_value = ttk.Combobox(frm_filter, 
                textvariable=self.value_vars[ii],
                postcommand=self._get_values, takefocus=0)
            # Show combobox
            cb_value.grid(row=6+ii, column=3, pady=(0,10), padx=10,
                sticky='nsew')
            # Append combobox to list
            self.value_cbs.append(cb_value)


    #####################
    # General Functions #
    #####################
    def _save_scrub_state(self, var, index, mode):
        """ Send event to controller that initial scrub 
            checkbox was toggled.
        """
        self.event_generate('<<FilterviewScrubToggled>>')


    def clear_output(self):
        """ Clear any existing text from the filter display 
            textbox.
        """
        self.txt_output.delete('1.0', tk.END)


    def clear_filters(self):
        """ Clear all values from the filter comboboxes.
        """
        # Delete any output from textbox
        self.clear_output()

        # Clear all combobox values
        for ii in range(0, len(self.attrib_cbs)):
            self.attrib_cbs[ii].set('')
            self.op_cbs[ii].set('')
            self.value_cbs[ii].set('')

        # Set the focus to the upper left combobox
        self.attrib_cbs[0].focus_set()


    ##############################
    # Filter Selection Functions #
    ##############################
    def _get_values(self, *_):
        """ Get values to populate value comboboxes based on the selected 
            attribute in the attribute comboboxes
        """
        # Loop through number of comboboxes set in num_fields above
        for ii in range(0, len(self.attrib_cbs)):
            # If the user did not specify any values in a combobox, skip it
            if len(self.attrib_cbs[ii].get()) != 0:
                # Drop "NaN" from df and grab unique values as list
                unique_vals = list(
                    self.db.data[self.attrib_cbs[ii].get()].dropna().unique()
                    )
                # Remove non-data fields
                if '-' in unique_vals:
                    unique_vals.remove('-')

                # Sort the unique data values
                unique_vals.sort()

                # Assign the unique values to the Values combobox
                self.value_cbs[ii]['values'] = unique_vals
                #print(f"\nfilterview: Added {self.attrib_cbs[ii].get()} to value combobox")


    ###################################
    # Filter Implementation Functions #
    ###################################
    def _on_filter(self):
        """ Update filter dict based on provided combobox values.
            Send filter event to controller.
        """
        # Send event to controller
        self.event_generate('<<FilterviewFilter>>')


    def _make_filter_dict(self):
        """ Create a dictionary of filter values from combobox values. 
            Check for missing values and skipped rows.
        """
        all_data = []
        filter_dict = {}
        self.clear_output()

        for ii in range(0, len(self.attrib_cbs)):
            # Check for any empty values in a given row
            if (not self.attrib_vars[ii].get()) \
                or (not self.op_vars[ii].get()) \
                or (not self.value_vars[ii].get()):
                # Check whether entire row is empty
                if (not self.attrib_vars[ii].get()) \
                    and (not self.op_vars[ii].get()) \
                    and (not self.value_vars[ii].get()):
                    pass # do nothing if entire row is empty
                else:
                    # If some values in a row are missing, 
                    # display message and exit
                    print("Missing values!")
                    messagebox.showerror(title="Missing Values",
                        message="There are missing values!",
                        detail="Please provide all filter parameters " +
                            "for a given row."
                    )
                    return
            else:
                # If all values are present in a given row, append to list
                all_data.append(
                    [
                    self.attrib_vars[ii].get(), 
                    self.op_vars[ii].get(), 
                    self.value_vars[ii].get()
                    ]
                )
                try:
                    # Update dictionary with list by index
                    filter_dict[ii] = all_data[ii]
                except IndexError:
                    # If indexes do not match, there was an empty row 
                    # between rows with values: display message and 
                    # exit
                    messagebox.showerror(title="Empty Rows",
                        message="One or more rows has been skipped!",
                        detail="There cannot be empty rows between rows " +
                            "with values."
                    )
                    return
        return filter_dict
