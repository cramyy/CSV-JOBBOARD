import requests
import pandas as pd

# URL of the Google Spreadsheet exported as an Excel file
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1MvcSBIFc6hgd2bqN1NEEhfgcxp9NfPwT9qicIVFiwXA/export?format=xlsx'

# Fetch the spreadsheet data
response = requests.get(spreadsheet_url)
with open('jobs.xlsx', 'wb') as file:
    file.write(response.content)

# Load the data into a DataFrame
df = pd.read_excel('jobs.xlsx', sheet_name='Client_Job_Posts')

# Generate the HTML for the job cards
job_cards = ''
for _, row in df.iterrows():
    job_cards += f'''
    <div class="job-card">
        <h3>{row['Post']}</h3>
        <p>{row['Client Name']}</p>
        <p>{row['Job Location']}</p>
        <p>{row['Qualification']}</p>
        <p class="salary">${row['Salary']} yearly</p>
        <p>{row['Responsibility']}</p>
        <a href="#" class="apply-button">Apply Now</a>
    </div>
    '''

# Read the index.html template
with open('index.html', 'r') as file:
    html_content = file.read()

# Insert the job cards into the template
updated_html = html_content.replace('<!-- Jobs will be inserted here by the Python script -->', job_cards)

# Save the updated HTML
with open('index.html', 'w') as file:
    file.write(updated_html)
