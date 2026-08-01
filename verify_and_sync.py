import json
import os
import re
import socket
import dns.resolver
import pandas as pd
from datetime import datetime

# Path to files
SCORED_LEADS_FILE = 'audit_data/scored_leads.json'
CRM_FILE = 'audit_data/crm_google_sheets.csv'

def verify_email(email):
    """Verify email syntax and MX records."""
    if not email:
        return False, "Missing email"
    
    # Syntax check
    regex = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
    if not re.match(regex, email.lower()):
        return False, "Invalid syntax"
    
    # MX record check
    domain = email.split('@')[1]
    try:
        records = dns.resolver.resolve(domain, 'MX')
        if records:
            return True, "Valid"
    except Exception as e:
        return False, f"MX check failed: {str(e)}"
    
    return False, "No MX records"

def generate_email_body(lead):
    company = lead['company']
    dm = lead['dm']
    pain_points = lead['pain_points']
    location = lead['location']
    
    automation_gaps = []
    if not lead.get("has_chatbot", True):
        automation_gaps.append("24/7 AI lead capture widget/chatbot")
    if not lead.get("has_booking_calendar", True):
        automation_gaps.append("instant booking calendar")
    if not lead.get("has_auto_responder", True):
        automation_gaps.append("automated lead confirmation / instant auto-responder")

    hook = f"I noticed {company} is missing a critical piece of your lead automation: no {', '.join(automation_gaps)}. This often leads to an estimated ${lead.get('estimated_monthly_lost_revenue', 0):,.0f} in lost monthly revenue."
    
    secondary_hook = ""
    if any("Slow website load time" in pp for pp in pain_points):
        secondary_hook += " I also noticed your website loads slowly, which can deter potential clients."
    
    # Fix DM name if it's generic
    first_name = dm.split()[0] if dm else 'Team'
    if first_name.lower() in ['information', 'the', 'admin', 'contact']:
        # Try to find a better name in the company string or just use 'Team'
        if 'Brenda' in dm: first_name = 'Brenda'
        elif 'Gabe' in dm: first_name = 'Gabe'
        else: first_name = 'Team'
    
    body = f"""Hi {first_name},

{hook}{secondary_hook}

At Vibe Studio AI, we specialize in 'Full-Funnel SDR & Lead Response Automation' for real estate and mortgage agencies like yours. Our automated 60-second lead follow-ups have been shown to increase booking rates by over 300%.

We help businesses like {company} convert more leads into appointments, ensuring no potential client falls through the cracks. Would you be open to a brief 15-minute call to explore how we can help you capture that estimated ${lead.get('estimated_monthly_lost_revenue', 0):,.0f} in lost monthly revenue and significantly boost your booking rates?

Best,

Kiran Irshad | Vibe Studio AI"""
    return body

def run_sync():
    if not os.path.exists(SCORED_LEADS_FILE):
        print("Scored leads file not found.")
        return

    with open(SCORED_LEADS_FILE, 'r') as f:
        data = json.load(f)
        hot_leads = data['hot_leads']

    verified_leads = []
    crm_data = []
    
    # Load existing CRM data to append
    if os.path.exists(CRM_FILE):
        existing_crm = pd.read_csv(CRM_FILE)
    else:
        existing_crm = pd.DataFrame(columns=['Date', 'Company Name', 'Contact Person', 'Email', 'Audit PDF Link', 'Status', 'Notes / Follow-up Date'])

    for lead in hot_leads:
        email = lead.get('email')
        is_valid, reason = verify_email(email)
        
        if is_valid:
            print(f"Verified: {email} for {lead['company']}")
            body = generate_email_body(lead)
            subject = f"Quick question about {lead['company']}'s website / Lead capture"
            
            verified_leads.append({
                "company": lead['company'],
                "dm": lead['dm'],
                "email": email,
                "subject": subject,
                "body": body,
                "lead_score": lead['lead_score']
            })
            
            # CRM Entry
            pdf_link = f"audit_data/pdf_reports/{lead['company'].replace(' ', '_')}_Audit_Report.pdf"
            crm_data.append({
                'Date': datetime.now().strftime('%Y-%m-%d'),
                'Company Name': lead['company'],
                'Contact Person': lead['dm'],
                'Email': email,
                'Audit PDF Link': pdf_link,
                'Status': 'Email Sent',
                'Notes / Follow-up Date': 'Initial outreach'
            })
        else:
            print(f"Skipping {lead['company']}: {reason}")

    # Save verified drafts
    with open('audit_data/verified_email_drafts.json', 'w') as f:
        json.dump(verified_leads, f, indent=2)

    # Update CRM
    if crm_data:
        new_crm = pd.DataFrame(crm_data)
        updated_crm = pd.concat([existing_crm, new_crm], ignore_index=True)
        updated_crm.to_csv(CRM_FILE, index=False)
        print(f"CRM updated with {len(crm_data)} new leads.")

if __name__ == "__main__":
    run_sync()
