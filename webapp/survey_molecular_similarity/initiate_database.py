#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Created on Thu Apr  1 12:47:37 2021
# Copyright © Enrico Gandini <enricogandini93@gmail.com>
#
# Distributed under terms of the MIT License.

"""Initiate database that will be used to store answers of
'Molecular Similarity Survey' web app:
create all necessary tables,
and populate table containing all possible molecular pairs.
"""
import argparse
from os import environ
from pathlib import Path
import subprocess


import pandas as pd

from database_utils import Base, MolecularPair
from database_utils import create_db_engine_and_session


parser = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 )
parser.add_argument("--where",
                    action="store",
                    choices=["local", "heroku"],
                    help=("Whether to initiate tables on a local database"
                          " or an existing Postgres database on Heroku"),
                    required=True,
                    )
args = parser.parse_args()
location_db = args.where

db_objects = {}

#Get Database URL
if location_db == "local":
    db_objects["url"] = environ.get("DATABASE_URL") #Use local Database

elif location_db == "heroku":
    process_get_db_url = subprocess.run("heroku config:get DATABASE_URL",
                                        capture_output=True,
                                        shell=True,
                                        )
    db_objects["url"] = process_get_db_url.stdout.decode()
    
    #SQLAlchemy >= 1.4 has changed Postgres URL,
    #but Heroku still has old style Postgres URL.
    db_objects["url"] = db_objects["url"].replace("postgres:", "postgresql:")

else:
    pass


#Connect to database
create_db_engine_and_session(db_objects)

#Add all tables defined in `database_utils.py`.
Base.metadata.create_all(db_objects["engine"])


#Load DataFrame containing all molecular pairs
#that were manually chosen for the survey.
file_chosen = Path("manuallyChosen_similarity_divergence_interesting_targets_compounds.csv")
df_chosen = pd.read_csv(file_chosen,
                        index_col="id_chosenPair",
                        )

#Add all molecular pairs to database table.
pairs = [MolecularPair(id=id_pair) for id_pair in df_chosen.index]
db_objects["session"].add_all(pairs)


#Close database connection.
db_objects["session"].commit()
db_objects["engine"].dispose()