import sys
import requests
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import re
from git import Repo
import os

def convert_to_export_link(shareable_link):
    file_id = shareable_link.split('/d/')[1].split('/')[0]
    return f'https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx'

def main(shareable_link):
    spreadsheet_url = convert_to_export_link(shareable_link)

    # Fetch the spreadsheet data
    response = requests.get(spreadsheet_url)
    with open('jobs.xlsx', 'wb') as file:
        file.write(response.content)

    # Load the data into a DataFrame
    df = pd.read_excel('jobs.xlsx', sheet_name='Client_Job_Posts')

    # Remove rows where 'Post' is NaN
    df = df.dropna(subset=['Post'])

    # Function to remove parentheses and their content
    def remove_parentheses(text):
        return re.sub(r'\([^)]*\)', '', str(text)).strip()

    # Apply the function to all columns
    for column in df.columns:
        df[column] = df[column].apply(remove_parentheses)

    # Setup Jinja2 environment
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template.html')

    # Render the template with job data
    html_output = template.render(jobs=df.to_dict(orient='records'))

    # Save the rendered HTML to index.html using UTF-8 encoding
    with open('index.html', 'w', encoding='utf-8') as file:
        file.write(html_output)

    # Push changes to GitHub
    repo = Repo('.')
    
    # Stage all changes
    repo.git.add(A=True)
    
    # Check if there are changes to commit
    if repo.is_dirty(untracked_files=True):
        repo.git.commit('-m', 'Update job listings')
        origin = repo.remote(name='origin')
        origin.push()
        print("Job board updated and changes pushed to GitHub!")
    else:
        print("No changes to commit. Job board is up to date.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("No Google Sheet link provided.")