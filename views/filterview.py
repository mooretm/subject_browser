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

    def __init__(self, parent, database, filter_dict, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        ##############
        # Initialize #
        ##############
        # Assign constructor arguments to class variables
        self.filter_dict = filter_dict
        self.db = database

        # Create list of database columns
        self.attributes = list(self.db.data.columns)
        self.attributes.sort()

        # Create list of operators
        self.operators = ["equals", "does not equal", "contains", ">", ">=", 
            "<", "<="]

        self._draw_widgets()


    def _draw_widgets(self):
        #################
        # Create Frames #
        #################
        # Allow expansion of main frame
        self.columnconfigure(index=0, weight=1)
        
        # Custom widget styles
        style = ttk.Style()
        style.configure("rec.TLabel", foreground='green')


        #################
        # Create Frames #
        #################
        # Frame options
        options = {'padx':10, 'pady':10}

        # Main frame
        frm_filter = ttk.Frame(self)
        frm_filter.grid(row=0, column=0, sticky='nsew')
        # Set columns to expand
        frm_filter.columnconfigure(index=1, weight=1)
        frm_filter.columnconfigure(index=2, weight=1)
        frm_filter.columnconfigure(index=3, weight=1)

        # Options frame
        frm_options = ttk.LabelFrame(frm_filter, text="Options")
        frm_options.grid(row=2, column=1, padx=10, pady=(10,0),
            sticky='nsew')
        # Set columns to expand
        frm_options.columnconfigure(index=1, weight=1)
        
        # Output textbox frame
        frm_output = ttk.Frame(self)
        frm_output.grid(row=21, column=0, **options, 
            sticky='nsew')
        # Set columns to expand
        frm_output.columnconfigure(index=1, weight=1)


        ############
        # Controls #
        ############
        # Initial scrub checkbutton
        self.scrub_var = tk.IntVar(value=0)
        ttk.Checkbutton(frm_options, text="Initial Scrub",
            takefocus=0, variable=self.scrub_var).grid(
                row=0, column=0, sticky='w', padx=5, pady=5)

        # Filter box labels
        label_text = ['Attribute', 'Operator', 'Value']
        for idx, label in enumerate(label_text, start=1):
            ttk.Label(frm_filter, text=label).grid(
                row=5, column=idx, pady=10, sticky='n')

        # Filter button
        ttk.Button(frm_filter, text="Filter Records", 
            command=self._on_filter).grid(row=20, column=2, sticky='ew')

        # Text widget for displaying filtering results
        self.txt_output = tk.Text(frm_output, height=10)
        self.txt_output.grid(row=1, column=1, sticky='nsew')

        # Scrollbar for text widget
        scroll = ttk.Scrollbar(frm_output, orient='vertical', 
            command=self.txt_output.yview)
        scroll.grid(row=1, column=2, sticky='ns')

        self.txt_output['yscrollcommand'] = scroll.set


        ###############################
        # Create Filtering Comboboxes #
        ###############################
        # Specify number of filter rows
        num_fields = 6

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
    def clear_output(self):
        self.txt_output.delete('1.0', tk.END)


    def _clear_filters(self):
        """ Clear all values from the filter comboboxes.
            Reset filter dict to empty.
        """
        # Clear out current filter dict
        self.filter_dict = {}

        # Delete any output from textbox
        self.clear_output()

        # Clear all combobox values
        for ii in range(0, len(self.attrib_cbs)):
            self.attrib_cbs[ii].set('')
            self.op_cbs[ii].set('')
            self.value_cbs[ii].set('')

        # Set the focus to the upper left combobox
        self.attrib_cbs[0].focus_set()


    # def _load_filters(self, filter_dict):
    #     """ Populate comboboxes with values from provided dict.
            
    #         Retired function - no longer called. 
    #     """
    #     # Clear any textbox output
    #     self.txt_output.delete('1.0', tk.END)

    #     # Populate comboxes with new values
    #     try:
    #         for ii in filter_dict:
    #             self.attrib_cbs[int(ii)].set(filter_dict[ii][0])
    #             self.op_cbs[int(ii)].set(filter_dict[ii][1])
    #             self.value_cbs[int(ii)].set(filter_dict[ii][2])
    #     except IndexError:
    #         messagebox.showinfo(title="So Many Filters",
    #             message="The number of imported filters exceeds the " +
    #                 "number of filter dropdowns!",
    #             detail="All filters will still be applied, but they " +
    #                 "will not be displayed.")
    #         raise IndexError


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
        # Get values from all comboboxes
        self._make_filter_dict()

        # Send event to controller to filter
        self.event_generate('<<FilterviewFilter>>')


    def _make_filter_dict(self):
        """ Create a dictionary of filter values from combobox values. 
            Check for missing values and skipped rows.
        """
        all_data = []
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
                # Create list from values if 'contains' operator
                # Create new 'value' variable because tk.StringVar
                # cannot hold a list
                if self.op_vars[ii].get() == "contains":
                    value = self.value_vars[ii].get().split()
                    # Convert each list element to float, if possible
                    try:
                        value = [float(x) for x in value]
                    except ValueError:
                        # Cannot convert string to float
                        pass
                else:
                    value = self.value_vars[ii].get()
                    # Convert value to float, if possible
                    try:
                        value = float(value)
                    except ValueError:
                        # Cannot convert string to float
                        pass

                # If all values are present in a given row, append to list
                all_data.append(
                    (
                    self.attrib_vars[ii].get(), 
                    self.op_vars[ii].get(), 
                    value
                    )
                )
                try:
                    # Update dictionary with list by index
                    self.filter_dict[ii] = all_data[ii]
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
