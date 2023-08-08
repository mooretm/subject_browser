import sqlite3
import pandas as pd

# Connect to SQLite database
conn = sqlite3.connect(r'C:\Users\MooTra\OneDrive - Starkey\Desktop\Subjects.db')

# Load CSV data into Pandas DataFrame
# Expects a FULL database exported from Subject Browser
sub_data = pd.read_csv(r'C:\Users\MooTra\OneDrive - Starkey\Desktop\Full Clean.csv')

# Replace spaces in column names with underscores
new_names = []
for col in sub_data.columns:
    new_names.append('_'.join(col.split()))
sub_data.columns = new_names

# Replace '-' with Python None
sub_data = sub_data.replace('-', None)
#sub_data.iloc[:,8].astype('float')

# Write the data to a sqlite table
try:
    sub_data.to_sql('subjects', conn, if_exists='fail', index=False)
except ValueError as e:
    print(e)
    print("Table already exists!")

# Create a cursor object
cur = conn.cursor()
# Fetch and display result
for row in cur.execute('SELECT * FROM subjects'):
    print(row)
# Close connection to SQLite database
conn.close()
