"""Generate 3 mock Gulf migrant worker contracts as PDFs. Dev-only script."""

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT

OUT = Path(__file__).parent / "mock_contracts"
OUT.mkdir(exist_ok=True)

W, H = A4

styles = getSampleStyleSheet()

def style(name="Normal", **kw):
    base = styles[name]
    return ParagraphStyle(name + str(id(kw)), parent=base, **kw)

HEADING = style("Heading1", fontSize=13, textColor=colors.HexColor("#1a3c6e"),
                spaceAfter=4, alignment=TA_CENTER)
SUBHEAD = style("Heading2", fontSize=10, textColor=colors.HexColor("#1a3c6e"),
                spaceBefore=10, spaceAfter=4)
BODY    = style("Normal", fontSize=9, leading=14, alignment=TA_JUSTIFY)
SMALL   = style("Normal", fontSize=8, leading=12, textColor=colors.HexColor("#555555"))
CENTER  = style("Normal", fontSize=9, alignment=TA_CENTER)
BOLD    = style("Normal", fontSize=9, leading=14, fontName="Helvetica-Bold")
RIGHT   = style("Normal", fontSize=8, alignment=TA_RIGHT, textColor=colors.grey)


def hr():
    return HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#1a3c6e"),
                      spaceAfter=6, spaceBefore=6)


def letterhead(company, address, ref, date):
    return [
        Paragraph(company.upper(), HEADING),
        Paragraph(address, CENTER),
        hr(),
        Paragraph(f"Ref: {ref} &nbsp;&nbsp;&nbsp; Date: {date}", RIGHT),
        Spacer(1, 0.3*cm),
        Paragraph("EMPLOYMENT CONTRACT FOR OVERSEAS WORKERS", style("Heading2",
            fontSize=11, alignment=TA_CENTER, textColor=colors.HexColor("#1a3c6e"))),
        hr(),
        Spacer(1, 0.2*cm),
    ]


def parties_section(employer, worker, nationality, destination):
    return [
        Paragraph("PARTIES", SUBHEAD),
        Paragraph(
            f"This Employment Contract is entered into <b>between</b>:<br/>"
            f"<b>Employer:</b> {employer}<br/>"
            f"<b>Employee:</b> {worker}, Nationality: {nationality}<br/>"
            f"<b>Place of Work:</b> {destination}",
            BODY,
        ),
        Spacer(1, 0.3*cm),
    ]


def clause(num, title, text):
    return [
        Paragraph(f"{num}. {title.upper()}", SUBHEAD),
        Paragraph(text, BODY),
        Spacer(1, 0.2*cm),
    ]


def signature_block(employer_name, worker_name):
    data = [
        ["EMPLOYER", "", "EMPLOYEE"],
        ["", "", ""],
        ["", "", ""],
        ["_______________________", "", "_______________________"],
        [employer_name, "", worker_name],
        ["Date: _______________", "", "Date: _______________"],
    ]
    t = Table(data, colWidths=[6*cm, 3*cm, 6*cm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,0), (-1,0), [colors.HexColor("#e8eef7")]),
        ("ROWHEIGHT", (0,1), (0,2), 18),
    ]))
    return [Spacer(1, 0.8*cm), Paragraph("SIGNATURES", SUBHEAD), t]


