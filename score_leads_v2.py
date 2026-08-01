#!/usr/bin/env python3
"""
Lead Scoring Script V2 - Recalibrated for realistic HOT lead identification
HOT Leads = Score > 80

Scoring philosophy: A HOT lead is a business that:
1. Has multiple observable pain points (losing revenue NOW)
2. Is at a growth stage where they'd invest in solutions
3. Has an identifiable, reachable decision maker
4. Operates in a competitive market where digital presence matters
"""

import json

# Load audit results
with open('audit_data/audit_results.json', 'r') as f:
    audit_results = json.load(f)

# Review data from search
review_data = {
    "Florida Homes Realty & Mortgage": {"google_rating": 4.8, "google_count": 309, "platforms": 4},
    "HomeTrust Financing": {"google_rating": 5.0, "google_count": 81, "platforms": 2},
    "Future Home Loans": {"google_rating": 5.0, "google_count": 1000, "platforms": 2},
    "Wholesale Mortgages LLC": {"google_rating": 4.8, "google_count": 150, "platforms": 2},
    "The Orlicki Group": {"google_rating": 5.0, "google_count": 50, "platforms": 1},
    "Pioneer Mortgage Funding": {"google_rating": 4.9, "google_count": 200, "platforms": 1},
    "Matador Lending": {"google_rating": 4.5, "google_count": 30, "platforms": 1},
    "Turn-Key Mortgage Inc.": {"google_rating": 5.0, "google_count": 45, "platforms": 2},
    "Rainmaker Realty": {"google_rating": 4.9, "google_count": 40, "platforms": 3},
    "Texas Premier Mortgage": {"google_rating": 4.9, "google_count": 500, "platforms": 1},
    "First Commerce Financial": {"google_rating": 5.0, "google_count": 200, "platforms": 1},
    "Realty Texas": {"google_rating": 4.7, "google_count": 100, "platforms": 1},
    "Networth Builders": {"google_rating": 5.0, "google_count": 200, "platforms": 3},
    "Mortgage Expert": {"google_rating": 5.0, "google_count": 100, "platforms": 2},
    "SI Real Estate Investments": {"google_rating": 4.7, "google_count": 168, "platforms": 3},
}

