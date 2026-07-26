#!/bin/bash
# run_pipeline.sh - Automated Daily Lead Finder Pipeline
# This script runs the full pipeline, generates timestamped reports, and pushes to GitHub.

set -e

TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
REPORT_FILE="LEAD_REPORT_${TIMESTAMP}.md"

echo "Starting Automated Lead Finder Pipeline..."

# 1. Run Audit
echo "1/4. Running website audits..."
python3 audit_sites.py

# 2. Run Scoring
echo "2/4. Scoring leads..."
python3 score_leads_v2.py

# 3. Generate Emails
echo "3/4. Generating email drafts..."
python3 email_drafts.py

# 4. Export to Sheets
echo "4/4. Exporting to CSV..."
python3 export_to_google_sheets.py

# 5. Generate Timestamped Report
echo "Generating timestamped report..."
cp LEAD_REPORT.md "$REPORT_FILE"
echo -e "\n\n---\n*Report generated at: $(date)*" >> "$REPORT_FILE"

# 6. Commit and Push to GitHub
echo "Committing and pushing to GitHub..."
git add -A
git commit -m "Automated Pipeline Run: $TIMESTAMP

- Updated audit data
- Generated new HOT leads
- Updated email drafts
- Added timestamped report: $REPORT_FILE"

# If the remote is not set, use the user's PAT
# Note: The PAT is managed by the user's git credentials or the Manus GitHub connector
git push origin main

echo "Pipeline complete. Files pushed to GitHub!"
