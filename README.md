# Repository of the Similarity Prediction paper

## Contents
* `datasets`: the data-sets used to train the similarity-prediction models described in the paper.
    * `original_training_set`: contains the [original training-set](https://jcheminf.biomedcentral.com/articles/10.1186/1758-2946-6-5) by Franco *et al.* used in the paper. The SMILES included in the CSV file are preprocessed and curated with the open source 2D protocol described in the paper. The directory also contains the 2D graph representations of all the molecules, and the aligned 3D conformers obtained with the 3D OpenEye protocol.
    * `new_dataset`: contains the new data-set created in the research project and described in the paper. The SMILES included in the CSV file are the ones from the open source 2D protocol. The 3D conformers are generated and aligned with the 3D OpenEye protocol.
* `webapp`: the source code for the web-app used to erogate the molecular similarity survey.
    * `survey_molecular_similarity`: all the code, instructions, and data necessary to erogate the app on Heroku. The `retrieve_user_data.py` script was used to extract the data from the Heroku PostgreSQL database.
    * `results_survey_molecular_similarity`: survey answers obtained from the database and retrieved with the aforementioned script.
