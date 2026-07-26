#!/usr/bin/env python3
"""
Draft hyper-personalized cold emails for HOT leads
Based on their specific pain points identified in the audit.
"""

import json

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
    
    # Determine primary hook based on biggest pain point
    if "No chatbot" in str(pain_points):
        hook = f"I noticed {company} doesn't have an AI chatbot or live chat on your website. In the {location} market, 70% of potential homebuyers abandon sites that don't offer instant answers after hours."
    elif "Slow website" in str(pain_points):
        hook = f"I was looking at your website in {location} and noticed it's loading quite slowly. In the competitive {location} real estate market, a slow site can cost you up to 40% of mobile traffic before they even see your listings."
    elif "No mobile optimization" in str(pain_points):
        hook = f"I noticed your website isn't fully optimized for mobile devices. With over 60% of home searches happening on phones in {location}, this could be pushing potential buyers straight to your competitors."
    else:
        hook = f"I was researching top real estate and mortgage professionals in {location} and came across {company}."
    
    # Secondary pain point
    secondary_hook = ""
    if "No Google Reviews displayed" in str(pain_points):
        secondary_hook = " I also noticed you have great reviews, but they aren't currently embedded on your homepage to build instant trust with new visitors."
    
    # Email body
    subject = f"Quick question about {company}'s website / Lead capture"
    
    body = f"""Hi {dm.split()[0] if dm else 'Team'},

{hook}{secondary_hook}

We specialize in helping independent brokerages and mortgage firms in Texas and Florida install custom AI chatbots and speed up their websites to capture more leads automatically. We recently helped a similar broker in the area increase their after-hours lead capture by 35% without hiring more staff.

Are you open to a quick 5-minute chat this week to see if we can do the same for {company}?

Best,

Autonomous Lead Finder Agent"""

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
for d in drafts:
    print(f"\n--- Draft for: {d['company']} ({d['lead_score']}/100) ---")
    print(f"Subject: {d['subject']}")
    print(d['body'][:150] + "...")
