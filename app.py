import functions as fs
import streamlit as st
import pandas as pd
import datetime
import scipy
import itertools
import fuzzywuzzy


# Variables
    #-- Main variables --#

if 'diagnosis' not in st.session_state:
    st.session_state["diagnosis"] = {}
if 'method_selection' not in st.session_state:
    st.session_state["method_selection"] = {}
if "action_taken" not in st.session_state:
    st.session_state["action_taken"] = []  # List of string statements

if "report" not in st.session_state:
    st.session_state["report"] = {}

if "helper" not in st.session_state:
    st.session_state["helper"] = {}

data_types = ["Text", "Number", "Date"]
method_options = ["Keep All", "Remove All", "Inspect"]
method_numeric_options = ["Keep All", "Remove All", "Replace with Column Average", "Replace with Zeros"]
omit_options = ["Omit", "Inspect"]
numeric_range = ["Keep All", "Greater Than", "Less Than", "Equal To"]
    #--------------------#

# Get file
if "file" not in st.session_state:
    st.session_state["file"] = None
# Dataframe
if "df" not in st.session_state:
    st.session_state["df"] = None

if "clean" not in st.session_state:
    st.session_state["clean"] = None

# Containers
# Header
header = st.container()
with header:
    st.title("Linda.ai")
    st.write("Your virtual data team")

# File input
file_input = st.container()
with file_input:
    st.session_state.file = st.file_uploader("Upload CSV") # Create upload file widget
    try:
        st.session_state.df = fs.read_file(st.session_state.file) # turn file into df
        #st.write(st.session_state.df.head()) # display df.head() if there is a file uploaded
        # RUN DIAGNOSIS #
        fs.find_duplicates(st.session_state.df, st.session_state.diagnosis)

    except ValueError:
        pass

if st.session_state.file == None:
    pass
