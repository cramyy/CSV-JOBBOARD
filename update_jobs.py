import requests
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os
import re

# URL of the Google Spreadsheet exported as an Excel file
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1MvcSBIFc6hgd2bqN1NEEhfgcxp9NfPwT9qicIVFiwXA/export?format=xlsx'

# Fetch the spreadsheet data
response = requests.get(spreadsheet_url)
with open('jobs.xlsx', 'wb') as file:
    file.write(response.content)

# Load the data into a DataFrame
df = pd.read_excel('jobs.xlsx', sheet_name='Client_Job_Posts')

# Remove rows where 'Post' is NaN
df = df.dropna(subset=['Post'])

# Function to remove text within brackets
def remove_brackets(text):
    if isinstance(text, str):
        return re.sub(r'\[.*?\]|\(.*?\)', '', text).strip()
    return text

# Clean data by removing text within brackets
df['Post'] = df['Post'].apply(remove_brackets)
df['Client Name'] = df['Client Name'].apply(remove_brackets)
df['Job Location'] = df['Job Location'].apply(remove_brackets)
df['Qualification'] = df['Qualification'].apply(remove_brackets)
df['Responsibility'] = df['Responsibility'].apply(remove_brackets)

# Setup Jinja2 environment
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('template.html')

# Render the template with job data
html_output = template.render(jobs=df.to_dict(orient='records'))

# Delete the existing index.html file if it exists
if os.path.exists('index.html'):
    os.remove('index.html')

# Save the rendered HTML to index.html
with open('index.html', 'w') as file:
    file.write(html_output)
