""" Main menu for Subject Browser
"""

# Import GUI packages
import tkinter as tk
from tkinter import messagebox

class MainMenu(tk.Menu):
    """ Main Menu
    """
    # Find parent window and tell it to 
    # generate a callback sequence
    def _event(self, sequence):
        def callback(*_):
            root = self.master.winfo_toplevel()
            root.event_generate(sequence)
        return callback


    def _bind_accelerators(self):
        self.bind_all('<Control-q>', self._event('<<FileQuit>>'))


    def __init__(self, parent, _app_info, **kwargs):
        super().__init__(parent, **kwargs)

        # Assign variables
        self._app_info = _app_info

        #############
        # File Menu #
        #############
        self.file_menu = tk.Menu(self, tearoff=False)
        self.file_menu.add_command(
            label="Import Full DB...",
            command=self._event('<<FileImportFullDB>>')
        )
        self.file_menu.add_command(
            label="Import Filtered DB...",
            command=self._event('<<FileImportFilteredDB>>')
        )
        self.file_menu.add_command(
            label="Export DB...",
            command=self._event('<<FileExportDB>>')
        )
        self.file_menu.add_separator()
        self.file_menu.add_command(
            label="Import Filter Values...",
            command=self._event('<<FileImportFilterVals>>')
        )
        self.file_menu.add_command(
            label="Export Filter Values...",
            command=self._event('<<FileExportFilterVals>>')
        )
        self.file_menu.add_separator()
        self.file_menu.add_command(
            label="Quit",
            command=self._event('<<FileQuit>>'),
            accelerator='Ctrl+Q'
        )
        self.add_cascade(label='File', menu=self.file_menu)


        ############## 
        # Tools menu #
        ##############
        tools_menu = tk.Menu(self, tearoff=False)
        tools_menu.add_command(
            label="Summary Statistics...",
            command=self._event('<<ToolsSummaryStats>>')
        )
        tools_menu.add_separator()
        tools_menu.add_command(
            label='Group Audiogram...',
            command=self._event('<<ToolsPlotGroupAudio>>')
        )
        tools_menu.add_command(
            label='Ear Specific Audiogram...',
            command=self._event('<<ToolsPlotEarSpecificGroupAudio>>')
        )
        tools_menu.add_separator()
        tools_menu.add_command(
            label='Reset Filters',
            command=self._event('<<ToolsReset>>')
        )
        # Add Tools menu to the menubar
        self.add_cascade(label="Tools", menu=tools_menu)


        #############
        # Help Menu #
        #############
        help_menu = tk.Menu(self, tearoff=False)
        help_menu.add_command(
            label='About...',
            command=self.show_about
        )
        help_menu.add_command(
            label='Help...',
            command=self._event('<<Help>>')
        )
        # Add help menu to the menubar
        self.add_cascade(label="Help", menu=help_menu)


        #####################
        # Bind accelerators #
        #####################
        self._bind_accelerators()


    ##################
    # Menu Functions #
    ##################
    # HELP menu
    def show_about(self):
        """ Show the about dialog """
        about_message = self._app_info['name']
        about_detail = (
            'Written by: Travis M. Moore\n' +
            'Version {}\n'.format(self._app_info['version']) +
            'Created: July 26, 2022\n'
            'Last edited: {}'.format(self._app_info['last_edited'])
        )
        messagebox.showinfo(
            title='About',
            message=about_message,
            detail=about_detail
        )