else:
    # Df head
    st.dataframe(st.session_state.df.head())



    # Duplicates
    duplicates = st.container()
    with duplicates:
        st.subheader("Duplicated Rows")
        # if there are no duplicates, show there are no duplicates
        if st.session_state.diagnosis["duplicates"] == []:
            st.write("There are no duplicated rows")
        else:
            st.session_state.method_selection["duplicates"] = st.selectbox(
                f"The data has {len(st.session_state.diagnosis['duplicates'])} duplicated rows",
                method_options)

            # If selected method == Remove all - remove all duplicates
            if st.session_state.method_selection["duplicates"] == method_options[1]:
                fs.remove_all_duplicates(st.session_state.df)

            # If == Inspect - show each duplicated row and offer keep/drop
            elif st.session_state.method_selection["duplicates"] == method_options[2]:
                for row in st.session_state.diagnosis["duplicates"]:
                    remove = st.checkbox(f"Remove row {row}", key=row)
                    st.write(st.session_state.df.loc[[row]])
                    if remove == True:
                        fs.remove_no_reset(st.session_state.df, row) # Wait for all inspection before resetting
                st.session_state.df.reset_index(drop=True, inplace=True)


        #st.write(st.session_state.df.index)

    column_selection = st.container()
    with column_selection: # Select columns to keep
        st.subheader("Select columns")
        st.session_state.method_selection["selection"] = st.multiselect(
            label="Select columns to keep",
            options=st.session_state.df.columns,
            default= st.session_state.df.columns.to_list()
        )
        # Only keep selected columns for df
        st.session_state.df = st.session_state.df[st.session_state.method_selection["selection"]]
        st.dataframe(st.session_state.df.head())

    # Assign data types
    dtypes = st.container()
    with dtypes:
        # Within method selection, create a key called "dtypes" - dtypes will be a dictionary with key/value for column/datatype

        st.subheader("Specify data types")
        st.write("For number and date columns, any data point with the incorrect format will be coerced to Null")
        st.session_state.method_selection["dtypes"] = dict.fromkeys(st.session_state.df.columns)
        for col in st.session_state.df.columns: # Choose data types
            st.session_state.method_selection["dtypes"][col] = st.selectbox(f"{col}", data_types)

        # Apply data conversion
        for col in st.session_state.df.columns:

            # For text strip forward and back spaces
            if st.session_state.method_selection["dtypes"][col] == data_types[0]:
                #for x in st.session_state.method_selection["dtypes"][col]:
                st.session_state.df[col] = st.session_state.df[col].astype(str)
                st.session_state.df[col] = st.session_state.df[col].str.strip()
                st.session_state.df[col] = st.session_state.df[col].str.casefold() # Ignore upper and lower cases

            # For numbers
            elif st.session_state.method_selection["dtypes"][col] == data_types[1]:
                st.session_state.df[col] = pd.to_numeric(st.session_state.df[col], errors="coerce")
            # For Dates
            elif st.session_state.method_selection["dtypes"][col] == data_types[2]:
                # st.session_state.df[col] = pd.to_datetime(st.session_state.df[col], errors="coerce")
                st.session_state.df[col] = fs.set_date(st.session_state.df[col])
                st.session_state.df[col] = st.session_state.df[col].dt.date

    #ion_state.df)


    # Sort Values
    sort_values = st.container()
    with sort_values:
        st.subheader("Sort Values")
        st.session_state.method_selection["sorting"] = st.multiselect("Select columns in order of priority for sorting values",
                                                                      options= st.session_state.method_selection["selection"])
        st.session_state.df.sort_values(st.session_state.method_selection["sorting"], inplace=True, ignore_index=True)

    # Filter values
    filter = st.container()
    with filter:
        st.subheader("Filter Values")
        for col in st.session_state.df.columns:
            st.session_state.helper[f"filter_{col}"] = st.expander(col)
            with st.session_state.helper[f"filter_{col}"]:
                # For text columns
                if st.session_state.method_selection["dtypes"][col] == data_types[0]:
                    st.session_state.method_selection[f"filter_{col}"] = st.multiselect(
                        f"Select values to keep from column {col}",
                        options= st.session_state.df[col].sort_values().unique(),
                        default= st.session_state.df[col].sort_values().unique().tolist()
                    )
                    if len(st.session_state.method_selection[f"filter_{col}"]) > 0: # If it's empty display everything, else display only selection
                        st.session_state.df = st.session_state.df[st.session_state.df[col].isin(st.session_state.method_selection[f"filter_{col}"])]
                        st.session_state.df.reset_index(drop=True, inplace=True)

                # For numeric columns
                elif st.session_state.method_selection["dtypes"][col] == data_types[1]:
                    a, b = st.columns(2)
                    with a:
                        st.session_state.method_selection[f"filter_{col}"] = st.selectbox(
                            f"Select value range to keep from column {col}",
                            options= numeric_range
                        )
                    with b:
                        if st.session_state.method_selection[f"filter_{col}"] == numeric_range[1]:
                            st.session_state.method_selection[f"filter_{col}_range"] = st.number_input(f"{col} Range")
                            st.session_state.df.query(f"{col} > {st.session_state.method_selection[f'filter_{col}_range']}", inplace=True)
                            st.session_state.df.reset_index(drop=True, inplace=True)

                        elif st.session_state.method_selection[f"filter_{col}"] == numeric_range[2]:
                            st.session_state.method_selection[f"filter_{col}_range"] = st.number_input(f"{col} Range")
                            st.session_state.df.query(f"{col} < {st.session_state.method_selection[f'filter_{col}_range']}", inplace=True)
                            st.session_state.df.reset_index(drop=True, inplace=True)

                        elif st.session_state.method_selection[f"filter_{col}"] == numeric_range[3]:
                            st.session_state.method_selection[f"filter_{col}_range"] = st.number_input(f"{col} Range")
                            st.session_state.df.query(f"{col} == {st.session_state.method_selection[f'filter_{col}_range']}", inplace=True)
                            st.session_state.df.reset_index(drop=True, inplace=True)
                # For dates
                elif st.session_state.method_selection["dtypes"][col] == data_types[2]:
                    a, b = st.columns(2)
                    with a:
                        st.session_state.method_selection[f"filter_{col}"] = st.selectbox(
                            f"Select value range to keep from column {col}",
                            options=numeric_range
                        )
                    with b:
                        if st.session_state.method_selection[f"filter_{col}"] == numeric_range[1]:
                            st.session_state.method_selection[f"filter_{col}_range"] = pd.to_datetime(st.date_input(f"{col} Range", min_value=datetime.datetime(1900, 1, 1)))
                            st.session_state.df = st.session_state.df[st.session_state.df[col] > st.session_state.method_selection[f"filter_{col}_range"]]
                            st.session_state.df.reset_index(drop=True, inplace=True)

                        elif st.session_state.method_selection[f"filter_{col}"] == numeric_range[2]:
                            st.session_state.method_selection[f"filter_{col}_range"] = pd.to_datetime(st.date_input(f"{col} Range", min_value=datetime.datetime(1900, 1, 1)))
                            st.session_state.df = st.session_state.df[st.session_state.df[col] < st.session_state.method_selection[f"filter_{col}_range"]]
                            st.session_state.df.reset_index(drop=True, inplace=True)

                        elif st.session_state.method_selection[f"filter_{col}"] == numeric_range[3]:
                            st.session_state.method_selection[f"filter_{col}_range"] = pd.to_datetime(st.date_input(f"{col} Range", min_value=datetime.datetime(1900, 1, 1)))
                            st.session_state.df = st.session_state.df[st.session_state.df[col] == st.session_state.method_selection[f"filter_{col}_range"]]
                            st.session_state.df.reset_index(drop=True, inplace=True)

        st.dataframe(st.session_state.df)
    # Dealing with missing values
    missing = st.container()
    with missing:
        st.subheader("Missing values")
        # Find missing and add to diagnosis
        st.session_state.diagnosis["missing_general"] = fs.find_missing(st.session_state.df)

        # missing_general method selection
        st.session_state.method_selection["missing_general"] = st.selectbox(f"The dataset contains {st.session_state.diagnosis['missing_general'][2]} rows with missing value(s)",options=method_options)

        # Remove all method
        if st.session_state.method_selection["missing_general"] == method_options[1]:
            fs.remove_row(st.session_state.df, st.session_state.diagnosis["missing_general"][1])

        # Inspect
        elif st.session_state.method_selection["missing_general"] == method_options[2]: # If inspect
            for col in st.session_state.diagnosis["missing_general"][0]: # Accesing map dictionary to iterate over columns
                # For text
                if (st.session_state.method_selection["dtypes"][col] == data_types[0] or st.session_state.method_selection["dtypes"][col] == data_types[2]) \
                        and len(st.session_state.diagnosis["missing_general"][0][col]) > 0:
                    st.session_state.method_selection[f"missing_inspect_{col}"] = st.selectbox(
                        f"{col} has {len(st.session_state.diagnosis['missing_general'][0][col])} missing value(s)",
                        method_options[0:-1]
                    )
                    # If remove
                    if st.session_state.method_selection[f"missing_inspect_{col}"] == method_options[1]:
                        fs.remove_row(st.session_state.df, st.session_state.diagnosis["missing_general"][0][col])

                # For Numeric
                elif st.session_state.method_selection["dtypes"][col] == data_types[1] and len(st.session_state.diagnosis["missing_general"][0][col]) > 0:
                    st.session_state.method_selection[f"missing_inspect_{col}"] = st.selectbox(
                        f"{col} has {len(st.session_state.diagnosis['missing_general'][0][col])} missing value(s)",
                        method_numeric_options)
                    # If remove all
                    if st.session_state.method_selection[f"missing_inspect_{col}"] == method_numeric_options[1]:
                        fs.remove_row(st.session_state.df, st.session_state.diagnosis["missing_general"][0][col])
                    # Elif impute average
                    elif st.session_state.method_selection[f"missing_inspect_{col}"] == method_numeric_options[2]:
                        fs.missing_average(st.session_state.df[col])
                    # Elif replace with zeros
                    elif st.session_state.method_selection[f"missing_inspect_{col}"] == method_numeric_options[3]:
                        fs.missing_zeros(st.session_state.df[col])

        #st.write(st.session_state.df)

    outliers = st.container()
    with outliers:
        st.subheader("Outliers - Numbers")
        # Create a dictionary of numeric columns to set outliers as values
        st.session_state.diagnosis["outliers"] = dict.fromkeys([col for col in st.session_state.df.columns if st.session_state.method_selection["dtypes"][col] == data_types[1]])
        # Get outliers for each numeric column
        for col in st.session_state.diagnosis["outliers"]:
            st.session_state.diagnosis["outliers"][col] = fs.find_outliers(st.session_state.df, st.session_state.df[col])

        # Create method selection for numeric rows WITH detected outliers
        st.session_state.method_selection["outliers"] = dict.fromkeys([x for x in st.session_state.diagnosis["outliers"] if st.session_state.diagnosis["outliers"][x] != None])
        for col in st.session_state.method_selection["outliers"]:
            if st.session_state.diagnosis["outliers"][col] != []:
                st.session_state.method_selection["outliers"][col] = st.selectbox(
                    f"{col} has {len(st.session_state.diagnosis['outliers'][col])} detected outliers",
                    method_numeric_options
                )
                if st.session_state.method_selection["outliers"][col] == method_numeric_options[1]:
                    fs.remove_row(st.session_state.df, st.session_state.diagnosis["outliers"][col])
                # Elif impute average
                else:
                    if st.session_state.method_selection["outliers"][col] == method_numeric_options[2]:
                        fs.outliers_average(st.session_state.df, col, st.session_state.diagnosis["outliers"][col])
                    # Elif replace with zeros
                    elif st.session_state.method_selection[f"outliers"][col] == method_numeric_options[3]:
                        fs.outliers_zeros(st.session_state.df, col, st.session_state.diagnosis["outliers"][col])


                    st.dataframe(st.session_state.df.iloc[st.session_state.diagnosis["outliers"][col]])


    fuzzy = st.container()
    with fuzzy:
        st.subheader("Outliers - Text")
        # Get matches
        st.session_state.diagnosis["fuzzy"] = {}
        for col in st.session_state.df:
            # Only use columns with dtype Text
            if st.session_state.method_selection["dtypes"][col] == data_types[0]:
                # Get fuzzy matches
                st.session_state.diagnosis["fuzzy"][col] = fs.find_matches(fs.get_combinations(st.session_state.df[col]))
                #st.write(st.session_state.diagnosis["fuzzy"][col])
        for col in st.session_state.diagnosis["fuzzy"]:
            if st.session_state.diagnosis["fuzzy"][col] != []:

                # use expander better

                #a.write(f"{len(st.session_state.diagnosis['fuzzy'][col])} text outliers detected in {col}")
                st.session_state.method_selection[f"inspect_fuzzy_{col}"] = st.expander(f"{len(st.session_state.diagnosis['fuzzy'][col])} text outliers detected in {col}")
                with st.session_state.method_selection[f"inspect_fuzzy_{col}"]:
                    for x in st.session_state.diagnosis["fuzzy"][col]:
                        st.session_state.method_selection[f"fuzzy_{col}_{st.session_state.diagnosis['fuzzy'][col].index(x)}"] =\
                        st.selectbox(f"{x[0]} and {x[1]} look very similar",["Keep Both", f"Replace {x[0]} with {x[1]}", f"Replace {x[1]} with {x[0]}"])

                        # If keep both
                            # pass
                        # if replace 0 - 1
                        if st.session_state.method_selection[f"fuzzy_{col}_{st.session_state.diagnosis['fuzzy'][col].index(x)}"] == f"Replace {x[0]} with {x[1]}":
                            st.session_state.df.replace({col:{x[0]:x[1]}}, inplace=True)
                        elif st.session_state.method_selection[f"fuzzy_{col}_{st.session_state.diagnosis['fuzzy'][col].index(x)}"] == f"Replace {x[1]} with {x[0]}":
                            st.session_state.df.replace({col:{x[1]:x[0]}}, inplace=True)

    download = st.container()
    with download:
        st.session_state.clean = fs.df_to_csv(st.session_state.df)
        st.download_button(
            label="Download clean data",
            data=st.session_state.clean,
            file_name="clean.csv",
            mime='text/csv'
        )