# ─────────────────────────────────────────────
# Contract A — worst_case.pdf
# ─────────────────────────────────────────────
def make_worst_case():
    doc = SimpleDocTemplate(str(OUT / "worst_case.pdf"), pagesize=A4,
                            leftMargin=2.5*cm, rightMargin=2.5*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    story = []
    story += letterhead(
        "Al Manara Manpower Services LLC",
        "P.O. Box 41207, Dubai, United Arab Emirates | Tel: +971-4-XXX-XXXX",
        "AMM/2024/DXB/4471", "15 January 2024",
    )
    story += parties_section(
        "Al Manara Domestic Services LLC, Dubai, UAE",
        "Rekha Devi", "Indian", "Dubai, UAE",
    )
    story += clause("1", "Nature of Work",
        "The Employee is engaged as a <b>Domestic Worker</b> (household helper, cook, and cleaner) "
        "at the private residence of the Employer's client in Dubai, UAE. The Employee shall perform "
        "all duties as directed by the Employer or the client household.")
    story += clause("2", "Wages",
        "The Employee shall receive a monthly wage of <b>AED 800 (Eight Hundred UAE Dirhams)</b> "
        "payable on the last working day of each calendar month. Wages shall be paid in cash or "
        "by bank transfer at the sole discretion of the Employer. No overtime compensation applies "
        "to domestic workers under this contract.")
    story += clause("3", "Working Hours",
        "The Employee agrees to work <b>fourteen (14) hours per day, seven (7) days per week</b> "
        "including all public holidays. The Employee acknowledges that the nature of domestic work "
        "requires availability at all times within the household and waives any claim to rest days "
        "during the contract period.")
    story += clause("4", "Deductions",
        "The following deductions shall be made from the Employee's monthly wage:<br/>"
        "• Food and Lodging Accommodation: <b>35% of monthly wage (AED 280)</b><br/>"
        "• Uniform maintenance: AED 50 per month<br/>"
        "The remaining net wage payable shall be AED 470 per month.")
    story += clause("5", "Termination",
        "This contract may be terminated at any time and without notice by <b>the Employer only</b>. "
        "The Employee shall have no right to unilaterally terminate this contract before its expiry "
        "date of 24 months. Any early departure by the Employee shall result in full forfeiture of "
        "all accrued wages and a penalty equivalent to three months' salary payable to the Employer.")
    story += clause("6", "Passport and Documents",
        "For the purpose of <b>safekeeping and administrative convenience</b>, the Employee agrees "
        "to surrender their passport and all travel documents to the Employer upon arrival in Dubai. "
        "Documents shall be held by the Employer for the duration of the contract and returned only "
        "upon formal termination by the Employer.")
    story += clause("7", "Recruitment Fee",
        "The Employee acknowledges having paid a recruitment/placement fee of <b>AED 4,500 "
        "(Four Thousand Five Hundred UAE Dirhams)</b> to the recruiting agent in India prior to "
        "departure. This fee is non-refundable under all circumstances.")
    story += clause("8", "Sponsor Change",
        "The Employee shall not seek transfer of sponsorship or change of employer under any "
        "circumstances during the contract period. Any attempt to change sponsors shall be "
        "considered a breach of contract and will result in immediate deportation proceedings.")
    story += signature_block("Al Manara Manpower Services LLC", "Rekha Devi")
    doc.build(story)


# ─────────────────────────────────────────────
# Contract B — sneaky.pdf
# ─────────────────────────────────────────────
def make_sneaky():
    doc = SimpleDocTemplate(str(OUT / "sneaky.pdf"), pagesize=A4,
                            leftMargin=2.5*cm, rightMargin=2.5*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    story = []
    # Page 1 — looks fair
    story += letterhead(
        "Gulf Star Recruitment Pvt Ltd",
        "Office 14, Al Olaya District, Riyadh, Kingdom of Saudi Arabia | CR: 1010XXXXXX",
        "GSR/2024/RUH/0892", "3 March 2024",
    )
    story += parties_section(
        "Riyadh National Construction Co. Ltd, Riyadh, KSA",
        "Mohammed Arif Khan", "Indian", "Riyadh, Kingdom of Saudi Arabia",
    )
    story += clause("1", "Nature of Work",
        "The Employee is engaged as a <b>Construction Labourer / Shuttering Carpenter</b> at "
        "various project sites operated by the Employer in Riyadh and surrounding regions. "
        "The Employee shall comply with all site safety regulations and the Employer's code of conduct.")
    story += clause("2", "Wages",
        "The Employee shall receive a basic monthly salary of <b>SAR 1,500 (One Thousand Five "
        "Hundred Saudi Riyals)</b> plus a site attendance allowance of SAR 200/month, payable "
        "via WPS (Wage Protection System) on or before the 10th of the following month.")
    story += clause("3", "Working Hours",
        "Normal working hours are <b>10 hours per day, 6 days per week</b> (Sunday to Friday). "
        "Overtime beyond 10 hours in any single day shall be compensated at 1.5× the basic hourly rate. "
        "Weekly rest day is Saturday.")
    story += clause("4", "Leave and Benefits",
        "The Employee is entitled to 21 days of paid annual leave after completion of one year "
        "of continuous service. The Employer shall provide return air tickets to India once per "
        "contract cycle of 24 months. Accommodation in labour camp is provided free of charge.")
    story += [
        Spacer(1, 0.4*cm),
        Paragraph("— continued on next page —", CENTER),
        Spacer(1, 20*cm),  # force page break
    ]

    # Page 2 — buries the bad clauses
    story += [
        Paragraph("Gulf Star Recruitment Pvt Ltd — Employment Contract (continued)", SMALL),
        hr(),
        Spacer(1, 0.3*cm),
    ]
    story += clause("5", "Deductions and Advances",
        "The Employer reserves the right to recover any salary advances at a rate of up to "
        "20% per month from the Employee's wages. Administrative processing fees of SAR 150/month "
        "shall apply for the first 12 months of employment.")
    story += clause("6", "Passport and Identity Documents",
        "In accordance with standard practice for expatriate labour management, <b>the Employee "
        "hereby irrevocably authorises the Employer to retain the Employee's passport and Iqama "
        "(residency permit)</b> for administrative and legal compliance purposes throughout the "
        "duration of this contract. The Employee waives all rights to demand return of these "
        "documents prior to formal contract conclusion.")
    story += clause("7", "Termination",
        "This contract shall be terminable at will by <b>the Employer</b> with seven (7) days' "
        "written notice or payment in lieu thereof. The Employee may not resign or abandon the "
        "workplace without the Employer's written consent. Unauthorised absence of more than "
        "three days shall be treated as automatic resignation, forfeiting all end-of-service benefits.")
    story += clause("8", "Sponsor Transfer",
        "Transfer of the Employee's sponsorship (Kafala) to any other employer within the "
        "Kingdom is <b>strictly prohibited</b> without the written approval of the Employer and "
        "the relevant government authority. The Employer's approval may be withheld at absolute discretion.")
    story += clause("9", "Dispute Resolution",
        "Any dispute arising from this contract shall be subject to the exclusive jurisdiction "
        "of the courts of Riyadh, KSA. The Employee expressly waives any right to seek recourse "
        "through Indian diplomatic missions or the Indian Emigration authorities.")
    story += signature_block("Gulf Star Recruitment Pvt Ltd", "Mohammed Arif Khan")
    doc.build(story)


# ─────────────────────────────────────────────
# Contract C — mostly_fair.pdf
# ─────────────────────────────────────────────
def make_mostly_fair():
    doc = SimpleDocTemplate(str(OUT / "mostly_fair.pdf"), pagesize=A4,
                            leftMargin=2.5*cm, rightMargin=2.5*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    story = []
    story += letterhead(
        "Doha Care Domestic Staffing W.L.L.",
        "Office 7, C-Ring Road, Doha, State of Qatar | CR: 78XXXXX",
        "DCDS/2024/DOH/1103", "20 February 2024",
    )
    story += parties_section(
        "Doha Care Domestic Staffing W.L.L., Doha, Qatar",
        "Sunita Kumari", "Indian", "Doha, State of Qatar",
    )
    story += clause("1", "Nature of Work",
        "The Employee is engaged as a <b>Domestic Worker (Housemaid)</b> at the private "
        "residence of the Employer's client family in Doha, Qatar. Duties include housekeeping, "
        "cooking, and childcare as mutually agreed with the client family.")
    story += clause("2", "Wages",
        "The Employee shall receive a monthly wage of <b>QAR 2,000 (Two Thousand Qatari Riyals)</b>, "
        "payable on the last day of each month via bank transfer to the Employee's designated "
        "account. No deduction shall be made from wages except as specified in Clause 4.")
    story += clause("3", "Working Hours",
        "Normal working hours are <b>9 hours per day, 6 days per week</b>. The Employee is "
        "entitled to one full rest day per week (Friday). Overtime work shall be compensated "
        "at QAR 15 per additional hour with the Employee's written consent.")
    story += clause("4", "Deductions",
        "The following deductions apply to the Employee's monthly wage:<br/>"
        "• Meals (breakfast, lunch, dinner) provided at the workplace: <b>26% of monthly wage "
        "(QAR 520)</b><br/>"
        "No other deductions shall be made without the Employee's prior written consent.")
    story += clause("5", "Termination",
        "This contract may be terminated by <b>either party</b> with thirty (30) days' written "
        "notice. The Employer shall pay all outstanding wages and provide a return air ticket "
        "to India upon termination for any reason. The Employee shall not be liable for any "
        "penalty upon resignation after the minimum notice period.")
    story += clause("6", "Passport and Documents",
        "The Employee shall <b>retain possession of their own passport and all travel documents</b> "
        "at all times. The Employer shall not demand or hold the Employee's passport under any "
        "circumstances. A certified copy of the passport may be held by the Employer for "
        "administrative registration purposes only.")
    story += clause("7", "Recruitment Fee",
        "No recruitment fee has been charged to the Employee. All placement and administrative "
        "costs have been borne entirely by the Employer in accordance with the ILO Fair "
        "Recruitment Guidelines.")
    story += clause("8", "Sponsor Change",
        "The Employee may apply for transfer of sponsorship in accordance with Qatar Labour "
        "Law No. 13 of 2018 (as amended). The Employer shall not unreasonably withhold consent "
        "to a sponsorship transfer after 12 months of continuous service.")
    story += clause("9", "Grievance Mechanism",
        "Any workplace dispute or grievance shall be first raised with the Employer's HR "
        "representative within 14 days of the incident. Unresolved disputes shall be referred "
        "to the Qatar Ministry of Labour (ADLSA) complaint portal or the Indian Embassy "
        "Labour Wing, Doha (Tel: +974-XXXX-XXXX). The Employee's right to contact the "
        "Indian Embassy shall not be restricted under any circumstances.")
    story += signature_block("Doha Care Domestic Staffing W.L.L.", "Sunita Kumari")
    doc.build(story)


if __name__ == "__main__":
    make_worst_case()
    print(f"  worst_case.pdf  — {(OUT / 'worst_case.pdf').stat().st_size:,} bytes")
    make_sneaky()
    print(f"  sneaky.pdf      — {(OUT / 'sneaky.pdf').stat().st_size:,} bytes")
    make_mostly_fair()
    print(f"  mostly_fair.pdf — {(OUT / 'mostly_fair.pdf').stat().st_size:,} bytes")
    print("Done.")
