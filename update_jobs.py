import sys
import requests
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import re

# Get the spreadsheet URL from command-line argument
if len(sys.argv) > 1:
    spreadsheet_url = sys.argv[1]
else:
    print("Error: No spreadsheet URL provided.")
    sys.exit(1)

# Fetch the spreadsheet data
response = requests.get(spreadsheet_url)
with open('jobs.xlsx', 'wb') as file:
    file.write(response.content)

# Load the data into a DataFrame

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

# Debug: Print column names
print("Columns in the DataFrame:", df.columns.tolist())

# Check for 'OnFire' column
if 'OnFire' in df.columns:
    print("'OnFire' column exists")
    print("Unique values in 'OnFire' column:", df['OnFire'].unique())
    
    # Normalize 'OnFire' values
    df['OnFire'] = df['OnFire'].str.lower().str.strip()
    print("Normalized unique values in 'OnFire' column:", df['OnFire'].unique())
else:
    print("'OnFire' column does not exist")

# Convert DataFrame to a list of dictionaries
jobs_list = df.to_dict(orient='records')

# Debug: Print the first job dictionary
print("First job data:", jobs_list[0])

# Setup Jinja2 environment
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('template.html')

# Render the template with job data
html_output = template.render(jobs=jobs_list)

# Debug: Check if 'hot-job' class is present in the rendered HTML
if 'hot-job' in html_output:
    print("'hot-job' class is present in the rendered HTML")
else:
    print("'hot-job' class is NOT present in the rendered HTML")

# Save the rendered HTML to index.html using UTF-8 encoding
with open('index.html', 'w', encoding='utf-8') as file:
    file.write(html_output)

print("Jobs updated successfully!")