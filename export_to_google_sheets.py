#!/usr/bin/env python3
"""
Export HOT leads to a Google Sheets-ready CSV file.
Also generates the gws CLI commands needed to push to Google Sheets.
"""

import json
import csv

# Load HOT leads
with open('audit_data/scored_leads.json', 'r') as f:
    data = json.load(f)
    hot_leads = data['hot_leads']

# Also load all scored for the full sheet
all_scored = data['all_scored']

# Create HOT leads CSV
csv_file = 'audit_data/hot_leads_google_sheets.csv'
with open(csv_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        'Company Name',
        'Contact Person',
        'Title',
        'Location',
        'Website',
        'Identified Pain Point',
        'Lead Score',
        'Status'
    ])
    
    for lead in hot_leads:
        pain_summary = '; '.join(lead['pain_points'][:2])
        writer.writerow([
            lead['company'],
            lead['dm'],
            lead['title'],
            lead['location'],
            lead['website'],
            pain_summary,
            lead['lead_score'],
            'HOT - Ready for Outreach'
        ])

# Create full pipeline CSV (all leads)
full_csv = 'audit_data/full_pipeline_leads.csv'
with open(full_csv, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        'Company Name',
        'Contact Person',
        'Title',
        'Location',
        'Website',
        'Identified Pain Point',
        'Lead Score',
        'Status',
        'Load Time (ms)',
        'Has Chatbot'
    ])
    
    for lead in all_scored:
        pain_summary = '; '.join(lead['pain_points'][:2])
        status = 'HOT - Ready for Outreach' if lead['lead_score'] > 80 else 'WARM - Monitor'
        writer.writerow([
            lead['company'],
            lead['dm'],
            lead['title'],
            lead['location'],
            lead['website'],
            pain_summary,
            lead['lead_score'],
            status,
            lead['load_time_ms'],
            'Yes' if lead['has_chatbot'] else 'No'
        ])

print(f"HOT leads CSV saved: {csv_file}")
print(f"Full pipeline CSV saved: {full_csv}")
print(f"\nHOT Leads ({len(hot_leads)}):")
for lead in hot_leads:
    print(f"  [{lead['lead_score']}] {lead['company']} | {lead['dm']} | {lead['location']}")
    print(f"      Pain: {'; '.join(lead['pain_points'][:2])}")

# Generate GWS commands for Google Sheets upload
gws_commands = f"""# GWS CLI Commands to push to Google Sheets
# Run these after authenticating with: gws auth login

# 1. Create a new spreadsheet
gws sheets spreadsheets create --json '{{"properties":{{"title":"HOT Leads - Real Estate & Mortgage TX/FL"}}}}'

# 2. Once created, use the spreadsheet ID from the response to populate data:
# gws sheets spreadsheets.values append --spreadsheet-id YOUR_SPREADSHEET_ID --range "Sheet1!A1:H1" --json '{{"values":[["Company Name","Contact Person","Title","Location","Website","Identified Pain Point","Lead Score","Status"]]}}'

# 3. Append HOT leads data
"""

with open('audit_data/gws_sheets_commands.sh', 'w') as f:
    f.write(gws_commands)

print(f"\nGWS commands saved to: audit_data/gws_sheets_commands.sh")
print("\nNOTE: Google Sheets integration requires gws auth login.")
print("The CSV files are ready for manual import into Google Sheets.")
