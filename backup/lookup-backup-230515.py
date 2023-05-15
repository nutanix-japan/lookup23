from flask import Flask, render_template, request
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

app = Flask(__name__)

# Set up credentials for Google Sheets API
creds = service_account.Credentials.from_service_account_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)

r1_r2_map = {
    "Lab - Consolidated Storage": [3,4,5],
    "Calm Iaas":[6,7,8,9,10,11],
    "Disaster recovery":[12,13,14,15,16,17],
    "NDB":[18,19,20,21,22,23],
    "Lab - OCP (Openshift, Objects, Files)":[24,25,26,27,28,29],
    "Lab GTS23 - Expand":[30,31,32,33,34,35],
    "Lab GTS23 - Migrate":[36,37,38,39,40,41],
    "Lab GTS23 - Secure":[42,43,44,45,46,47]
}

# Define function to search for rows in the sheet
def search_sheet(spreadsheet_id, sheet_name, search_col, search_term):
    service = build('sheets', 'v4', credentials=creds)
    sheet_range = f'{sheet_name}!A:ZZ'  # adjust the range as per your sheet data
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=sheet_range).execute()
    rows = result.get('values', [])

    if not rows:
        return []

    # Find the column index to search in
    headers = rows[0]
    search_col_index = headers.index(search_col)

    # Filter the rows based on search term
    filtered_rows = [headers]
    for row in rows[1:]:
        if row[search_col_index] == search_term:
            filtered_rows.append(row)
    print(rows[0])
    print(rows[1])
    print(len(rows[0]))
    return filtered_rows

# Define a route for the search page
@app.route('/', methods=['GET', 'POST'])
def search():
    # Get the search parameters from the form submission
    if request.method == 'POST':
        search_term = request.form['search_term']
        # Search the sheet for matching rows
        spreadsheet_id = '1meMee6yCvtplZCkljknSYtdFECBEPauw8kn-1YB5x7A'
        sheet_name = 'Sheet1'
        search_col = 'Email'
        rows = search_sheet(spreadsheet_id, sheet_name, search_col, search_term)
        return render_template('search.html', rows=rows, map=r1_r2_map)
    else:
        return render_template('search.html', rows=None)

if __name__ == '__main__':
    app.run(debug=True)
