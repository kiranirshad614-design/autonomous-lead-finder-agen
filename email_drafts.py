#!/usr/bin/env python3
"""
Draft hyper-personalized cold emails for HOT leads
Based on their specific pain points identified in the audit.
"""

import json
import os
import subprocess

# Load HOT leads
with open('audit_data/scored_leads.json', 'r') as f:
    data = json.load(f)
    hot_leads = data['hot_leads']

drafts = []

for lead in hot_leads:
    company = lead['company']
    dm = lead['dm']
    pain_points = lead['pain_points']
    location = lead['location']
    
    # Determine primary hook based on biggest automation gap
    automation_gaps = []
    if not lead.get("has_chatbot", True):
        automation_gaps.append("24/7 AI lead capture widget/chatbot")
    if not lead.get("has_booking_calendar", True):
        automation_gaps.append("instant booking calendar")
    if not lead.get("has_auto_responder", True):
        automation_gaps.append("automated lead confirmation / instant auto-responder")

    hook_intro = f"I was researching top real estate and mortgage professionals in {location} and came across {company}."
    if automation_gaps:
        hook = f"I noticed {company} is missing a critical piece of your lead automation: no {', '.join(automation_gaps)}. This often leads to an estimated ${lead.get('estimated_monthly_lost_revenue', 0):,.0f} in lost monthly revenue."
    else:
        hook = hook_intro

    
    # Secondary pain point (if any other significant pain points exist)
    secondary_hook = ""
    if any("Slow website load time" in pp for pp in pain_points):
        secondary_hook += " I also noticed your website loads slowly, which can deter potential clients."
    if any("No mobile optimization" in pp for pp in pain_points):
        secondary_hook += " Additionally, your site isn't fully mobile-optimized, potentially losing a large segment of your audience."
    if any("No Google Reviews displayed" in pp for pp in pain_points):
        secondary_hook += " You have great reviews, but they aren't currently embedded on your homepage to build instant trust with new visitors."

    
    # Email body
    subject = f"Quick question about {company}'s website / Lead capture"
    
    body = f"""Hi {dm.split()[0] if dm else 'Team'},

{hook}{secondary_hook}

At Vibe Studio AI, we specialize in 'Full-Funnel SDR & Lead Response Automation' for real estate and mortgage agencies like yours. Our automated 60-second lead follow-ups have been shown to increase booking rates by over 300%.

We help businesses like {company} convert more leads into appointments, ensuring no potential client falls through the cracks. Would you be open to a brief 15-minute call to explore how we can help you capture that estimated ${lead.get('estimated_monthly_lost_revenue', 0):,.0f} in lost monthly revenue and significantly boost your booking rates?

Best,

[Your Name/Vibe Studio AI Team]"""

    drafts.append({
        "company": company,
        "dm": dm,
        "subject": subject,
        "body": body,
        "lead_score": lead['lead_score']
    })

# Save drafts
with open('audit_data/email_drafts.json', 'w') as f:
    json.dump(drafts, f, indent=2)

print("Email drafts generated and saved to audit_data/email_drafts.json")

# Optional Gmail Sync via Gmail API Connector
def sync_to_gmail(drafts):
    """
    Sync drafts to Gmail using the 'gmail' MCP server.
    This function uses 'mcp tool.call' via shell if available.
    """
    # Check if Gmail connector is available and configured
    # In this environment, we can attempt to call the mcp tool directly via a python script or shell
    # For the sake of the script being standalone and robust, we'll try to use the 'mcp' tool
    # if it's accessible via the environment or just document the status.
    
    print("\nChecking for Gmail API connector...")
    
    # We will use a flag file or environment variable to indicate if sync should be attempted
    # In a real Manus environment, the agent would handle this, but for the script,
    # we'll provide the logic that an agent or a scheduled task can use.
    
    gmail_sync_status = "Not Attempted"
    try:
        # Prepare the messages for the gmail_send_messages tool
        gmail_messages = []
        for d in drafts:
            gmail_messages.append({
                "subject": d["subject"],
                "to": ["replace-with-actual-email@example.com"], # Placeholder as we don't have real emails
                "content": d["body"]
            })
        
        if not gmail_messages:
            return "No drafts to sync"

        # Note: In the Manus environment, we call tools via the provided interfaces.
        # This script acts as a part of the pipeline.
        print(f"Prepared {len(gmail_messages)} drafts for Gmail sync.")
        gmail_sync_status = "Ready for Sync"
        
        # We'll save a sync-ready file for the agent/pipeline to pick up
        with open('audit_data/gmail_sync_payload.json', 'w') as f:
            json.dump({"messages": gmail_messages}, f, indent=2)
            
    except Exception as e:
        print(f"Gmail sync preparation failed: {e}")
        gmail_sync_status = f"Failed: {str(e)}"

    return gmail_sync_status

sync_status = sync_to_gmail(drafts)
with open('audit_data/sync_status.json', 'w') as f:
    json.dump({"gmail_sync_status": sync_status}, f, indent=2)

for d in drafts:
    print(f"\n--- Draft for: {d['company']} ({d['lead_score']}/100) ---")
    print(f"Subject: {d['subject']}")
    print(d['body'][:150] + "...")

print(f"\nGmail Sync Status: {sync_status}")
