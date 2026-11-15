"""
Pure-Python OpenXML PPTX Presentation Generator.
Generates presentation/ECOMMERCE_CUSTOMER_MARKETING_ANALYTICS_FINAL_PRESENTATION.pptx
without external dependencies (pure standard library: zipfile, xml.sax.saxutils).
"""

import os
import sys
import zipfile
from xml.sax.saxutils import escape
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Slides Data: exactly 12 slides as required by the assessment
SLIDES_DATA = [
    {
        "num": 1,
        "title": "Ecommerce Customer & Marketing Analytics",
        "subtitle": "Final Technical & Strategic Assessment Presentation\nAuthor: Antigravity Analytics Team | Date: November 2026",
        "category": "TITLE",
        "bullets": [
            "Project Scope: End-to-End E-Commerce Data Engineering & Advanced Marketing Analytics",
            "Execution Mode: LOCAL_REPRODUCIBLE_EXECUTION (Public GA4 Schema Design Pattern)",
            "Core Deliverables: Identity Resolution, RFM, CLV, Multi-Touch Attribution, Marketing ROI, Tableau Mart"
        ]
    },
    {
        "num": 2,
        "title": "Business Problem & Objectives",
        "subtitle": "Connecting anonymous web traffic to customer lifetime value and marketing efficiency",
        "category": "STRATEGY",
        "bullets": [
            "The Core Challenge: Disconnected web analytics (GA4 cookies) and CRM databases prevent true customer-level attribution and marketing ROI measurement.",
            "Wasted Ad Spend: Marketing spent $308,808.42 across 8 campaigns without granular ROAS/CAC clarity across top, middle, and bottom of funnel.",
            "Primary Objectives:",
            "  1. Unify GA4 web journeys with CRM customer profiles via deterministic identity resolution.",
            "  2. Implement and reconcile 4 attribution models (First Touch, Last Touch, Linear, Time Decay 7d).",
            "  3. Quantify Customer Lifetime Value (Historical Realized Margin vs 12-Month Forward Prediction).",
            "  4. Deliver an empirical, rule-based budget reallocation engine to maximize enterprise marketing ROI."
        ]
    },
    {
        "num": 3,
        "title": "Data Sources & Governance Framework",
        "subtitle": "Strict 5-Tier Data Architecture and Transparency Disclosures",
        "category": "GOVERNANCE",
        "bullets": [
            "Tier A (Public GA4 Dataset Source/Design): Schema & models based on bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*.",
            "Tier B (Synthetic CRM Data): 5,000 simulated customer profiles (Faker Seed 42, RFC 2606 @example.com, zero real PII).",
            "Tier C (Synthetic Advertising Spend): 736 daily spend records across 8 campaigns, $308,808.42 total marketing spend.",
            "Tier D (Synthetic Identity Resolution): 7,000 simulated GA4 visitor cookies with 60% resolved (4,200) and 40% anonymous (2,800).",
            "Tier E (LOCAL_REPRODUCIBLE_EXECUTION Validation Outputs): All data marts and benchmark KPIs ($131.1K revenue, 1,659 orders, 12,108 sessions) are generated deterministically by the Python analytics engine.",
            "GCP Credential Disclosure: Ambient GCP credentials not configured; live BigQuery execution is not falsely claimed."
        ]
    },
    {
        "num": 4,
        "title": "Pipeline Architecture & Data Flow",
        "subtitle": "Modular staging, intermediate sessionization/orders, and specialized analytical marts",
        "category": "ARCHITECTURE",
        "bullets": [
            "Staging Layer (SQL / BigQuery Pattern): stg_ga4_events.sql flattens repeated event_params, standardizes session_key, and isolates channel UTMs.",
            "Intermediate Sessionization & Deduplication:",
            "  • int_sessions.sql: 12,108 distinct sessions with duration, page views, engagement flags, and conversion tags.",
            "  • int_orders.sql: 1,659 deduplicated orders using ROW_NUMBER() over transaction_id (first timestamp wins).",
            "Analytical Marts (4 Core Dimensions):",
            "  • customer_profile.sql: 5,000 unified customer records combining CRM demographics and GA4 behaviors.",
            "  • fct_attribution_multi_model.sql: 9,464 attribution records comparing 4 models side-by-side.",
            "  • fct_customer_clv.sql: Historical vs predicted 12M margin per customer.",
            "  • fct_campaign_roi.sql: Campaign unit economics, ROAS, CAC, and reallocation recommendations."
        ]
    },
    {
        "num": 5,
        "title": "Deterministic Identity Resolution Bridge",
        "subtitle": "Resolving pseudonymous visitor cookies to authenticated CRM customer IDs",
        "category": "IDENTITY",
        "bullets": [
            "Resolution Mechanism: Deterministic graph bridge matching visitor user_pseudo_id to CRM customer_id via high-intent touchpoints (Checkout, Account Login, Newsletter Signup).",
            "Resolution Performance Metrics:",
            "  • Total GA4 Visitor Cookies: 7,000 distinct browser instances.",
            "  • Successfully Resolved: 4,200 visitors (60.0% Resolution Rate).",
            "  • Anonymous / Unresolved: 2,800 visitors (40.0% Unresolved Rate) — explicitly preserved to avoid false attribution.",
            "Referential Integrity: 100% of resolved customer IDs strictly link to valid synthetic CRM customer records.",
            "Cross-Device Handling: Supports 1-to-many device mapping with max confidence scoring and primary link method tracking."
        ]
    },
    {
        "num": 6,
        "title": "Customer Intelligence: RFM & CLV Segmentation",
        "subtitle": "Behavioral quintiles and forward-looking lifetime value modeling",
        "category": "CUSTOMER_ANALYTICS",
        "bullets": [
            "RFM 5x5 Quintile Segmentation (5,000 Customers):",
            "  • Champions (R>=4, F>=4, M>=4): 962 customers (19.2%) — VIP loyalty rewards, early product drops.",
            "  • At Risk High Value (R<=2, F>=3, M>=3): 1,154 customers (23.1%) — Urgent win-back offers and retention incentives.",
            "  • Loyal Customers (884, 17.7%) | Recent Potential Loyalists (704, 14.1%) | Hibernating (846, 16.9%) | Promising (450, 9.0%).",
            "Customer Lifetime Value (CLV) Framework:",
            "  • Historical Realized Margin: $59,010.32 total ($11.80 avg) based on 45% contribution margin illustrative assumption.",
            "  • Predicted 12M Forward Margin: $149,065.05 total ($29.81 avg) based on annualized order frequency, AOV, and retention curves.",
            "  • CLV Tiers: High Value VIP (163, >$120), Medium Value Core (388, $50-$120), Low Value (1,020, $20-$50), Prospect (3,429, <$20)."
        ]
    },
    {
        "num": 7,
        "title": "Multi-Touch Attribution Model Reconciliation",
        "subtitle": "Side-by-side comparison across 4 attribution models with zero revenue variance",
        "category": "ATTRIBUTION",
        "bullets": [
            "Mathematical Invariant: Every model reconciles to exactly $131,133.96 total order revenue with $0.00 unexplained variance.",
            "Attribution Weights: Sum to 1.000000 per order across all 9,464 records; zero duplicate records.",
            "Model Channel Comparison & Behavioral Insights:",
            "  • First Touch (Acquisition View): Paid Search $48.3K (36.9%), Paid Social $35.6K (27.2%), Organic Search $11.2K (8.6%).",
            "  • Last Touch (Closing View): Direct $49.7K (37.9%), Paid Search $33.5K (25.6%), Paid Social $22.3K (17.0%).",
            "  • Linear (Uniform Full-Funnel): Paid Search $39.8K (30.4%), Direct $34.3K (26.1%), Paid Social $27.6K (21.1%).",
            "  • Time Decay (Half-Life = 7 Days): Direct $39.2K (29.9%), Paid Search $37.7K (28.8%), Paid Social $25.9K (19.8%).",
            "Strategic Conclusion: Single-touch Last Touch severely penalizes top-of-funnel acquisition channels by crediting returning Direct traffic."
        ]
    },
    {
        "num": 8,
        "title": "Marketing Campaign ROI & Unit Economics",
        "subtitle": "Evaluating 8 active campaigns across Paid Search, Paid Social, Display, Video, and Affiliate",
        "category": "MARKETING_ROI",
        "bullets": [
            "Total Marketing Budget: $308,808.42 USD | Attributed Campaign Revenue: $71,747.88 | Blended ROAS: 0.232x",
            "Campaign Performance League Table:",
            "  1. Brand_Search_Core (Paid Search): Spend $36.7K | Revenue $20.8K | ROAS 0.567 | CAC $8.02 | CTR 5.87% (Rank #1)",
            "  2. Dynamic_Remarketing_Banners (Display): Spend $25.2K | Revenue $6.7K | ROAS 0.265 | CAC $68.28 | CTR 0.86% (Rank #2)",
            "  3. Holiday_Gift_Guide_2020 (Paid Social): Spend $43.2K | Revenue $10.1K | ROAS 0.234 | CAC $37.79 | CTR 2.17% (Rank #3)",
            "  4. Generic_Apparel_Promo (Paid Search): Spend $51.8K | Revenue $12.0K | ROAS 0.231 | CAC $38.36 | CTR 2.92% (Rank #4)",
            "  5. Brand_Awareness_Video_Q4 (Video): Spend $31.8K | Revenue $6.4K | ROAS 0.201 | CAC $103.20 | CTR 1.21% (Rank #5)",
            "  6. Black_Friday_Cyber_Week (Paid Social): Spend $62.6K | Revenue $11.8K | ROAS 0.189 | CAC $29.08 | CTR 2.44% (Rank #6)",
            "  7. Affiliate_Partner_Deals (Affiliate): Spend $22.1K | Revenue $3.9K | ROAS 0.178 | CAC $14.88 | CTR 3.42% (Rank #7)",
            "  8. Winter_Clearance_Sale (Paid Search): Spend $35.4K | Revenue $0.00 | ROAS 0.000 | CAC $29.56 | CTR 3.11% (Rank #8)"
        ]
    },
    {
        "num": 9,
        "title": "Tableau Analytics Mart & Dashboard Design",
        "subtitle": "Production-ready 5,000-row x 40-column mart and 5 interactive visual dashboards",
        "category": "TABLEAU",
        "bullets": [
            "Dataset Architecture: data/tableau_customer_marketing_analytics.csv (5,000 rows x 40 columns, 1 row per customer_id).",
            "Complete Data Dictionary: All 40 fields verified with zero nulls in critical measures; documented in TABLEAU_DATA_DICTIONARY.md.",
            "Interactive Dashboard Suite Designed in TABLEAU_DASHBOARD_GUIDE.md:",
            "  • Dashboard 1 (Executive Overview): Revenue scorecards, daily trend, acquisition channel donut, conversion funnel.",
            "  • Dashboard 2 (Attribution Comparison): Side-by-side 4-model bar charts, channel unit economics, touchpoint decay.",
            "  • Dashboard 3 (Campaign Efficiency Matrix): ROAS vs CAC scatter plot sized by spend, campaign league table.",
            "  • Dashboard 4 (Customer Intelligence): 5x5 RFM heatmap, segment treemap, historical vs predicted CLV scatter.",
            "  • Dashboard 5 (Budget Reallocation Waterfall): Interactive scenario model showing $74.1K capital reallocation."
        ]
    },
    {
        "num": 10,
        "title": "Budget Reallocation Recommendations",
        "subtitle": "Shifting $74,069.20 from underperforming campaigns into high-efficiency acquisition",
        "category": "RECOMMENDATIONS",
        "bullets": [
            "Transparent Rule-Based Framework: Built on objective ROAS and CAC performance thresholds.",
            "SCALE_BUDGET (+20% Immediate Expansion):",
            "  • Target: Brand_Search_Core (ROAS 0.567 >= 0.50, CAC $8.02 <= $200). Expand daily budget to capture unmet intent.",
            "OPTIMIZE_WATCH (Freeze & Monitor):",
            "  • Target: Dynamic_Remarketing_Banners (ROAS 0.265 in [0.25, 0.35), CAC $68.28). Refine audience frequency caps.",
            "REDUCE_REALLOCATE (-30% Capital Extraction):",
            "  • Harvest 30% budget reduction across 6 underperforming campaigns with ROAS < 0.25 (Total Pool: $74,069.20).",
            "  • Capital Sourced From: Black Friday Cyber Week (-$18.8K), Generic Apparel (-$15.5K), Holiday Gift Guide (-$13.0K), Winter Clearance (-$10.6K), Brand Video (-$9.5K), Affiliate (-$6.6K).",
            "Expected Impact: Blended ROAS projected to increase from 0.232 to 0.385 without increasing total marketing spend ($308.8K)."
        ]
    },
    {
        "num": 11,
        "title": "Challenges, Governance & Technical Lessons",
        "subtitle": "Overcoming ambient credential blocks, identity ambiguity, and modeling invariants",
        "category": "GOVERNANCE",
        "bullets": [
            "Challenge 1 — Missing GCP Credentials: Solved by designing a deterministic LOCAL_REPRODUCIBLE_EXECUTION engine adhering 100% to Public GA4 schema.",
            "Challenge 2 — Multi-Touch Attribution Reconciliation: Solved by implementing strict normalized lookback weights ensuring zero revenue variance ($0.00).",
            "Challenge 3 — Cross-Device Cookie Fragmentation: Addressed via deterministic identity bridge while maintaining 40% anonymous traffic as unresolved.",
            "Challenge 4 — Profitability Assumption Transparency: Addressed by explicitly labeling the 45% contribution margin as an illustrative retail scenario.",
            "Quality Assurance: 45 automated unit tests executed with 100% pass rate; full regression coverage across data, models, and analytics."
        ]
    },
    {
        "num": 12,
        "title": "Roadmap, Next Steps & Conclusion",
        "subtitle": "Productionizing the pipeline for enterprise Google Cloud deployment",
        "category": "CONCLUSION",
        "bullets": [
            "Phase 4 Production Deployment Roadmap:",
            "  1. Live BigQuery Scheduling: Migrate SQL staging and marts into dbt Core / BigQuery scheduled queries.",
            "  2. Probabilistic Identity Stitching: Augment deterministic bridge with graph-based probabilistic matching (Device Fingerprinting).",
            "  3. Algorithmic Attribution: Implement Shapley Value / Markov Chain attribution models alongside heuristic models.",
            "  4. Automated Bidding API Connectors: Feed campaign recommendations directly into Google Ads and Meta Ads bidding APIs.",
            "Executive Conclusion: Delivered a fully auditable, mathematically verified e-commerce customer and marketing analytics platform with immediate $74.1K budget optimization roadmap."
        ]
    }
]


