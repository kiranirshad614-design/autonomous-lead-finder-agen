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
warnings.filterwarnings('ignore')

# Websites to audit
leads = [
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
]

def audit_website(lead):
    """Audit a website for pain points."""
    url = lead["url"]
    results = {
        "company": lead["company"],
        "dm": lead["dm"],
        "title": lead["title"],
        "location": lead["location"],
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
        "audit_notes": ""
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
        
        # Check for chatbot/live chat
        chatbot_keywords = ['tawk', 'intercom', 'drift', 'zendesk', 'livechat', 'crisp', 'olark', 'chatbot', 'chat-widget', 'live-chat', 'jivosite', 'tidio', 'comm100', 'freshchat', 'hubspot_chat', 'hubspotconversations', 'zopim', 'smartsupp', 'chatra']
        for kw in chatbot_keywords:
            if kw in html:
                results["has_chatbot"] = True
                results["has_live_chat"] = True
                break
        
        # Check specifically for <script> tags with chat services
        scripts = soup.find_all('script', src=True)
        for script in scripts:
            src = script.get('src', '').lower()
            if any(kw in src for kw in chatbot_keywords):
                results["has_chatbot"] = True
                results["has_live_chat"] = True
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
        
        # Generate pain points
        pain_points = []
        if not results["has_chatbot"]:
            pain_points.append("No live chat or AI chatbot on website - missing 24/7 lead capture opportunity")
        
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
        
        # Summary note
        if pain_points:
            results["audit_notes"] = f"Found {len(pain_points)} pain point(s): {'; '.join(pain_points[:2])}"
        else:
            results["audit_notes"] = "Website appears well-optimized with no major pain points detected"
            
    except Exception as e:
        results["site_reachable"] = False
        results["audit_notes"] = f"Could not reach website: {str(e)[:100]}"
        results["pain_points"] = ["Website unreachable or down - critical business issue"]
    
    return results

# Run audits
all_results = []
for lead in leads:
    print(f"Auditing: {lead['company']}...")
    result = audit_website(lead)
    all_results.append(result)
    print(f"  Pain points found: {len(result['pain_points'])}")
    for pp in result['pain_points']:
        print(f"    - {pp}")

# Save results
with open('audit_data/audit_results.json', 'w') as f:
    json.dump(all_results, f, indent=2)

print(f"\nAudit complete! Results saved for {len(all_results)} websites.")
