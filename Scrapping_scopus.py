# -*- coding: utf-8 -*-
"""
Created on Sat Oct 21 12:10:38 2023

@author: Adriano Reimer
"""

# Import the necessary modules
import os
import datetime
import pybliometrics
from pybliometrics.scopus import ScopusSearch
import pandas as pd
from IPython.display import display



os.chdir(r"")

# Define the terms terms
DBS_terms = ["deep brain stimulation", "DBS"]
Target = ["Striatum", "Striatal", "Striato", "Accumbens", "Subthalamic", "Subthalamus"]
Limiter = ["Animal", "Animals", "Rodent", "Rodents", "Rat", "Rats", "Mouse", "Mice"]

# Define the key for accessing Scopus API
key = [""]

# Set the key as an environment variable
pybliometrics.scopus.utils.create_config(key)

# Dictionary to store the number of results for each search term
results_dict = {}

# Create a new directory with the current date
today = datetime.date.today().strftime("%Y-%m-%d")
os.makedirs(today, exist_ok=True)

# Loop through the combinations of terms and perform the searches
for dbs in DBS_terms:
    for target in Target:
        for limiter in Limiter:
            # Construct the query string using the boolean AND operator and parentheses
            query =f'TITLE-ABS-KEY("{dbs}") AND TITLE-ABS-KEY("{target}") AND TITLE-ABS-KEY("{limiter}")'
            # Print a message to indicate the start of each search
            print(f"Starting search for {query}...")
            # Create a ScopusSearch object with the query and the limit of 25 results per request
            s = ScopusSearch(query, count=25)
            # Convert the results to a pandas dataframe
            df = pd.DataFrame(s.results)
            # Add search term as a new column
            df['Search_Term'] = query
            # Print a message to indicate the end of each search and show a snapshot of the dataframe
            print(f"Search for {query} completed. Found {len(df)} results.")
            display(df.head())
            # Save the dataframe as a csv file with a name based on the query
            filename = f"{today}/busca_scopus_TITLE-ABS-KEY_{dbs}_{target}_{limiter}" + ".csv"
            df.to_csv(filename, index=False)
            # Print a message to indicate the completion of each file saving
            print(f"Saved results to {filename}.")
            # Store the number of results in the dictionary
            results_dict[query] = len(df)

# Convert the results dictionary to a DataFrame
results_df = pd.DataFrame.from_dict(results_dict, orient='index', columns=['Number_of_Results'])

# Calculate the grand total
grand_total = results_df['Number_of_Results'].sum()

# Add the grand total to the DataFrame
results_df.loc['Grand Total'] = grand_total

# Save the DataFrame as a CSV file
results_df.to_csv(f"{today}/extraction_result.csv")
