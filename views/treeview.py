import tkinter as tk
from tkinter import ttk


class SubjectTree(tk.Frame):
    """ Treeview for database subjects """
    def __init__(self, parent, db, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        style = ttk.Style()
        style.configure("new.Treeview", highlightthickness=5, bd=4)
        style.configure("new.Treeview.Heading", font=('TkDefaultFont', 10, 'bold'))
        style.configure("new.Vertical.TScrollbar")

        # Initialize
        self.db = db
        self.rowconfigure(0, weight=1)

        self._load_tree()


    def _load_tree(self):
        """ Create tree widget from database
        """
        # Get subs from dataframe
        subjects = self.db.data['Subject Id']
        columns = ('subject_id')
        self.tree = ttk.Treeview(self, columns=columns, show='headings', height=20, style='new.Treeview')
        self.tree.column("# 1", width=100, anchor=tk.CENTER)
        self.tree.heading('subject_id', text='Subject ID')
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.tree.bind('<<TreeviewSelect>>', self._item_selected)

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview, style='new.Vertical.TScrollbar')
        self.tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.grid(row=0, rowspan=10, column=1, sticky='ns')

        # Add subjects to tree
        for subject in subjects:
            self.tree.insert('', tk.END, values=subject)


    def _item_selected(self, *args):
        """ Trigger event that tree item was selected """
        self.event_generate('<<TreeviewSelect>>')
