# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 14:55:29 2023

@author: Adriano Reimer
"""
# Import necessary libraries
from Bio import Entrez
import pandas as pd
import string
import os
import datetime


os.chdir(r"C:\Users\Adriano Reimer\Documents\sysrev\out5")

# Create a folder with the current date (YYYY-MM-DD format)
current_date = datetime.date.today().strftime("%Y-%m-%d")
output_folder = os.path.join(r"C:\Users\Adriano Reimer\Documents\sysrev\out5", current_date)

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Function to search PubMed with the specified query
def search(query):
    # Define the user email for Entrez
    Entrez.email = 'adrianoreimer@gmail.com'
    # Use the Entrez esearch function to search PubMed
    handle = Entrez.esearch(db='pubmed',
                            sort='relevance',
                            retmax=25000,
                            retmode='xml',
                            term=query)
    results = Entrez.read(handle)
    return results

# Function to fetch the details for a list of PubMed IDs
def fetch_details(id_list):
    ids = ','.join(id_list)
    Entrez.email = 'adrianoreimer@gmail.com'
    handle = Entrez.efetch(db='pubmed',
                            retmode='xml',
                            id=ids)
    results = Entrez.read(handle)
    return results

# Function to clean filenames
def clean_filename(filename, whitelist="-_. %s%s" % (string.ascii_letters, string.digits)):
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    filename = filename.replace('Title/Abstract', '_')
    
    # Remove characters not in the whitelist
    filename = ''.join(c for c in filename if c in whitelist)
    
    # Prevent consecutive underscores and dots at the start of the filename
    filename = filename.replace('__', '_')
    filename = filename.lstrip('.').lstrip('_')
    
    # Remove parentheses
    filename = filename.replace('(', '').replace(')', '')
    
    return filename

# Function to save data to a CSV file
def save_to_csv(query, data):
    df = pd.DataFrame(data, columns=[
        'PubMedID', 'Title', 'Authors', 'Abstract', 'Journal', 'Language', 'Year', 'Month', 'Keywords'])
    
    filename = clean_filename(f"busca_pubmed_{query}.csv")
    
    # Save the CSV files in the folder with the current date
    csv_path = os.path.join(output_folder, filename)
    df.to_csv(csv_path, encoding='utf-8', index=False)



# Define the terms terms
DBS_terms = ["deep brain stimulation", "DBS"]
Target = ["Striatum", "Striatal", "Striato", "Accumbens", "Subthalamic", "Subthalamus"]
Limiter = ["Animal", "Animals", "Rodent", "Rodents", "Rat", "Rats", "Mouse", "Mice"]

# Generate the list of queries
Queries = []

for dbs in DBS_terms:
    for target in Target:
        for limiter in Limiter:
            query = f'"{dbs}" AND "{target}" AND "{limiter}"'
            Queries.append(query)

# Print each query
for query in Queries:
    print(query)

# Initialize the total results counter    
total_results = 0


# For each query, search PubMed, fetch the details for each result, and save the results to a CSV file
for query in Queries:
    studies = search(query)
    studiesIdList = studies['IdList']

    id_list = []
    title_list= []
    abstract_list=[]
    journal_list = []
    language_list =[]
    pubdate_year_list = []
    pubdate_month_list = []
    authors_list = []
    keywords_list = []

    chunk_size = 10000
    for chunk_i in range(0, len(studiesIdList), chunk_size):
        chunk = studiesIdList[chunk_i:chunk_i + chunk_size]
        papers = fetch_details(chunk)
        for i, paper in enumerate(papers['PubmedArticle']):
            id_list.append(paper['MedlineCitation']['PMID'])
            title_list.append(paper['MedlineCitation']['Article']['ArticleTitle'])
            try:
                abstract_parts = paper['MedlineCitation']['Article']['Abstract']['AbstractText']
                abstract_full = ' '.join([part for part in abstract_parts])
                abstract_list.append(abstract_full)
            except:
                abstract_list.append('No Abstract')
            journal_list.append(paper['MedlineCitation']['Article']['Journal']['Title'])
            language_list.append(paper['MedlineCitation']['Article']['Language'][0])
            try:
                pubdate_year_list.append(paper['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['Year'])
            except:
                pubdate_year_list.append('No Data')
            try:
                pubdate_month_list.append(paper['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['Month'])
            except:
                pubdate_month_list.append('No Data')
                # Some papers might not have authors or keywords, so use a try/except block to handle these cases
            try:
                authors = paper['MedlineCitation']['Article']['AuthorList']
                authors_str_list = [f"{author['ForeName']} {author['LastName']}" for author in authors]
                authors_str = ', '.join(authors_str_list)
                authors_list.append(authors_str)
            except:
                authors_list.append('No Authors')
            try:
                keywords = paper['MedlineCitation']['KeywordList']
                keywords_str_list = [keyword for keyword in keywords[0]]
                keywords_str = ', '.join(keywords_str_list)
                keywords_list.append(keywords_str)
            except:
                keywords_list.append('No Keywords')
                
    # Zip the lists together and save the data to a CSV file
    data = list(zip(id_list, title_list, authors_list, abstract_list, journal_list, language_list, pubdate_year_list, pubdate_month_list, keywords_list))
    save_to_csv(query, data)
    
    # Create a summary for this query
    num_results = len(id_list)
    print(f"Query: {query}\nNumber of Results: {num_results}\n")
    
    total_results += num_results

# Create a summary of all queries
print(f"Total Number of Results Across All Queries: {total_results}")
