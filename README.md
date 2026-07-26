# Autonomous Lead Finder Agent

This repository contains the complete Python-based pipeline for the **Autonomous Lead Finder Agent**. The system automates lead generation, pain-point auditing, scoring, email drafting, and export to Google Sheets.

## Pipeline Overview

The agent follows a 6-step execution workflow:

1. **Lead Scraping**: Searches for target businesses (Real Estate & Mortgage Brokers in TX/FL).
2. **Pain-Point Audit**: Crawls lead websites to identify missing chatbots, slow loading speeds, and lack of mobile optimization.
3. **Scoring & Filtering**: Assigns a 1-100 score to each lead. Only "HOT Leads" (>80) are kept.
4. **Email Drafting**: Generates hyper-personalized cold emails targeting the specific pain points found.
5. **Google Sheets Export**: Formats the HOT leads into a CSV/JSON ready for Google Sheets API integration.
6. **Code Backup**: This repository serves as the version-controlled backup for all agent scripts.

## Requirements

- Python 3.8+
- `requests`
- `beautifulsoup4`

Install dependencies:
```bash
pip install requests beautifulsoup4
```

## How to Run

1. **Run the Audit Script**:
   ```bash
   python3 audit_sites.py
   ```
   *This will crawl the URLs in the script and generate `audit_results.json`.*

2. **Run the Scoring Script**:
   ```bash
   python3 score_leads_v2.py
   ```
   *This evaluates the audit results and outputs the HOT leads.*

3. **Generate Emails**:
   ```bash
   python3 email_drafts.py
   ```
   *This creates the `email_drafts.json` file containing the personalized outreach copy.*

4. **Export to Sheets**:
   ```bash
   python3 export_to_google_sheets.py
   ```
   *This generates the final CSV files ready for CRM or Google Sheets import.*

## Directory Structure

- `audit_sites.py`: The web scraper and audit tool.
- `score_leads_v2.py`: The lead scoring logic.
- `email_drafts.py`: The personalized email generator.
- `export_to_google_sheets.py`: The formatting and export script.
- `audit_data/`: Contains the generated JSON and CSV files.

## Configuration

To change the target criteria, edit the `leads` array in `audit_sites.py` with your desired companies and URLs.
