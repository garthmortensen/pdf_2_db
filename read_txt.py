# -*- coding: utf-8 -*-
"""
Created on Sun Jun 19 06:33:08 2022

@author: morte

#####  #####  ######    #    # # #    # ###### #####
#    # #    # #         ##  ## # ##   # #      #    #
#    # #    # #####     # ## # # # #  # #####  #    #
#####  #    # #         #    # # #  # # #      #####
#      #    # #         #    # # #   ## #      #   #
#      #####  #         #    # # #    # ###### #    #
"""

from pathlib import Path
import os
import pandas as pd
from datetime import datetime  # timestamp column for archiving

# text cleaning
import string  # for punctuation list
import re  # regex for text cleaning

import sqlite3
import uuid

# read relative paths
dir_py = os.path.dirname(__file__)
path_in = os.path.join(dir_py, "data", "in")
path_out = os.path.join(dir_py, "data", "out")

# populate empty df using dict, which is refreshed in each loop
columns = [
           "id",
           "load_date",
           "filepath",
           "filename",
           "kb",
           "content",
           ]

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

    kb = round(os.path.getsize(os.path.join(path_in, filename)) / 1024, 1)

    with open(os.path.join(path_in, filename), 'r', encoding='utf8') as f:
        content = f.read()  # readlines() for list

        content = string_cleaning(content)

        # populate dict and append it to df as new_row
        new_row["id"] = str(uuid.uuid4())
        new_row["load_date"] = datetime.today().strftime('%Y-%m-%d')
        new_row["filepath"] = path_in
        new_row["filename"] = filename
        new_row["kb"] = str(kb)  # otherwise wont insert
        new_row["content"] = content
        df = df.append(new_row, ignore_index=True)

# %%

# create db

# https://www.sqlitetutorial.net/sqlite-python/creating-database/
# Create a shared named in-memory database.
# conn = sqlite3.connect("file:mem1?mode=memory&cache=shared", uri=True)  # for in memory db
db_name = "pythonsqlite"
conn = sqlite3.connect(os.path.join(path_out, db_name + ".db"))

cursor = conn.cursor()

# %%

tablename_content = "pdf_content"
tablename_keywords = "pdf_keywords"
cursor.executescript(
    f"""
    drop table if exists {tablename_content};
    create table if not exists {tablename_content} (
      id            varchar(256)
    , load_date     varchar(256)
    , filepath      varchar(256)
    , filename      varchar(256)
    , kb            varchar(256)
    , content       blob
    );
    """
    )

df_content = pd.read_sql(f"select * from {tablename_content}", con=conn)

# %%

# insert file content into table
df_tuples = df.to_records(index=False)  # sqlite requires tuples
query_insert = \
    f"""insert into {tablename_content} ({', '.join(columns)})
    values(?, ?, ?, ?, ?, ?)
    """  # insert into tablexyz (field1, field2) values(?, ?)
cursor.executemany(query_insert, df_tuples)

df_content = pd.read_sql(f"select * from {tablename_content}", con=conn)

# %%

# quick keyword search in sql to complete exercise
cursor.executescript(
    f"""
    drop table if exists {tablename_keywords};
    create table if not exists {tablename_keywords} as
    select
          id
        , case when content like ('% alaska %') then 1 else 0 end has_alaska
        , case when content like ('% saturday %') then 1 else 0 end has_saturday
        , case when content like ('% house %') then 1 else 0 end has_house
    from {tablename_content}
    ;
    """
    )

df_keywords = pd.read_sql(f"select * from {tablename_keywords}", con=conn)

conn.commit()
conn.close()
