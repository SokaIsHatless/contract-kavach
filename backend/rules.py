"""Red-flag rules engine. Hardcoded against Indian Emigration Act + ILO frameworks."""

import re

INR_FEE_CAP = 30000  # Indian Emigration Act recruiter fee ceiling

# Rough destination-country monthly minimum wage in INR (approximations for demo)
DESTINATION_MIN_WAGE_INR = {
    "UAE": 25000,
    "Saudi Arabia": 22000,
    "Qatar": 22000,
    "Kuwait": 24000,
    "Oman": 21000,
    "Bahrain": 23000,
}

CURRENCY_TO_INR = {  # rough, for demo only
    "INR": 1, "AED": 22.5, "SAR": 22.0, "QAR": 22.5,
    "KWD": 270, "OMR": 215, "BHD": 220, "USD": 83,
}

CANONICAL_COUNTRY = {
    "United Arab Emirates": "UAE",
    "Kingdom of Saudi Arabia": "Saudi Arabia",
    "KSA": "Saudi Arabia",
    "State of Qatar": "Qatar",
    "Sultanate of Oman": "Oman",
    "Kingdom of Bahrain": "Bahrain",
    "State of Kuwait": "Kuwait",
}


def to_inr(amount, currency):
    return amount * CURRENCY_TO_INR.get(currency, 1)