def build_slide_xml(slide: dict) -> str:
    """Builds OpenXML string for a single slide."""
    title_escaped = escape(slide["title"])
    subtitle_escaped = escape(slide["subtitle"])
    category_escaped = escape(slide["category"])
    
    # Generate bullet paragraphs
    bullet_xml_parts = []
    for bullet in slide["bullets"]:
        b_escaped = escape(bullet)
        is_sub = bullet.startswith("  •") or bullet.startswith("  1.") or bullet.startswith("  2.") or bullet.startswith("  3.") or bullet.startswith("  4.")
        lvl = "1" if is_sub else "0"
        sz = "1500" if is_sub else "1700"
        b_clean = b_escaped.strip()
        bullet_xml_parts.append(f"""
            <a:p>
              <a:pPr lvl="{lvl}"/>
              <a:r>
                <a:rPr lang="en-US" sz="{sz}" dirty="0">
                  <a:solidFill><a:srgbClr val="2D3748"/></a:solidFill>
                </a:rPr>
                <a:t>{b_clean}</a:t>
              </a:r>
            </a:p>""")
    
    bullets_xml = "".join(bullet_xml_parts)
    slide_num = slide["num"]

    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/>
          <a:ext cx="0" cy="0"/>
          <a:chOff x="0" y="0"/>
          <a:chExt cx="0" cy="0"/>
        </a:xfrm>
      </p:grpSpPr>

      <!-- Top Header Color Banner -->
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="2" name="HeaderBanner"/>
          <p:cNvSpPr/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="0" y="0"/>
            <a:ext cx="12192000" cy="180000"/>
          </a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:solidFill><a:srgbClr val="1A365D"/></a:solidFill>
        </p:spPr>
      </p:sp>

      <!-- Category Pill -->
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="3" name="CategoryPill"/>
          <p:cNvSpPr/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="685800" y="360000"/>
            <a:ext cx="2600000" cy="280000"/>
          </a:xfrm>
          <a:prstGeom prst="roundRect"><a:avLst/></a:prstGeom>
          <a:solidFill><a:srgbClr val="E2E8F0"/></a:solidFill>
        </p:spPr>
        <p:txBody>
          <a:bodyPr lIns="72000" rIns="72000" tIns="36000" bIns="36000" anchor="ctr"/>
          <a:lstStyle/>
          <a:p>
            <a:pPr algn="ctr"/>
            <a:r>
              <a:rPr lang="en-US" sz="1100" b="1">
                <a:solidFill><a:srgbClr val="2B6CB0"/></a:solidFill>
              </a:rPr>
              <a:t>{category_escaped}</a:t>
            </a:r>
          </a:p>
        </p:txBody>
      </p:sp>

      <!-- Slide Title & Subtitle Box -->
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="4" name="TitleBox"/>
          <p:cNvSpPr/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="685800" y="680000"/>
            <a:ext cx="10820400" cy="1100000"/>
          </a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:noFill/>
        </p:spPr>
        <p:txBody>
          <a:bodyPr lIns="0" rIns="0" tIns="0" bIns="0"/>
          <a:lstStyle/>
          <a:p>
            <a:r>
              <a:rPr lang="en-US" sz="2800" b="1">
                <a:solidFill><a:srgbClr val="1A202C"/></a:solidFill>
              </a:rPr>
              <a:t>{title_escaped}</a:t>
            </a:r>
          </a:p>
          <a:p>
            <a:r>
              <a:rPr lang="en-US" sz="1500" i="1">
                <a:solidFill><a:srgbClr val="4A5568"/></a:solidFill>
              </a:rPr>
              <a:t>{subtitle_escaped}</a:t>
            </a:r>
          </a:p>
        </p:txBody>
      </p:sp>

      <!-- Content Container Box (Card) -->
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="5" name="ContentCard"/>
          <p:cNvSpPr/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="685800" y="1850000"/>
            <a:ext cx="10820400" cy="4450000"/>
          </a:xfrm>
          <a:prstGeom prst="roundRect"><a:avLst/></a:prstGeom>
          <a:solidFill><a:srgbClr val="F7FAFC"/></a:solidFill>
          <a:ln w="12700"><a:solidFill><a:srgbClr val="E2E8F0"/></a:solidFill></a:ln>
        </p:spPr>
        <p:txBody>
          <a:bodyPr lIns="250000" rIns="250000" tIns="250000" bIns="250000"/>
          <a:lstStyle/>
          {bullets_xml}
        </p:txBody>
      </p:sp>

      <!-- Footer Info -->
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="6" name="Footer"/>
          <p:cNvSpPr/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="685800" y="6420000"/>
            <a:ext cx="10820400" cy="300000"/>
          </a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:noFill/>
        </p:spPr>
        <p:txBody>
          <a:bodyPr lIns="0" rIns="0" tIns="0" bIns="0"/>
          <a:lstStyle/>
          <a:p>
            <a:r>
              <a:rPr lang="en-US" sz="1000">
                <a:solidFill><a:srgbClr val="718096"/></a:solidFill>
              </a:rPr>
              <a:t>Ecommerce Customer &amp; Marketing Analytics Assessment | LOCAL_REPRODUCIBLE_EXECUTION | Slide {slide_num} of 12</a:t>
            </a:r>
          </a:p>
        </p:txBody>
      </p:sp>

    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>"""


def build_slide_rels() -> str:
    """Builds relationships XML for each slide."""
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>"""


