# Molecular Similarity Survey
This repository contains all files necessary to deploy the 'Molecular Similarity Survey' web app on Heroku.

## Create GIT Repository
```bash
git init
git add --all
git commit 'Start repository'
```

## Create Heroku App
```bash
heroku create molecular-similarity-survey --region eu
git push heroku master
```
Then, create a Postgres database for the app,
and initiate all necessary tables:
```bash
heroku addons:create heroku-postgresql:<PLAN_NAME>
python initiate_database.py --where heroku
```
`<PLAN_NAME>` is the name of the Heroku price tier; `hobby-dev` is the free tier.
Use `heroku open` to open the web app.

Use `python retrieve_user_data.py --where heroku` to execute some important queries
on the Heroku database, and save the results locally as CSV files.

When you wish to close the survey web app, use `heroku apps:delete`.


## Use App Locally
```bash
conda create -n survey -c conda-forge --file requirements.txt
conda activate survey
voila survey.ipynb
```
