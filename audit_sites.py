#!/usr/bin/env python3
"""
Website Audit Script - Checks for pain points in lead websites
1. Missing AI chatbot / Live chat
2. Outdated website design indicators
3. Slow loading (via response headers / size)
"""

import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import json
import warnings
import os
warnings.filterwarnings('ignore')

# Path to deduplication file
SEEN_LEADS_FILE = 'seen_leads.json'

def load_seen_leads():
    if os.path.exists(SEEN_LEADS_FILE):
        with open(SEEN_LEADS_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_seen_leads(seen_leads):
    with open(SEEN_LEADS_FILE, 'w') as f:
        json.dump(list(seen_leads), f, indent=2)

# Websites to audit
all_leads = [
    {"company": "Florida Homes Realty & Mortgage", "url": "https://www.joinfhrm.com/", "dm": "James Angelo", "title": "Founder, CEO, Broker", "location": "Jacksonville, FL"},
    {"company": "HomeTrust Financing", "url": "https://hometrustfinancing.com/", "dm": "Chris Cavazos", "title": "Mortgage Broker/Owner", "location": "Sugar Land, TX"},
    {"company": "Future Home Loans", "url": "https://future.loans/", "dm": "Robert Lynn", "title": "CEO Founder", "location": "Jacksonville Beach, FL"},
    {"company": "Wholesale Mortgages LLC", "url": "https://www.findeasymortgages.com/", "dm": "Javier Satizabal", "title": "Founder, CEO", "location": "Tampa, FL"},
    {"company": "The Orlicki Group", "url": "https://orlickigroup.com/", "dm": "Oliver Orlicki", "title": "Founder, Mortgage Loan Originator", "location": "Tampa, FL"},
    {"company": "Pioneer Mortgage Funding", "url": "https://yourkey.com/", "dm": "Gerald Cugno", "title": "President and Owner", "location": "Florida"},
    {"company": "Matador Lending", "url": "https://www.matadorlending.com/", "dm": "Founding Team", "title": "Mortgage Broker Owner", "location": "Houston, TX"},
    {"company": "Turn-Key Mortgage Inc.", "url": "https://turnkeymortgage.net/", "dm": "Jennifer Brown", "title": "Mortgage Broker/Owner", "location": "Houston, TX"},
    {"company": "Rainmaker Realty", "url": "https://www.rainmakerrealty.com/", "dm": "Jeanne", "title": "Founder, Owner", "location": "San Antonio, TX"},
    {"company": "Texas Premier Mortgage", "url": "https://www.txpremiermortgage.com/", "dm": "Owner", "title": "Owner", "location": "Houston, TX"},
    {"company": "First Commerce Financial", "url": "https://www.firstcommercefinancial.com/", "dm": "Kirk Chivas", "title": "Co-Founder", "location": "Jacksonville, FL"},
    {"company": "Realty Texas", "url": "https://www.realtytexas.com/", "dm": "Jack Stapleton", "title": "Co-Founder, Broker", "location": "Texas"},
    {"company": "Networth Builders", "url": "https://networthbuilders.com/", "dm": "Wale Lawal", "title": "Founder", "location": "Houston, TX"},
    {"company": "Mortgage Expert", "url": "https://mortgageexpert.com/", "dm": "Shahram Sondi", "title": "Broker-Owner", "location": "Orlando, FL"},
    {"company": "SI Real Estate Investments", "url": "https://www.sirealestateinvestments.com/", "dm": "Nibal Elsaadi", "title": "Broker Associate", "location": "Tampa, FL"},
    {"company": "Momentum Realty", "url": "https://movewithmomentum.com/", "dm": "Jon Brooks", "title": "Co-Founder", "location": "Jacksonville, FL"},
    {"company": "Champions Mortgage", "url": "https://championsmortgageteam.com/", "dm": "Joel Mathew", "title": "President/CEO", "location": "Houston, TX"},
    {"company": "Arnaiz Mortgage", "url": "https://arnaizmortgage.com/", "dm": "Tyler Arnaiz", "title": "Owner", "location": "Austin, TX"},
    {"company": "Vreeland Real Estate", "url": "https://vreelandre.com/", "dm": "Jordan Vreeland", "title": "Founder", "location": "Tampa, FL"},
    {"company": "LoKation Real Estate", "url": "https://joinlokation.com/", "dm": "Nathan Klutznick", "title": "CEO", "location": "Florida"},
    {"company": "London Foster", "url": "https://www.londonfoster.com/", "dm": "Bobby Mahallati", "title": "Broker & Owner", "location": "Miami, FL", "email": "broker@londonfoster.net"},
    {"company": "Balistreri Real Estate", "url": "https://www.balistreri.com/", "dm": "Jim Balistreri", "title": "CEO/Owner", "location": "Fort Lauderdale, FL", "email": "jim@balistreri.com"},
    {"company": "The Keyes Company", "url": "https://www.keyes.com/", "dm": "Mike Pappas", "title": "CEO", "location": "Miami, FL", "email": "mikepappas@keyes.com"},
    {"company": "United Real Estate DFW Properties", "url": "http://brendacole.unitedrealestatedfwproperties.com/", "dm": "Brenda Cole", "title": "Broker/Owner-Partner", "location": "Grapevine, TX", "email": "BrendaColeDFW@gmail.com"},
    {"company": "The Agency Dallas", "url": "https://txrootsglobalre.com/damon-williamson/", "dm": "Damon Williamson", "title": "Broker/Owner", "location": "Dallas, TX", "email": "damon.williamson@theagencyre.com"},
    {"company": "The Mortgage Brokers, LLC", "url": "https://hellomortgagebrokers.com/", "dm": "Gabe Garza", "title": "Mortgage Broker/Owner", "location": "Frisco, TX", "email": "gabe@hellomortgagebrokers.com"},
    {"company": "Spyglass Realty", "url": "https://www.spyglassrealty.com/", "dm": "Ryan Rodenbeck", "title": "Owner", "location": "Austin, TX", "email": "ryan@spyglassrealty.com"},
    {"company": "Mortgage Expert", "url": "https://mortgageexpert.com/", "dm": "Shahram Sondi", "title": "Broker-Owner", "location": "Orlando, FL", "email": "shahram@mortgageexpert.com"},
]

def audit_website(lead):
    """Audit a website for pain points."""
    url = lead["url"]
    results = {
        "company": lead["company"],
        "dm": lead["dm"],
        "title": lead["title"],
        "location": lead["location"],
        "email": lead.get("email"),
        "url": url,
        "has_chatbot": False,
        "has_live_chat": False,
        "site_reachable": False,
        "load_time_ms": 0,
        "page_size_kb": 0,
        "has_meta_viewport": False,
        "has_mobile_optimization": False,
        "uses_outdated_tech": False,
        "outdated_tech_details": [],
        "ssl": False,
        "has_social_links": False,
        "has_google_reviews_embed": False,
        "pain_points": [],
        "audit_notes": "",
        "has_booking_calendar": False,
        "has_auto_responder": False,
        "linkedin_url": None,
        "dm_extracted": None
    }
    
    try:
        # Check site speed and reachability
        start = time.time()
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=15, verify=False, allow_redirects=True)
        load_time = (time.time() - start) * 1000
        results["load_time_ms"] = round(load_time)
        results["page_size_kb"] = round(len(response.content) / 1024, 1)
        results["site_reachable"] = True
        results["ssl"] = url.startswith("https")
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        html = response.text.lower()
        
        # Check for chatbot/live chat and auto-responders
        chatbot_keywords = ['tawk', 'intercom', 'drift', 'zendesk', 'livechat', 'crisp', 'olark', 'chatbot', 'chat-widget', 'live-chat', 'jivosite', 'tidio', 'comm100', 'freshchat', 'hubspot_chat', 'hubspotconversations', 'zopim', 'smartsupp', 'chatra']
        for kw in chatbot_keywords:
            if kw in html:
                results["has_chatbot"] = True
                results["has_live_chat"] = True
                results["has_auto_responder"] = True # Assume if chatbot, then auto-responder
                break
        
        # Check specifically for <script> tags with chat services
        scripts = soup.find_all('script', src=True)
        for script in scripts:
            src = script.get('src', '').lower()
            if any(kw in src for kw in chatbot_keywords):
                results["has_chatbot"] = True
                results["has_live_chat"] = True
                results["has_auto_responder"] = True # Assume if chatbot, then auto-responder
                break
        
        # Check for mobile viewport
        meta_viewport = soup.find('meta', attrs={'name': 'viewport'})
        results["has_meta_viewport"] = meta_viewport is not None
        
        # Check mobile responsiveness indicators
        if 'mobile' in html or 'responsive' in html or 'bootstrap' in html or 'tailwind' in html:
            results["has_mobile_optimization"] = True
        
        # Check for outdated tech
        if 'table' in html and '<table' in response.text:
            tables = soup.find_all('table')
            if len(tables) > 3:
                results["uses_outdated_tech"] = True
                results["outdated_tech_details"].append("Uses tables for layout")
        
        if '<font' in response.text.lower():
            results["uses_outdated_tech"] = True
            results["outdated_tech_details"].append("Uses deprecated <font> tags")
        
        if 'javascript:void(0)' in html:
            results["uses_outdated_tech"] = True
            results["outdated_tech_details"].append("Uses javascript:void(0) links")
        
        # Check for social media links
        social_kw = ['facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com', 'tiktok.com', 'youtube.com']
        for skw in social_kw:
            if skw in html:
                results["has_social_links"] = True
                break
        
        # Check for Google Reviews embed
        review_kw = ['google.com/maps/reviews', 'google-review', 'reviews.google.com', 'trustindex']
        for rkw in review_kw:
            if rkw in html:
                results["has_google_reviews_embed"] = True
                break
        
        # Check for booking calendars
        booking_calendar_keywords = ["calendly.com", "acuityscheduling.com", "secure.scheduleonce.com", "honeybook.com/widget/", "setmore.com", "youcanbook.me", "booksteam.com", "appointy.com", "timetrade.com", "vcita.com/scheduler", "simplybook.me", "bookingpage.com", "schedule.oncehub.com", "gohighlevel.com/widget"]
        for kw in booking_calendar_keywords:
            if kw in html:
                results["has_booking_calendar"] = True
                break

        # Extract LinkedIn URLs
        linkedin_patterns = [
            r'https?://(?:www\.)?linkedin\.com/in/[\w\-\%]+',
            r'https?://(?:www\.)?linkedin\.com/company/[\w\-\%]+'
        ]
        for pattern in linkedin_patterns:
            matches = re.findall(pattern, response.text)
            if matches:
                results["linkedin_url"] = matches[0]
                break
        
        # Extract Decision Maker (heuristic-based)
        dm_patterns = [
            r'(?:Founder|CEO|Owner|President|Broker|Director):\s*([A-Z][a-z]+ [A-Z][a-z]+)',
            r'([A-Z][a-z]+ [A-Z][a-z]+)\s*(?:Founder|CEO|Owner|President|Broker|Director)'
        ]
        for pattern in dm_patterns:
            matches = re.findall(pattern, response.text)
            if matches:
                results["dm_extracted"] = matches[0]
                break
        
        # Prioritize provided DM, fallback to extraction
        results["dm_extracted"] = lead.get("dm") or results.get("dm_extracted")

        # Generate pain points
        pain_points = []
        if not results["has_chatbot"]:
            pain_points.append("No 24/7 AI lead capture widget/chatbot - missing instant engagement and lead qualification")
        
        if not results["has_booking_calendar"]:
            pain_points.append("No instant booking calendar (Calendly, Acuity, GHL) - friction in scheduling and lost appointments")

        if not results["has_auto_responder"]:
            pain_points.append("No automated lead confirmation / instant auto-responder - leads go cold waiting for a reply")
        
        if not results["has_meta_viewport"] and not results["has_mobile_optimization"]:
            pain_points.append("No mobile optimization detected - poor experience for mobile visitors")
        
        if results["load_time_ms"] > 4000:
            pain_points.append(f"Slow website load time ({results['load_time_ms']}ms) - losing impatient leads")
        elif results["load_time_ms"] > 2500:
            pain_points.append(f"Moderate load time ({results['load_time_ms']}ms) - could be faster for better UX")
        
        if results["page_size_kb"] > 3000:
            pain_points.append(f"Very large page size ({results['page_size_kb']}KB) - may impact load speed on mobile")
        
        if results["uses_outdated_tech"]:
            pain_points.append(f"Outdated web technology: {', '.join(results['outdated_tech_details'])}")
        
        if not results["has_social_links"]:
            pain_points.append("No social media links found - weak digital presence")
        
        if not results["has_google_reviews_embed"]:
            pain_points.append("No Google Reviews displayed on website - missing trust signals")
        
        results["pain_points"] = pain_points

        # Update audit notes with new automation gaps
        automation_gaps = []
        if not results["has_chatbot"]:
            automation_gaps.append("No AI Chatbot")
        if not results["has_booking_calendar"]:
            automation_gaps.append("No Booking Calendar")
        if not results["has_auto_responder"]:
            automation_gaps.append("No Auto-Responder")

        if automation_gaps:
            results["audit_notes"] += f"; Automation Gaps: {', '.join(automation_gaps)}"
        
        # Summary note
        if pain_points:
            results["audit_notes"] = f"Found {len(pain_points)} pain point(s): {'; '.join(pain_points[:2])}"
            if automation_gaps:
                results["audit_notes"] += f"; Automation Gaps: {', '.join(automation_gaps)}"
        else:
            results["audit_notes"] = "Website appears well-optimized with no major pain points detected"
            
    except Exception as e:
        results["site_reachable"] = False
        results["audit_notes"] = f"Could not reach website: {str(e)[:100]}"
        results["pain_points"] = ["Website unreachable or down - critical business issue"]
    
    return results

# Run audits
seen_leads = load_seen_leads()
all_results = []
new_leads_count = 0

for lead in all_leads:
    domain = lead['url'].split('//')[-1].split('/')[0].replace('www.', '')
    if domain in seen_leads:
        print(f"Skipping {lead['company']} (already processed).")
        continue
    
    print(f"Auditing: {lead['company']}...")
    result = audit_website(lead)
    all_results.append(result)
    seen_leads.add(domain)
    new_leads_count += 1
    print(f"  Pain points found: {len(result['pain_points'])}")
    for pp in result['pain_points']:
        print(f"    - {pp}")

# Save results
if all_results:
    with open('audit_data/audit_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    save_seen_leads(seen_leads)
    print(f"\nAudit complete! Results saved for {new_leads_count} new websites.")
else:
    print("\nNo new leads to audit.")
