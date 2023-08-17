# **Subject Browser**

Graphical user interface (GUI) for filtering and browsing the participant database.

- Written by: **Travis M. Moore**
- Latest version: **Version 1.0.0**
- Created: **July 26, 2022**
- Last edited: **August 17, 2023**
<br>
<br>

---

## Description
This application was developed to provide an easy method for (1) filtering the Star database, (2) browsing the filtered selections, and (3) generating descriptive statistics and audiogram plots. 

1. The Subject Browser truncates the Star database to fields pertinent to recruiting, making the database easier to work with. Values are sorted alphanumerically, allowing for easy selection. Because values are stored locally, filtering is instantaneous. 

2. You can now see the most pertinent subject information all in one organized display, including the full graphical audiogram. Recommended acoustic coupling, vent sizes, and receiver gains are provided based on Pro Fit logic. Because values are stored locally, browsing is instantaneous.

3. After filtering or importing your participants, the Subject Browser can provide descriptive statistics (e.g., mean age, PTA), as well as individual and mean audiogram plots based on your selected participants. 
<br>
<br>

---

## Getting Started

### Dependencies

- Windows 10 or greater (not compatible with Mac OS)

### Installing

- This is a compiled app; the executable file is stored on Starfile at: starfile\Public\Temp\MooreT\Custom Software
- Simply copy the executable file and paste to a location on the local machine

### First Use
- Double-click to start the application for the first time
- Select a database .csv file using the **File** menu
- Use the dropdowns to enter your filtering criteria
- Click the FILTER RECORDS button on the Filter tab
- Browse filtered records using the Browse tab
<br>
<br>

---

# Downloading the Star Database
1. Log into the [Star database](http://ordsprd.starkey.com:8080/ords/glp/f?p=500:LOGIN:23703464524781:::::) and click the "General Search" tab.

    <img src="general_search.png" alt="General Search image" width="600"/>

1. Click the "Actions" button, then choose "Select Columns."

    <img src="actions_columns.png" alt="Select Columns image" width="600"/>

1. In the window that appears, click the double arrows (pointing right) button to move all the columns into the "Display in Report" list box. Then click "Apply."

    <img src="select_all_columns.png" alt="Select All Columns image" width="600"/>

1. Click the "Actions" button again, then choose "Download."

    <img src="actions_download.png" alt="Select Download image" width="600"/>

1. Click the "CSV" button in the window that appears and wait for the file to download. 

    <img src="choose_csv.png" alt="Choose .csv image" width="300"/>
<br>
<br>

---

# File Menu

## Importing Database Files
The Subject Browser can import full downloads from the Star database, as well as filtered database files exported from the Subject Browser. Because a lot of data are removed from the original download upon import, you will need to select the proper type of database from the ```File``` menu (i.e., Full DB or Filtered DB). 

### Full Database Imports
When importing the full database, you have the option to perform some default filtering to remove:

- Inactive participants
- Participants rated as "poor"
- Starkey employees

These filters are automatically applied if the "Initial Scrub" checkbox in the "Options" group (in the filter view) is selected. To avoid these filters, deselect the checkbox before importing the full database. 

<img src="filter_options.png" alt="Initial Scrub image" width="600"/>

### Filtered Database Imports
Filtered databases refer to databases previously exported from the Subject Browser, even if no filters were applied. Note that automatic filtering is not applied when importing filtered databases (i.e., previously exported databases).
<br>
<br>

---

## Exporting Database Files
The Subject Browser allows you to export filtered .csv database files for further work in Excel and for sharing with others. You can also import the exported files later for browsing and/or further filtering. 
<br>
<br>

---

## Exporting Filter Values
The Subject Browser allows you to export a list of your custom filters in .csv format for reuse. This is useful after manually setting several filter values that you might want to use again. The values are stored in a .csv file, which you can edit to add/remove or change filter values.

<img src="csv_filters.png" alt="Initial Scrub image" width="600"/>

<br>
<br>

---

## Importing Filter Values
The Subject Browser allows you to import a list of saved filter values to avoid entering filter values by hand, useful when using the same filter values across several recruiting sessions, or to make use of more filters than the number of filtering dropdowns on the interface.  

<img src="csv_filters.png" alt="Initial Scrub image" width="600"/>

Note: Imported filters are not displayed in the filter dropdowns in the filter view. You can still track filtering progress in the Filtering Results text area in the filter view, however. 
<br>
<br>

---

## Resetting the Filters
To clear all filter values, navigate to ```Tools>Reset Filters```.  
<br>
<br>

---

# Tools Menu

## Summary Statistics
The Subject Browser will provide descriptive statistics for the currently loaded group of participants by navigating to ```Tools>Summary Statistics```. 

<img src="summary_stats.png" alt="Initial Scrub image" width="300"/>

The frequencies used for PTA3 include: 500, 1000, and 2000 Hz.

The frequencies used for PTA4 include: 500, 1000, 2000, and 4000 Hz.
<br>
<br>

---

## Group Audiogram Plot
You can generate a plot showing each individual ear's thresholds, as well as the group mean thresholds by navigating to ```Tools>Group Audiogram```. The resulting plot show individual thresholds in grey (for each ear), with mean thresholds per ear in red and blue (right and left, respectively).

<img src="group_audiogram.png" alt="Initial Scrub image" width="500"/>
<br>
<br>

---

# Compiling from Source
Additional data:

- Add README folder
- Add sample_data.csv file

```
pyinstaller --noconfirm --onefile --windowed --add-data "C:/Users/MooTra/Code/Python/recruiting/assets/README;README/" --add-data "C:/Users/MooTra/Code/Python/recruiting/assets/sample_data.csv;."  "C:/Users/MooTra/Code/Python/recruiting/controller.py"
```
<br>
<br>

---

# Contact
Please use the contact information below to submit bug reports, feature requests and any other feedback. Thank you for using the Subject Browser!

- Travis M. Moore: travis_moore@starkey.com
