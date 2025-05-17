import pandas as pd
import os
from sklearn.preprocessing import StandardScaler

def load_df(current_dir):
    """This function loads the data from the according path into a pandas dataframe."""

    # construct path to the project data folder
    data_dir = os.path.join(current_dir, '..', '..', 'Data', 'Sonar_Measures')
    # load SonarQube measure data of version 1 and 2, cleaned
    df = pd.read_csv(os.path.join(data_dir, 'sonar_measures_v1_v2_no_statics.csv'), low_memory=False)
    return df

def put_label_in_front(df, label):
    """This function puts the label variable into the first column."""
    cols = df.columns.tolist()
    cols.remove(label)
    cols.insert(0, label)
    df = df[cols]
    return df

def select_variables(df, variable_list):
    """This function returns a smaller df that only contains a subset of variables contained in variable_list."""
    df = df[variable_list]
    return df

def scale_predictors(df, label):
    """This function scales numerical predictor variables. The label remains unscaled."""
    columns_to_scale = [col for col in df.select_dtypes(include=['number']) if col != label]
    scaler = StandardScaler()
    df[columns_to_scale] = scaler.fit_transform(df[columns_to_scale])
    return df