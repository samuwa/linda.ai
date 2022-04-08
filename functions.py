import pandas as pd
from scipy import stats
import numpy as np
from itertools import combinations
from fuzzywuzzy import fuzz
import datetime



# 1.- create df from csv
def read_file(path):
    df = pd.read_csv(path, skipinitialspace=True)
    return df

# 2.- find duplicates
def find_duplicates(df, logger):
    dups = list(df[df.duplicated()].index)
    # Creating a dataframe with the condition of only rows duplicated
    # using the .index attribute to get the index object
    # convert to list to get a list of row numbers

    # Log dubs
    logger["duplicates"] = dups
    return

# 3.- Remove all duplicates
def remove_all_duplicates(df):
    df.drop_duplicates(inplace=True, ignore_index=True)

    return

# 4.- Remove specific row
def remove_row(df, row):
    df.drop(row, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return

def remove_no_reset(df,row):
    df.drop(row, inplace=True)
    return

# 5.- Convert column to numeric
def set_numeric(col):
    col = pd.to_numeric(col, errors="coerce")
    return

# 6.- Convert column to date
def set_date(col):
    # date_formates = ["21 June, 2018", "12/11/2018 09:15:32", "April-21" ]
    date_formats = ["%d %B, %Y", "%d/%m/%Y %H:%M:%S", "%B-%y", "%d %B, %Y", "%m/%d/Y"] # Can add different date formats to this list to test
    for x in date_formats:
        col = pd.to_datetime(col, errors="ignore", format= f"{x}")

    col = pd.to_datetime(col, errors="coerce") # To remove errors in the columns like strings or numbers
    return col

# 7.- Find missing values in
# Three returns:
    # [0] = Dict of columns with missing rows
    # [1] = all rows containing missing values
    # [2] = how many rows have missing values
def find_missing(df):
    missing = {}
    every = []
    for col in df.columns:
        missing[col] = df[df[col].isnull()].index.tolist()
        for x in missing[col]:
            every.append(x)

    return missing, set(every), len(set(every))

# 8.- Replace missing with column average
def missing_average(col):
    col.fillna(col.mean(), inplace=True)
    return

# 9.- Replace missing with 0
def missing_zeros(col):
    col.fillna(0, inplace=True)
    return

# 10.- sort values
'''
Use pandas sorting function
DataFrame.sort_values(by, axis=0, ascending=True, inplace=False, kind='quicksort', na_position='last', ignore_index=False, key=None)
'''

# 11.- find outliers
def find_outliers(df, col):
    colb = col.fillna(col.mean()) # Temporarily replace NaN with the column mean to prevent errors when calculating z-score
    alist = df[(np.abs(stats.zscore(colb))>3)].index.to_list()
    return alist

# 12.-  replace outliers with mean
def outliers_average(df, col, outliers): # This works because when sorting ignore_index = True
    for x in outliers:
        df.replace({col:{df.iloc[x][col]:df[col].mean()}}, inplace=True)
    return

# 13.- Replace outliers with zeros
def outliers_zeros(df, col, outliers): # This works because when sorting ignore_index = True
    for x in outliers:
        df.replace({col:{df.iloc[x][col]:0}}, inplace=True)
    return

# 14.- find string combinations
def get_combinations(col):
    uniques = list(set(col))
    uniques = [x for x in uniques if str(x) != 'nan']
    combs = combinations(uniques, 2)
    return list(combs)

# 15.- find fuzzy matches in combinations
def find_matches(alist):
    finds = []
    for comb in alist:
        aratio = fuzz.ratio(comb[0].lower(), comb[1].lower())
        part_ratio = fuzz.partial_ratio(comb[0].lower(), comb[1].lower())

        if aratio > 80 or part_ratio > 70:
            finds.append(comb)
    return finds

def df_to_csv(df):
    csv = df.to_csv(index=False).encode('utf-8')
    return csv
