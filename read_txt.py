from pathlib import Path
import os
import pandas as pd

from datetime import datetime  # timestamp column for archival purposes

# text cleaning
import string  # for punctuation list
import re  # regex for text cleaning

dir_py = os.path.dirname(__file__)
path_in = os.path.join(dir_py, "data", "in")
path_out = os.path.join(dir_py, "data", "out")

run_date = datetime.today().strftime('%Y-%m-%d')
# run_date = "'" + run_date + "'"  # without ' it does the math of 2021 - 07

# populate empty df using dict, which is refreshed in each loop
columns = ["filepath", "filename", "content", "run_date"]
df = pd.DataFrame(columns=columns)
one_row = dict.fromkeys(columns)

def string_cleaning(content):
    """Clean and reformat a string. Perhaps turn each one of these into methods"""

    content = content.lower()

    re_punc = re.compile("[^a-z ]")  # keep only lowercase alpha and spaces
    # replace stripped out chars with space
    content = re_punc.sub(" ", content)

    # remove redundent spaces
    content = re.sub("\s\s+" , " ", content)

    return content

i = 0
# loop through all files, create new row for each file
for filename in os.listdir(path_in):
    i += 1
    print(f"Reading {filename}, file #{i}")

    with open(os.path.join(path_in, filename), 'r', encoding='utf8') as f:
        content = f.read()  # readlines() for list

        content = string_cleaning(content)

        # populate dict and append row to df
        one_row["filepath"] = path_in
        one_row["filename"] = filename
        one_row["content"] = content
        one_row["run_date"] = run_date
        df = df.append(one_row, ignore_index=True)

# %%

# create db
import sqlite3

# https://www.sqlitetutorial.net/sqlite-python/creating-database/
def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = sqlite3.connect(db_file)  # :memory:
    print(sqlite3.version)
    conn.close()

db_name = "pythonsqlite"
create_connection(os.path.join(path_out, db_name + ".db"))

# %%

# create table
from sqlalchemy import create_engine

connection_string = "sqlite:///{db_name} + .db"
engine = create_engine(connection_string, echo=True)
conn = engine.connect()

tablename = "all_content"
query_create = \
    f"""
    create table if not exists {tablename} (
    filepath        varchar(256)
    , filename      varchar(256)
    , content       varchar(256)
    , run_date      varchar(256)
    )
    ;
    """
engine.execute(query_create)

query_select = f"select * from {tablename}"
df2 = pd.read_sql(query_select, con=engine)

# %%

# load into table
conn = sqlite3.connect(os.path.join(path_out, db_name + ".db"))
cursor = conn.cursor()


df_tuples = df.to_records(index=False)
query_insert = \
    f"""insert into {tablename} (filepath, filename, content, run_date)
    values(?, ?, ?, ?)
    """
cursor.executemany(query_insert, df_tuples)
conn.commit()
if(conn):
  conn.close()
  print("\nThe SQLite connection is closed.")

# OperationalError: no such table: all_content
# am i creating 2 different dbs???