def build_presentation_xml() -> str:
    """Builds ppt/presentation.xml for 12 slides."""
    sld_id_parts = []
    for i in range(1, 13):
        sld_id_parts.append(f'<p:sldId id="{255 + i}" r:id="rId{i}"/>')
    sld_id_xml = "".join(sld_id_parts)

    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst>
    <p:sldMasterId id="2147483648" r:id="rId13"/>
  </p:sldMasterIdLst>
  <p:sldIdLst>
    {sld_id_xml}
  </p:sldIdLst>
  <p:sldSz cx="12192000" cy="6858000" type="screen16x9"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>"""


def build_presentation_rels() -> str:
    """Builds ppt/_rels/presentation.xml.rels."""
    rel_parts = []
    for i in range(1, 13):
        rel_parts.append(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>\n')
    rel_parts.append('<Relationship Id="rId13" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>\n')
    rel_parts.append('<Relationship Id="rId14" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>\n')
    rels_content = "".join(rel_parts)

    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
{rels_content}
</Relationships>"""


def build_content_types() -> str:
    """Builds [Content_Types].xml."""
    override_parts = []
    for i in range(1, 13):
        override_parts.append(f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>\n')
    overrides_content = "".join(override_parts)

    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
  {overrides_content}
</Types>"""


def build_root_rels() -> str:
    """Builds _rels/.rels."""
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>"""


def build_theme_xml() -> str:
    """Builds ppt/theme/theme1.xml."""
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Enterprise Theme">
  <a:themeElements>
    <a:clrScheme name="Executive">
      <a:dk1><a:srgbClr val="1A202C"/></a:dk1>
      <a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>
      <a:dk2><a:srgbClr val="2D3748"/></a:dk2>
      <a:lt2><a:srgbClr val="F7FAFC"/></a:lt2>
      <a:accent1><a:srgbClr val="1A365D"/></a:accent1>
      <a:accent2><a:srgbClr val="2B6CB0"/></a:accent2>
      <a:accent3><a:srgbClr val="319795"/></a:accent3>
      <a:accent4><a:srgbClr val="DD6B20"/></a:accent4>
      <a:accent5><a:srgbClr val="E53E3E"/></a:accent5>
      <a:accent6><a:srgbClr val="805AD5"/></a:accent6>
      <a:hlink><a:srgbClr val="2B6CB0"/></a:hlink>
      <a:folHlink><a:srgbClr val="805AD5"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="Modern">
      <a:majorFont><a:latin typeface="Segoe UI"/></a:majorFont>
      <a:minorFont><a:latin typeface="Segoe UI"/></a:minorFont>
    </a:fontScheme>
    <a:fmtScheme name="Office">
      <a:fillStyleLst><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill></a:fillStyleLst>
      <a:lnStyleLst><a:ln w="9525"><a:solidFill><a:srgbClr val="CBD5E0"/></a:solidFill></a:ln></a:lnStyleLst>
      <a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>
      <a:bgFillStyleLst><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill></a:bgFillStyleLst>
    </a:fmtScheme>
  </a:themeElements>
</a:theme>"""


def build_slide_layout_xml() -> str:
    """Builds ppt/slideLayouts/slideLayout1.xml."""
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
             type="blank" preserve="1">
  <p:cSld name="Blank">
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>"""


def build_slide_layout_rels() -> str:
    """Builds ppt/slideLayouts/_rels/slideLayout1.xml.rels."""
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>"""


def build_slide_master_xml() -> str:
    """Builds ppt/slideMasters/slideMaster1.xml."""
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    </p:spTree>
  </p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst>
    <p:sldLayoutId id="2147483649" r:id="rId1"/>
  </p:sldLayoutIdLst>
  <p:txStyles>
    <p:titleStyle><a:lvl1pPr><a:defRPr sz="2800"><a:solidFill><a:srgbClr val="1A202C"/></a:solidFill></a:defRPr></a:lvl1pPr></p:titleStyle>
    <p:bodyStyle><a:lvl1pPr><a:defRPr sz="1800"><a:solidFill><a:srgbClr val="2D3748"/></a:solidFill></a:defRPr></a:lvl1pPr></p:bodyStyle>
    <p:otherStyle><a:lvl1pPr><a:defRPr sz="1200"><a:solidFill><a:srgbClr val="4A5568"/></a:solidFill></a:defRPr></a:lvl1pPr></p:otherStyle>
  </p:txStyles>
</p:sldMaster>"""


def build_slide_master_rels() -> str:
    """Builds ppt/slideMasters/_rels/slideMaster1.xml.rels."""
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>"""


def create_pptx_file(output_path: Path):
    """Assembles all OpenXML components into a valid .pptx file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # 1. Root & Content Types
        zf.writestr("[Content_Types].xml", build_content_types())
        zf.writestr("_rels/.rels", build_root_rels())

        # 2. Presentation definition & relationships
        zf.writestr("ppt/presentation.xml", build_presentation_xml())
        zf.writestr("ppt/_rels/presentation.xml.rels", build_presentation_rels())

        # 3. Master, layout, and theme
        zf.writestr("ppt/theme/theme1.xml", build_theme_xml())
        zf.writestr("ppt/slideMasters/slideMaster1.xml", build_slide_master_xml())
        zf.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", build_slide_master_rels())
        zf.writestr("ppt/slideLayouts/slideLayout1.xml", build_slide_layout_xml())
        zf.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", build_slide_layout_rels())

        # 4. Slides and slide relationships
        for slide in SLIDES_DATA:
            i = slide["num"]
            zf.writestr(f"ppt/slides/slide{i}.xml", build_slide_xml(slide))
            zf.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", build_slide_rels())

    print(f"Successfully generated PowerPoint presentation: {output_path} ({len(SLIDES_DATA)} slides)")


if __name__ == "__main__":
    out_file = PROJECT_ROOT / "presentation" / "ECOMMERCE_CUSTOMER_MARKETING_ANALYTICS_FINAL_PRESENTATION.pptx"
    create_pptx_file(out_file)

