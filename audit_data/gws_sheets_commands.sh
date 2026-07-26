# GWS CLI Commands to push to Google Sheets
# Run these after authenticating with: gws auth login

# 1. Create a new spreadsheet
gws sheets spreadsheets create --json '{"properties":{"title":"HOT Leads - Real Estate & Mortgage TX/FL"}}'

# 2. Once created, use the spreadsheet ID from the response to populate data:
# gws sheets spreadsheets.values append --spreadsheet-id YOUR_SPREADSHEET_ID --range "Sheet1!A1:H1" --json '{"values":[["Company Name","Contact Person","Title","Location","Website","Identified Pain Point","Lead Score","Status"]]}'

# 3. Append HOT leads data
