#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Created on Fri Mar 26 16:35:26 2021
# Copyright © Enrico Gandini <enricogandini93@gmail.com>
#
# Distributed under terms of the MIT License.

"""Retrieve data from database, and save it as CSV files
that can be further analyzed.

Files will be saved in a separate directory each day this script is executed.
So, various versions of the same queries will be present on the disk, and you
can monitor the progress of the survey.
"""

import argparse
import datetime
from os import environ
from pathlib import Path
import subprocess

import pandas as pd
from sqlalchemy import func, case, cast, Integer

from database_utils import MolecularPair, User, Answer
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


create_db_engine_and_session(db_objects)
session = db_objects["session"]


dir_results = Path("../results_survey_molecular_similarity")
today = datetime.date.today()
dir_today = Path(dir_results,
                 f"queried_{location_db}_{today.isoformat()}"
                 )
dir_today.mkdir(parents=True, exist_ok=True)
print(f"Saving results to: `{dir_today.as_posix()}`")


#Query the database and insert results in DataFrames.
#See this:
#https://stackoverflow.com/questions/29525808/sqlalchemy-orm-conversion-to-pandas-dataframe
#for help on `pd.read_sql` usage with SQLAlchemy.


#All Users.
query_all_users = session.query(User)
df_all_users = pd.read_sql(query_all_users.statement,
                           session.bind,
                           index_col="id",
                           )
df_all_users.to_csv(Path(dir_today, "all_users.csv"))

#All Answers.
query_all_answers = session.query(Answer)
df_all_answers = pd.read_sql(query_all_answers.statement,
                             session.bind,
                             index_col="id",
                             )
df_all_answers.to_csv(Path(dir_today, "all_answers.csv"))


#Define a time interval: only answers in the time interval will be considered
#for further analysis.
start_date = datetime.date(year=2021,
                           month=4,
                           day=14,
                           )
query_time_interval = (session
                       .query(User.id)
                       .filter(User.date >= start_date)
                       )
#Save information about used time interval.
file_ti = Path(dir_today, "used_time_interval.txt")
with open(file_ti, "w") as f:
    print(f"Start Date: {start_date}", file=f)


#All Users (in time interval).
query_ti_users = (query_all_users
                  .filter(User.id.in_(query_time_interval))
                  )
df_ti_users = pd.read_sql(query_ti_users.statement,
                          session.bind,
                          index_col="id",
                          )
df_ti_users.to_csv(Path(dir_today, "time_interval_users.csv"))

#All Answers (in time interval).
query_ti_answers = (query_all_answers
                    .filter(Answer.id_user.in_(query_time_interval))
                    )
df_ti_answers = pd.read_sql(query_ti_answers.statement,
                            session.bind,
                            index_col="id",
                            )
df_ti_answers.to_csv(Path(dir_today, "time_interval_answers.csv"))


#Calculate aggregated properties.
count_answers = func.count(Answer.id)


#Get number of answers that each molecular pair received during the course
#of the whole survey, and fraction of "Yes" answers for each molecular pair.
similar_to_1 = case([(Answer.similar == "Yes", 1.0),
                     (Answer.similar == "No", 0.0),
                     ])
sum_similar = func.sum(similar_to_1)
frac_similar = sum_similar / count_answers

query_agg = (session
             .query(MolecularPair.id,
                    count_answers.label("n_answers"),
                    cast(sum_similar, Integer).label("n_similar"),
                    frac_similar.label("frac_similar"),
                    )
             .outerjoin(Answer)
             .filter(Answer.id_user.in_(query_time_interval))
             .group_by(MolecularPair.id)
             )
df_agg = pd.read_sql(query_agg.statement,
                     session.bind,
                     index_col="id",
                     )


#Close connection to Database.
db_objects["engine"].dispose()


#Read DataFrame of manually chosen pairs
basename_files_divergence = "similarity_divergence_interesting_targets_compounds"
file_chosen = Path(f"manuallyChosen_{basename_files_divergence}.csv")
df_chosen = pd.read_csv(file_chosen,
                        index_col="id_chosenPair",
                        )

#Merge DataFrame of manually chosen pairs with DataFrame
#of aggregated answers.
df_merged = pd.merge(left=df_chosen,
                     right=df_agg,
                     how="left",
                     left_index=True,
                     right_index=True,
                     )
df_merged.to_csv(Path(dir_today, "aggregated_survey_answers.csv"))