def evaluate(contract: dict) -> list:
    flags = []

    # RF01: Recruitment fee exceeds legal cap
    fee = contract.get("recruitment_fee_paid")
    if fee:
        fee_inr = to_inr(fee["amount"], fee["currency"])
        if fee_inr > INR_FEE_CAP:
            flags.append({
                "rule_id": "RF01",
                "severity": "critical",
                "title_en": "Recruitment fee exceeds legal cap of ₹30,000",
                "title_hi": "भर्ती शुल्क कानूनी सीमा ₹30,000 से अधिक है",
                "explanation_en": f"You paid approximately ₹{int(fee_inr):,}. Indian law caps recruiter fees at ₹30,000. The excess is recoverable.",
                "explanation_hi": f"आपने लगभग ₹{int(fee_inr):,} दिया। भारतीय कानून के अनुसार भर्ती शुल्क ₹30,000 से अधिक नहीं हो सकता। अतिरिक्त राशि वापस मांगी जा सकती है।",
                "evidence_page": 1,
                "evidence_quote": "",
            })

    # RF02: Passport surrender
    if contract.get("passport_handling") == "employer_holds":
        flags.append({
            "rule_id": "RF02",
            "severity": "critical",
            "title_en": "Employer holding your passport is illegal",
            "title_hi": "नियोक्ता द्वारा आपका पासपोर्ट रखना अवैध है",
            "explanation_en": "Indian and ILO law forbid passport confiscation. This is a modern slavery indicator. Refuse this clause.",
            "explanation_hi": "भारतीय और अंतर्राष्ट्रीय कानून के तहत पासपोर्ट जब्त करना मना है। यह आधुनिक बंधुआ मजदूरी का संकेत है। इस शर्त को मानने से इनकार करें।",
            "evidence_page": 1,
            "evidence_quote": "",
        })

    # RF03: Wage below destination minimum
    wage = contract.get("wage")
    dest = CANONICAL_COUNTRY.get(contract.get("destination_country"), contract.get("destination_country"))
    if wage and dest in DESTINATION_MIN_WAGE_INR:
        monthly_inr = to_inr(wage["amount"], wage["currency"])
        if wage.get("period") == "daily":
            monthly_inr *= 26
        if monthly_inr < DESTINATION_MIN_WAGE_INR[dest]:
            flags.append({
                "rule_id": "RF03",
                "severity": "critical",
                "title_en": f"Wage below {dest} minimum standard",
                "title_hi": f"वेतन {dest} के न्यूनतम मानक से कम",
                "explanation_en": f"Promised wage (~₹{int(monthly_inr):,}/month) is below typical {dest} minimums.",
                "explanation_hi": f"वादा किया गया वेतन (लगभग ₹{int(monthly_inr):,}/माह) {dest} के सामान्य न्यूनतम वेतन से कम है।",
                "evidence_page": 1,
                "evidence_quote": "",
            })

    # RF04: Excessive working hours
    hrs = contract.get("working_hours_per_day")
    days = contract.get("working_days_per_week") or 6
    if hrs and (hrs > 10 or hrs * days > 60):
        flags.append({
            "rule_id": "RF04",
            "severity": "high",
            "title_en": "Working hours violate ILO standards",
            "title_hi": "कार्य घंटे ILO मानकों का उल्लंघन करते हैं",
            "explanation_en": f"Contract specifies {hrs} hours/day, {days} days/week. ILO standard is max 48 hrs/week.",
            "explanation_hi": f"अनुबंध में {hrs} घंटे/दिन, {days} दिन/सप्ताह है। ILO मानक अधिकतम 48 घंटे/सप्ताह है।",
            "evidence_page": 1,
            "evidence_quote": "",
        })

    # RF05: Heavy deductions
    deductions = contract.get("deductions", [])
    for d in deductions:
        amt_str = str(d.get("amount_or_percent", ""))
        if "%" in amt_str:
            m = re.match(r"(\d+(?:\.\d+)?)\s*%", amt_str)
            if m:
                pct = float(m.group(1))
                if pct > 25:
                    flags.append({
                        "rule_id": "RF05",
                        "severity": "high",
                        "title_en": f"Heavy {d['type']} deduction ({amt_str})",
                        "title_hi": f"{d['type']} में भारी कटौती ({amt_str})",
                        "explanation_en": "Deductions over 25% of wage are a common wage-theft pattern.",
                        "explanation_hi": "वेतन से 25% से अधिक कटौती सामान्य वेतन-चोरी का तरीका है।",
                        "evidence_page": d.get("page", 1),
                        "evidence_quote": "",
                    })

    # RF06: Asymmetric termination
    if contract.get("termination") == "employer_only":
        flags.append({
            "rule_id": "RF06",
            "severity": "high",
            "title_en": "Only employer can terminate the contract",
            "title_hi": "केवल नियोक्ता ही अनुबंध समाप्त कर सकता है",
            "explanation_en": "Workers should have the same right to exit. This locks you in.",
            "explanation_hi": "कर्मचारी को भी अनुबंध छोड़ने का समान अधिकार होना चाहिए। यह आपको फंसा देता है।",
            "evidence_page": 1,
            "evidence_quote": "",
        })

    # RF07: No grievance mechanism
    if not contract.get("grievance_mechanism"):
        flags.append({
            "rule_id": "RF07",
            "severity": "medium",
            "title_en": "No grievance mechanism specified",
            "title_hi": "कोई शिकायत प्रक्रिया निर्दिष्ट नहीं",
            "explanation_en": "If something goes wrong, the contract gives no path to complain. Insist on adding the Indian Embassy / MEA complaint route.",
            "explanation_hi": "अगर कुछ गलत होता है, तो शिकायत का कोई रास्ता नहीं है। भारतीय दूतावास/MEA शिकायत मार्ग जोड़ने पर जोर दें।",
            "evidence_page": 1,
            "evidence_quote": "",
        })

    # RF08: Kafala-style sponsor lock
    if contract.get("sponsor_change_allowed") is False:
        flags.append({
            "rule_id": "RF08",
            "severity": "critical",
            "title_en": "You cannot change employer (kafala lock-in)",
            "title_hi": "आप नियोक्ता नहीं बदल सकते (कफाला बंधन)",
            "explanation_en": "Inability to change sponsors is a defining feature of kafala bondage. Several Gulf states have reformed this — verify current law.",
            "explanation_hi": "नियोक्ता बदलने में असमर्थता कफाला बंधुआ-मजदूरी की पहचान है। कई खाड़ी देशों ने यह नियम बदला है — वर्तमान कानून जांचें।",
            "evidence_page": 1,
            "evidence_quote": "",
        })

    # Attach evidence quotes from key_clauses where possible
    critical_clauses = [c for c in contract.get("key_clauses", []) if c.get("concern_level") == "critical"]
    for i, flag in enumerate(flags):
        if i < len(critical_clauses) and not flag["evidence_quote"]:
            flag["evidence_quote"] = critical_clauses[i]["text"]
            flag["evidence_page"] = critical_clauses[i]["page"]

    severity_order = {"critical": 0, "high": 1, "medium": 2}
    flags.sort(key=lambda f: severity_order[f["severity"]])
    return flags