import requests
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os

# URL of the Google Spreadsheet exported as an Excel file
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1MvcSBIFc6hgd2bqN1NEEhfgcxp9NfPwT9qicIVFiwXA/export?format=xlsx'

# Fetch the spreadsheet data
response = requests.get(spreadsheet_url)
with open('jobs.xlsx', 'wb') as file:
    file.write(response.content)

# Load the data into a DataFrame
df = pd.read_excel('jobs.xlsx', sheet_name='Client_Job_Posts')

# Setup Jinja2 environment
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('template.html')

# Render the template with job data
html_output = template.render(jobs=df.to_dict(orient='records'))

# Delete the existing index.html file if it exists
if os.path.exists('index.html'):
    os.remove('index.html')

# Save the rendered HTML to index.html with UTF-8 encoding
with open('index.html', 'w', encoding='utf-8') as file:
    file.write(html_output)

print("HTML file updated successfully.")