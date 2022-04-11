# linda.ai

Visit linda.ai with this link: https://share.streamlit.io/samuwa/linda.ai/main/app.py

Linda.ai is a prototype for a self-service data cleaning tool. The objective is to create a friendly graphical user interface (GUI) for performing and tracking different data cleaning tasks in a guided manner, such as:
  •	Identifying and eliminating duplicate rows from data set.
  •	Dropping unwanted columns.
  •	Specifying data types for each column.
  •	Sorting dataset by selected columns.
  •	Filtering values by specified conditions.
  •	Handling missing values.
  •	Detecting and managing outliers and anomalies.
    o	Numeric: Using standard deviations, assuming normal distribution.
    o	String: Based on Levenshtein distance for fuzzy string matching.

Tech Stack
Linda.ai is fully programmed in the Python programming language, as it counts with all the necessary modules:
  •	Pandas: transforms datasets into dataframe for easy manipulations and computing.
  •	Streamlit: Open-source project owned by Snowflake, allows programmers to design and host interactive GUIs with just python.
  •	Datetime: Manipulate date-format data points.
  •	Scipy: Get statistical analysis from data.
  •	Fuzzywuzzy: Find fuzzy string data points.