def score_lead(audit, reviews):
    score = 0
    reasons = []
    pain_points = audit.get("pain_points", [])
    pain_count = len(pain_points)

    # Estimated business metrics (placeholders - ideally these would come from lead research)
    AVG_DEAL_VALUE = 5000  # Average commission/profit per deal for real estate/mortgage
    MONTHLY_LEAD_VOLUME = 100 # Estimated monthly website visitors / leads
    CONVERSION_RATE_BASELINE = 0.02 # 2% conversion rate baseline (visitors to clients)
    lost_revenue_monthly = 0

    
    # ===== PAIN POINT SEVERITY (max 40 pts) =====
    # No chatbot = DIRECT revenue loss every night
    if any("No 24/7 AI lead capture widget/chatbot" in pp for pp in pain_points):
        score += 18
        reasons.append("No 24/7 AI lead capture widget/chatbot = losing leads 24/7 (CRITICAL)")
        lost_revenue_monthly += MONTHLY_LEAD_VOLUME * CONVERSION_RATE_BASELINE * AVG_DEAL_VALUE * 0.30 # 30% conversion drop

    
    # Slow website = visitors bouncing before seeing offer
    if any("Slow website load time" in pp for pp in pain_points):
        score += 12
        reasons.append("Slow site speed = high bounce rate (CRITICAL)")
        lost_revenue_monthly += MONTHLY_LEAD_VOLUME * CONVERSION_RATE_BASELINE * AVG_DEAL_VALUE * 0.20 # 20% conversion drop

    
    # No mobile optimization = losing majority of traffic
    if any("No mobile optimization" in pp for pp in pain_points):
        score += 10
        reasons.append("No mobile optimization = losing 60%+ traffic (HIGH)")
        lost_revenue_monthly += MONTHLY_LEAD_VOLUME * CONVERSION_RATE_BASELINE * AVG_DEAL_VALUE * 0.25 # 25% conversion drop

    
    # Outdated tech = credibility issue
    if any("Outdated web technology" in pp for pp in pain_points):
        score += 8
        reasons.append("Outdated tech hurting credibility (HIGH)")
    
    # No social media = invisible to younger buyers
    if any("No social media links" in pp for pp in pain_points):
        score += 6
        reasons.append("No social media = invisible to prospects (MED)")
    
    # No Google reviews embedded = no trust signal
    if any("No Google Reviews displayed" in pp for pp in pain_points):
        score += 6
        reasons.append("No reviews on site = trust gap (MED)")
        lost_revenue_monthly += MONTHLY_LEAD_VOLUME * CONVERSION_RATE_BASELINE * AVG_DEAL_VALUE * 0.10 # 10% conversion drop

    
    # Bonus for MULTIPLE pain points (compounding urgency)
    if pain_count >= 4:
        score += 5
        reasons.append("4+ pain points = compounding urgency")
    elif pain_count >= 3:
        score += 3
        reasons.append("3 pain points = clear need")
    
    # ===== REVIEW/REPUTATION FACTOR (max 15 pts) =====
    if reviews:
        rating = reviews.get("google_rating", 5.0)
        count = reviews.get("google_count", 0)
        platforms = reviews.get("platforms", 0)
        
        # Small review count but good rating = they need MORE reviews managed
        if count < 100 and rating >= 4.5:
            score += 8
            reasons.append(f"Only {count} reviews - needs review automation")
        elif count < 50:
            score += 10
            reasons.append(f"Very few reviews ({count}) - major reputation gap")
        
        # Rating below 4.8 = room for improvement pitch
        if rating < 4.8 and rating >= 4.5:
            score += 5
            reasons.append(f"Rating {rating} - can improve with review mgmt")
        elif rating < 4.5:
            score += 10
            reasons.append(f"Rating {rating} - reputation needs fixing")
        
        # Few platforms = they're not capturing reviews everywhere
        if platforms <= 2:
            score += 5
            reasons.append(f"Only {platforms} review platforms - leaving reviews on table")
    
    # ===== BUSINESS STAGE / INVESTMENT READINESS (max 25 pts) =====
    # Independent businesses are more likely to adopt new solutions
    score += 12
    reasons.append("Independent business - decision agility")
    
    # If they have a website but it's basic/slow = ready to invest
    if audit.get("site_reachable", False):
        score += 8
        reasons.append("Has existing website - ready for upgrade")
    
    # Load time issues indicate they're using basic hosting
    if audit.get("load_time_ms", 0) > 3500:
        score += 5
        reasons.append("Slow infrastructure - needs modern solution")
    
    # ===== DECISION MAKER ACCESSIBILITY (max 20 pts) =====
    title = audit.get("title", "").lower()
    if any(kw in title for kw in ["founder", "ceo", "owner", "president", "broker owner"]):
        score += 10
        reasons.append("Direct decision maker identified")
    
    # Active online presence means they're reachable
    if audit.get("site_reachable", False):
        score += 5
        reasons.append("Active online = reachable")
    
    # Real estate/mortgage in TX/FL = competitive market = urgency
    location = audit.get("location", "")
    if any(st in location for st in ["TX", "FL", "Texas", "Florida"]):
        score += 5
        reasons.append("Competitive TX/FL market = urgency")
    
    # New automation gap pain points
    if any("No instant booking calendar" in pp for pp in pain_points):
        score += 15 # High impact
        reasons.append("No instant booking calendar = lost appointments (CRITICAL)")
        lost_revenue_monthly += MONTHLY_LEAD_VOLUME * CONVERSION_RATE_BASELINE * AVG_DEAL_VALUE * 0.25 # 25% conversion drop

    if any("No automated lead confirmation" in pp for pp in pain_points):
        score += 10 # Medium impact
        reasons.append("No automated lead confirmation = leads go cold (HIGH)")
        lost_revenue_monthly += MONTHLY_LEAD_VOLUME * CONVERSION_RATE_BASELINE * AVG_DEAL_VALUE * 0.15 # 15% conversion drop

    # Cap at 100
    score = min(score, 100)
    
    return score, reasons, round(lost_revenue_monthly)



# Score all leads
hot_leads = []
all_scored = []

for audit in audit_results:
    company = audit["company"]
    reviews = review_data.get(company, None)
    score, reasons, lost_revenue = score_lead(audit, reviews)
    
    scored_lead = {
        "estimated_monthly_lost_revenue": lost_revenue,
        "company": company,
        "dm": audit.get("dm_extracted") or audit["dm"],
        "title": audit["title"],
        "location": audit["location"],
        "email": audit.get("email"),
        "website": audit["url"],
        "linkedin_url": audit.get("linkedin_url"),
        "lead_score": score,
        "pain_points": audit["pain_points"],
        "scoring_reasons": reasons,
        "load_time_ms": audit["load_time_ms"],
        "has_chatbot": audit["has_chatbot"],
        "has_booking_calendar": audit.get("has_booking_calendar", False),
        "has_auto_responder": audit.get("has_auto_responder", False),
        "is_hot": score > 80,
        "google_review_data": reviews
    }
    
    all_scored.append(scored_lead)
    if score > 80:
        hot_leads.append(scored_lead)
    print(f"[{score:3d}/100] {company} - {audit['dm']} ({audit['location']}) {'*** HOT ***' if score > 80 else ''}")
    for r in reasons:
        print(f"          {r}")

# Sort hot leads by score
hot_leads.sort(key=lambda x: x["lead_score"], reverse=True)

# Save results
with open('audit_data/scored_leads.json', 'w') as f:
    json.dump({"hot_leads": hot_leads, "all_scored": all_scored}, f, indent=2)

print(f"\n{'='*60}")
print(f"Total leads scored: {len(all_scored)}")
print(f"HOT leads (score > 80): {len(hot_leads)}")
print(f"{'='*60}")
print(f"\nHOT LEADS:")
for i, hl in enumerate(hot_leads, 1):
    print(f"  {i}. [{hl['lead_score']}/100] {hl['company']} - {hl['dm']}")
