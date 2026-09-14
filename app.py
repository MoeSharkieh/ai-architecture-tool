import json
import os
import re
from io import BytesIO

import pandas as pd
import streamlit as st
from fpdf import FPDF
from matplotlib import font_manager
from openai import OpenAI
from supabase import create_client


PACK_SCHEMA = {
    "type": "object",
    "properties": {
        "project_overview": {"type": "string"},
        "design_objectives": {
            "type": "array",
            "items": {"type": "string"},
        },
        "assumptions": {
            "type": "array",
            "items": {"type": "string"},
        },
        "missing_information": {
            "type": "array",
            "items": {"type": "string"},
        },
        "spaces": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "zone": {
                        "type": "string",
                        "enum": ["Public", "Private", "Service"],
                    },
                    "space_name": {"type": "string"},
                    "quantity": {"type": "integer", "minimum": 1},
                    "unit_area_m2": {"type": "number", "minimum": 0.1},
                    "priority": {
                        "type": "string",
                        "enum": ["Essential", "Recommended", "Optional"],
                    },
                    "suggested_floor": {"type": "string"},
                    "notes": {"type": "string"},
                },
                "required": [
                    "zone",
                    "space_name",
                    "quantity",
                    "unit_area_m2",
                    "priority",
                    "suggested_floor",
                    "notes",
                ],
                "additionalProperties": False,
            },
        },
        "zoning_strategy": {
            "type": "array",
            "items": {"type": "string"},
        },
        "circulation_accessibility": {
            "type": "array",
            "items": {"type": "string"},
        },
        "environmental_strategy": {
            "type": "array",
            "items": {"type": "string"},
        },
        "materials_facade": {
            "type": "array",
            "items": {"type": "string"},
        },
        "risks": {
            "type": "array",
            "items": {"type": "string"},
        },
        "next_steps": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": [
        "project_overview",
        "design_objectives",
        "assumptions",
        "missing_information",
        "spaces",
        "zoning_strategy",
        "circulation_accessibility",
        "environmental_strategy",
        "materials_facade",
        "risks",
        "next_steps",
    ],
    "additionalProperties": False,
}


def clean_text_for_pdf(text):
    text = re.sub(r"#{1,6}\s*", "", text)
    text = text.replace("**", "")
    text = text.replace("*", "")
    text = text.replace("â¢", "-")
    text = text.replace("â", "-")
    text = text.replace("â", "-")
    text = text.replace("â", "'")
    text = text.replace("â", '"')
    text = text.replace("â", '"')
    text = text.replace("|", "  ")
    return text


def get_pdf_font(pdf, language):
    is_arabic = language == "Ø§ÙØ¹Ø±Ø¨ÙØ©"

    if not is_arabic:
        return "Helvetica", "L"

    regular_font = font_manager.findfont(
        font_manager.FontProperties(family="DejaVu Sans")
    )
    bold_font = font_manager.findfont(
        font_manager.FontProperties(
            family="DejaVu Sans",
            weight="bold",
        )
    )

    if not os.path.exists(regular_font):
        raise FileNotFoundError("Arabic font was not found.")
    if not os.path.exists(bold_font):
        raise FileNotFoundError("Arabic bold font was not found.")

    pdf.add_font("DejaVu", "", regular_font)
    pdf.add_font("DejaVu", "B", bold_font)
    pdf.set_text_shaping(
        use_shaping_engine=True,
        direction="rtl",
        script="arab",
        language="ara",
    )
    return "DejaVu", "R"


def create_pdf(project_name, report_markdown, language):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    font_name, alignment = get_pdf_font(pdf, language)

    pdf.set_font(font_name, "B", 18)
    pdf.set_text_color(22, 50, 79)
    pdf.multi_cell(0, 10, "AI Architecture Tool", align=alignment)
    pdf.ln(3)

    pdf.set_font(font_name, "B", 14)
    pdf.set_text_color(37, 99, 235)
    pdf.multi_cell(
        0,
        8,
        clean_text_for_pdf(project_name),
        align=alignment,
    )
    pdf.ln(5)

    pdf.set_font(font_name, size=10)
    pdf.set_text_color(30, 30, 30)

    for line in clean_text_for_pdf(report_markdown).splitlines():
        pdf.set_x(pdf.l_margin)
        if line.strip():
            pdf.multi_cell(0, 6, line, align=alignment)
        else:
            pdf.ln(2)

    return bytes(pdf.output())


def get_supabase():
    if "supabase_client" not in st.session_state:
        st.session_state.supabase_client = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"],
        )
    return st.session_state.supabase_client


def calculate_space_program(
    spaces,
    circulation_percentage,
    service_percentage,
    walls_percentage,
    language,
):
    rows = []

    zone_ar = {
        "Public": "Ø¹Ø§Ù",
        "Private": "Ø®Ø§Øµ",
        "Service": "Ø®Ø¯ÙØ§Øª",
    }
    priority_ar = {
        "Essential": "Ø£Ø³Ø§Ø³Ù",
        "Recommended": "ÙÙØµÙ Ø¨Ù",
        "Optional": "Ø§Ø®ØªÙØ§Ø±Ù",
    }

    for space in spaces:
        quantity = max(int(space["quantity"]), 1)
        unit_area = max(float(space["unit_area_m2"]), 0.1)
        net_total = quantity * unit_area

        zone = space["zone"]
        priority = space["priority"]
        if language == "Ø§ÙØ¹Ø±Ø¨ÙØ©":
            zone = zone_ar.get(zone, zone)
            priority = priority_ar.get(priority, priority)

        rows.append(
            {
                "Zone" if language == "English" else "Ø§ÙÙÙØ·ÙØ©": zone,
                "Space" if language == "English" else "Ø§ÙÙØ±Ø§Øº": space[
                    "space_name"
                ],
                "Qty" if language == "English" else "Ø§ÙØ¹Ø¯Ø¯": quantity,
                "Unit Area (mÂ²)"
                if language == "English"
                else "ÙØ³Ø§Ø­Ø© Ø§ÙÙØ­Ø¯Ø© (ÙÂ²)": round(unit_area, 2),
                "Net Total (mÂ²)"
                if language == "English"
                else "Ø§ÙØ¥Ø¬ÙØ§ÙÙ Ø§ÙØµØ§ÙÙ (ÙÂ²)": round(net_total, 2),
                "Priority"
                if language == "English"
                else "Ø§ÙØ£ÙÙÙÙØ©": priority,
                "Suggested Floor"
                if language == "English"
                else "Ø§ÙØ·Ø§Ø¨Ù Ø§ÙÙÙØªØ±Ø­": space["suggested_floor"],
                "Notes" if language == "English" else "ÙÙØ§Ø­Ø¸Ø§Øª": space[
                    "notes"
                ],
            }
        )

    dataframe = pd.DataFrame(rows)
    total_column = (
        "Net Total (mÂ²)"
        if language == "English"
        else "Ø§ÙØ¥Ø¬ÙØ§ÙÙ Ø§ÙØµØ§ÙÙ (ÙÂ²)"
    )
    net_area = float(dataframe[total_column].sum()) if not dataframe.empty else 0
    circulation_area = net_area * circulation_percentage / 100
    service_area = net_area * service_percentage / 100
    walls_area = net_area * walls_percentage / 100
    built_up_area = net_area + circulation_area + service_area + walls_area
    efficiency_ratio = (
        net_area / built_up_area * 100 if built_up_area else 0
    )

    metrics = {
        "net_area": net_area,
        "circulation_area": circulation_area,
        "service_area": service_area,
        "walls_area": walls_area,
        "built_up_area": built_up_area,
        "efficiency_ratio": efficiency_ratio,
    }
    return dataframe, metrics


def bullet_list(items):
    if not items:
        return "- None"
    return "\n".join(f"- {item}" for item in items)


def dataframe_to_markdown(dataframe):
    if dataframe.empty:
        return "No spaces were generated."

    columns = list(dataframe.columns)
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in dataframe.iterrows():
        values = [str(row[column]).replace("|", "/") for column in columns]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def build_report_markdown(pack, dataframe, metrics, percentages, language):
    circulation_percentage, service_percentage, walls_percentage = percentages

    if language == "Ø§ÙØ¹Ø±Ø¨ÙØ©":
        headings = {
            "title": "# Ø­Ø²ÙØ© ÙØ§ ÙØ¨Ù Ø§ÙØªØµÙÙÙ Ø§ÙÙØ¹ÙØ§Ø±Ù",
            "overview": "## 1. ÙÙØ®Øµ Ø§ÙÙØ´Ø±ÙØ¹",
            "objectives": "## 2. Ø£ÙØ¯Ø§Ù Ø§ÙØªØµÙÙÙ",
            "assumptions": "## 3. Ø§ÙØ§ÙØªØ±Ø§Ø¶Ø§Øª",
            "missing": "## 4. Ø§ÙÙØ¹ÙÙÙØ§Øª Ø§ÙÙØ§ÙØµØ©",
            "program": "## 5. Ø¨Ø±ÙØ§ÙØ¬ Ø§ÙÙØ³Ø§Ø­Ø§Øª",
            "areas": "## 6. ÙÙØ®Øµ Ø­Ø³Ø§Ø¨Ø§Øª Ø§ÙÙØ³Ø§Ø­Ø§Øª",
            "zoning": "## 7. Ø§Ø³ØªØ±Ø§ØªÙØ¬ÙØ© ØªÙØ²ÙØ¹ Ø§ÙÙÙØ§Ø·Ù",
            "circulation": "## 8. Ø§ÙØ­Ø±ÙØ© ÙØ³ÙÙÙØ© Ø§ÙÙØµÙÙ",
            "environment": "## 9. Ø§ÙØ§Ø³ØªØ±Ø§ØªÙØ¬ÙØ© Ø§ÙØ¨ÙØ¦ÙØ©",
            "materials": "## 10. Ø§ÙÙÙØ§Ø¯ ÙØ§ÙÙØ§Ø¬ÙØ§Øª",
            "risks": "## 11. Ø§ÙÙØ®Ø§Ø·Ø± ÙØ§ÙÙØ±Ø§Ø±Ø§Øª Ø§ÙÙØ·ÙÙØ¨Ø©",
            "steps": "## 12. Ø§ÙØ®Ø·ÙØ§Øª Ø§ÙØªØ§ÙÙØ©",
            "disclaimer": "## 13. Ø§ÙØªÙØ¨ÙÙ Ø§ÙÙÙÙÙ",
        }
        area_summary = f"""
- **Ø§ÙÙØ³Ø§Ø­Ø© Ø§ÙØµØ§ÙÙØ© Ø§ÙÙØ¨Ø±ÙØ¬Ø©:** {metrics['net_area']:.1f} ÙÂ²
- **Ø¨Ø¯Ù Ø§ÙØ­Ø±ÙØ© ({circulation_percentage}%):** {metrics['circulation_area']:.1f} ÙÂ²
- **Ø¨Ø¯Ù Ø§ÙØ®Ø¯ÙØ§Øª ({service_percentage}%):** {metrics['service_area']:.1f} ÙÂ²
- **Ø¨Ø¯Ù Ø§ÙØ¬Ø¯Ø±Ø§Ù ÙØ§ÙØ¥ÙØ´Ø§Ø¡ ({walls_percentage}%):** {metrics['walls_area']:.1f} ÙÂ²
- **Ø§ÙÙØ³Ø§Ø­Ø© Ø§ÙØ¨ÙØ§Ø¦ÙØ© Ø§ÙØªÙØ±ÙØ¨ÙØ©:** {metrics['built_up_area']:.1f} ÙÂ²
- **ÙØ³Ø¨Ø© Ø§ÙÙÙØ§Ø¡Ø© Ø§ÙØªÙØ±ÙØ¨ÙØ©:** {metrics['efficiency_ratio']:.1f}%
"""
        disclaimer = (
            "ÙØ°Ù Ø­Ø²ÙØ© Ø£ÙÙÙØ© ÙØ¯Ø¹Ù ÙØ±Ø­ÙØ© ÙØ§ ÙØ¨Ù Ø§ÙØªØµÙÙÙ. Ø§ÙÙØ³Ø§Ø­Ø§Øª ÙØ§ÙÙØ³Ø¨ "
            "Ø§ÙÙÙØªØ±Ø­Ø© ØªÙØ¯ÙØ±ÙØ© ÙÙØ§Ø¨ÙØ© ÙÙØªØ¹Ø¯ÙÙØ ÙÙØ§ ØªÙØ«Ù Ø§Ø¹ØªÙØ§Ø¯ÙØ§ ÙÙØ¯Ø³ÙÙØ§ Ø£Ù "
            "ØªØ­ÙÙÙØ§ ÙÙ ÙÙØ¯ Ø§ÙØ¨ÙØ§Ø¡. ÙØ¬Ø¨ ÙØ±Ø§Ø¬Ø¹ØªÙØ§ ÙÙ ÙØ¹ÙØ§Ø±Ù ÙØ¤ÙÙ ÙØ§ÙØ¬ÙØ§Øª Ø§ÙÙØ®ØªØµØ©."
        )
    else:
        headings = {
            "title": "# Architectural Pre-Design Pack",
            "overview": "## 1. Project Snapshot",
            "objectives": "## 2. Design Objectives",
            "assumptions": "## 3. Assumptions",
            "missing": "## 4. Missing Information",
            "program": "## 5. Space Program",
            "areas": "## 6. Area Calculation Summary",
            "zoning": "## 7. Functional Zoning Strategy",
            "circulation": "## 8. Circulation and Accessibility",
            "environment": "## 9. Environmental Strategy",
            "materials": "## 10. Materials and FaÃ§ade",
            "risks": "## 11. Risks and Required Decisions",
            "steps": "## 12. Recommended Next Steps",
            "disclaimer": "## 13. Professional Disclaimer",
        }
        area_summary = f"""
- **Programmed net area:** {metrics['net_area']:.1f} mÂ²
- **Circulation allowance ({circulation_percentage}%):** {metrics['circulation_area']:.1f} mÂ²
- **Service allowance ({service_percentage}%):** {metrics['service_area']:.1f} mÂ²
- **Walls/structure allowance ({walls_percentage}%):** {metrics['walls_area']:.1f} mÂ²
- **Approximate gross built-up area:** {metrics['built_up_area']:.1f} mÂ²
- **Approximate efficiency ratio:** {metrics['efficiency_ratio']:.1f}%
"""
        disclaimer = (
            "This is an early-stage pre-design aid. Suggested areas and "
            "allowances are preliminary and editable; they are not an "
            "engineering approval or a building-code compliance check. A "
            "qualified architect and the relevant authorities must review them."
        )

    return f"""
{headings['title']}

{headings['overview']}

{pack['project_overview']}

{headings['objectives']}

{bullet_list(pack['design_objectives'])}

{headings['assumptions']}

{bullet_list(pack['assumptions'])}

{headings['missing']}

{bullet_list(pack['missing_information'])}

{headings['program']}

{dataframe_to_markdown(dataframe)}

{headings['areas']}
{area_summary}
{headings['zoning']}

{bullet_list(pack['zoning_strategy'])}

{headings['circulation']}

{bullet_list(pack['circulation_accessibility'])}

{headings['environment']}

{bullet_list(pack['environmental_strategy'])}

{headings['materials']}

{bullet_list(pack['materials_facade'])}

{headings['risks']}

{bullet_list(pack['risks'])}

{headings['steps']}

{bullet_list(pack['next_steps'])}

{headings['disclaimer']}

{disclaimer}
""".strip()


def create_excel(dataframe, metrics, percentages, language):
    output = BytesIO()
    circulation_percentage, service_percentage, walls_percentage = percentages

    if language == "Ø§ÙØ¹Ø±Ø¨ÙØ©":
        summary_data = {
            "Ø§ÙØ¨ÙØ¯": [
                "Ø§ÙÙØ³Ø§Ø­Ø© Ø§ÙØµØ§ÙÙØ©",
                f"Ø§ÙØ­Ø±ÙØ© ({circulation_percentage}%)",
                f"Ø§ÙØ®Ø¯ÙØ§Øª ({service_percentage}%)",
                f"Ø§ÙØ¬Ø¯Ø±Ø§Ù ÙØ§ÙØ¥ÙØ´Ø§Ø¡ ({walls_percentage}%)",
                "Ø§ÙÙØ³Ø§Ø­Ø© Ø§ÙØ¨ÙØ§Ø¦ÙØ© Ø§ÙØªÙØ±ÙØ¨ÙØ©",
                "ÙØ³Ø¨Ø© Ø§ÙÙÙØ§Ø¡Ø©",
            ],
            "Ø§ÙÙÙÙØ©": [
                round(metrics["net_area"], 2),
                round(metrics["circulation_area"], 2),
                round(metrics["service_area"], 2),
                round(metrics["walls_area"], 2),
                round(metrics["built_up_area"], 2),
                f"{metrics['efficiency_ratio']:.1f}%",
            ],
        }
        program_sheet = "Ø¨Ø±ÙØ§ÙØ¬ Ø§ÙÙØ³Ø§Ø­Ø§Øª"
        summary_sheet = "ÙÙØ®Øµ Ø§ÙÙØ³Ø§Ø­Ø§Øª"
    else:
        summary_data = {
            "Item": [
                "Programmed net area",
                f"Circulation ({circulation_percentage}%)",
                f"Services ({service_percentage}%)",
                f"Walls and structure ({walls_percentage}%)",
                "Approximate gross built-up area",
                "Efficiency ratio",
            ],
            "Value": [
                round(metrics["net_area"], 2),
                round(metrics["circulation_area"], 2),
                round(metrics["service_area"], 2),
                round(metrics["walls_area"], 2),
                round(metrics["built_up_area"], 2),
                f"{metrics['efficiency_ratio']:.1f}%",
            ],
        }
        program_sheet = "Space Program"
        summary_sheet = "Area Summary"

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dataframe.to_excel(writer, sheet_name=program_sheet, index=False)
        pd.DataFrame(summary_data).to_excel(
            writer,
            sheet_name=summary_sheet,
            index=False,
        )

        for worksheet in writer.book.worksheets:
            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = worksheet.dimensions
            for column_cells in worksheet.columns:
                max_length = max(
                    len(str(cell.value or "")) for cell in column_cells
                )
                worksheet.column_dimensions[
                    column_cells[0].column_letter
                ].width = min(max(max_length + 2, 12), 45)

    output.seek(0)
    return output.getvalue()


def generate_pack(client, project_information, language):
    if language == "Ø§ÙØ¹Ø±Ø¨ÙØ©":
        output_instruction = (
            "Write every user-facing value in clear professional Modern "
            "Standard Arabic. Keep the JSON property names unchanged."
        )
    else:
        output_instruction = (
            "Write every user-facing value in clear professional English."
        )

    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=f"""
You are a professional architectural programming consultant working at
the pre-design stage.

Create a structured Architectural Pre-Design Pack from only the project
information supplied by the user. {output_instruction}

Rules:
- Never claim that a building code, zoning regulation, budget, site
  condition, or authority requirement has been verified.
- Separate user facts from your preliminary recommendations.
- Build a practical starter space program suited to the stated project.
- Space quantities and unit areas are concept-stage recommendations, not
  verified requirements. Mention this clearly in assumptions.
- Do not include circulation, service allowance, walls, structure,
  parking, landscape, or outdoor areas as ordinary room rows unless the
  user explicitly requested a named space. Python calculates allowances.
- Use only Public, Private, or Service in the zone field.
- Use only Essential, Recommended, or Optional in the priority field.
- If information is missing, list it instead of silently inventing it.
- Avoid generic filler. Keep recommendations project-specific, concise,
  and useful before schematic design begins.
- Do not provide construction-ready dimensions or approvals.
""",
        input=project_information,
        text={
            "format": {
                "type": "json_schema",
                "name": "architectural_pre_design_pack",
                "schema": PACK_SCHEMA,
                "strict": True,
            }
        },
    )
    return json.loads(response.output_text)


st.set_page_config(
    page_title="AI Architecture Tool",
    page_icon="ðï¸",
    layout="wide",
)

st.markdown(
    """
<style>
    .stApp { background-color: #f7f9fc; }
    .main-title {
        color: #16324f;
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 5px;
    }
    .subtitle {
        color: #4f6d8a;
        font-size: 20px;
        margin-bottom: 25px;
    }
    .stButton > button,
    .stFormSubmitButton > button,
    .stDownloadButton > button {
        width: 100%;
        border-radius: 10px;
        padding: 12px;
        font-size: 16px;
        font-weight: 600;
    }
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stNumberInput"] input {
        border-radius: 10px;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">ðï¸ AI Architecture Tool</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">From project idea to a structured '
    'architectural pre-design pack</div>',
    unsafe_allow_html=True,
)

try:
    supabase = get_supabase()
except Exception as connection_error:
    st.error(f"Supabase connection failed: {connection_error}")
    st.stop()


if "user_id" not in st.session_state:
    st.info(
        "Sign in or create an account to receive one free pre-design pack.\n\n"
        "Ø³Ø¬ÙÙ Ø§ÙØ¯Ø®ÙÙ Ø£Ù Ø£ÙØ´Ø¦ Ø­Ø³Ø§Ø¨ÙØ§ ÙÙØ­ØµÙÙ Ø¹ÙÙ Ø­Ø²ÙØ© ÙØ§ ÙØ¨Ù Ø§ÙØªØµÙÙÙ ÙØ¬Ø§ÙÙØ§."
    )

    sign_in_tab, sign_up_tab = st.tabs(
        ["Sign In / ØªØ³Ø¬ÙÙ Ø§ÙØ¯Ø®ÙÙ", "Create Account / Ø¥ÙØ´Ø§Ø¡ Ø­Ø³Ø§Ø¨"]
    )

    with sign_in_tab:
        with st.form("sign_in_form"):
            sign_in_email = st.text_input(
                "Email / Ø§ÙØ¨Ø±ÙØ¯ Ø§ÙØ¥ÙÙØªØ±ÙÙÙ",
                key="sign_in_email",
            )
            sign_in_password = st.text_input(
                "Password / ÙÙÙØ© Ø§ÙÙØ±ÙØ±",
                type="password",
                key="sign_in_password",
            )
            sign_in_button = st.form_submit_button(
                "Sign In / ØªØ³Ø¬ÙÙ Ø§ÙØ¯Ø®ÙÙ"
            )

        if sign_in_button:
            if not sign_in_email.strip() or not sign_in_password:
                st.warning("Please enter your email and password.")
            else:
                try:
                    auth_response = supabase.auth.sign_in_with_password(
                        {
                            "email": sign_in_email.strip(),
                            "password": sign_in_password,
                        }
                    )
                    if auth_response.user:
                        st.session_state.user_id = auth_response.user.id
                        st.session_state.user_email = auth_response.user.email
                        st.rerun()
                except Exception:
                    st.error(
                        "Sign-in failed. Check your email, password, "
                        "and email confirmation."
                    )

    with sign_up_tab:
        with st.form("sign_up_form"):
            sign_up_email = st.text_input(
                "Email / Ø§ÙØ¨Ø±ÙØ¯ Ø§ÙØ¥ÙÙØªØ±ÙÙÙ",
                key="sign_up_email",
            )
            sign_up_password = st.text_input(
                "Create Password / Ø¥ÙØ´Ø§Ø¡ ÙÙÙØ© ÙØ±ÙØ±",
                type="password",
                key="sign_up_password",
            )
            confirm_password = st.text_input(
                "Confirm Password / ØªØ£ÙÙØ¯ ÙÙÙØ© Ø§ÙÙØ±ÙØ±",
                type="password",
                key="confirm_password",
            )
            sign_up_button = st.form_submit_button(
                "Create Account / Ø¥ÙØ´Ø§Ø¡ Ø­Ø³Ø§Ø¨"
            )

        if sign_up_button:
            if not sign_up_email.strip():
                st.warning("Please enter your email address.")
            elif len(sign_up_password) < 8:
                st.warning("Password must contain at least 8 characters.")
            elif sign_up_password != confirm_password:
                st.warning("The passwords do not match.")
            else:
                try:
                    auth_response = supabase.auth.sign_up(
                        {
                            "email": sign_up_email.strip(),
                            "password": sign_up_password,
                        }
                    )
                    if auth_response.session:
                        st.session_state.user_id = auth_response.user.id
                        st.session_state.user_email = auth_response.user.email
                        st.rerun()
                    else:
                        st.success(
                            "Account created! Check your email and confirm "
                            "your account, then sign in."
                        )
                except Exception:
                    st.error(
                        "Account creation failed. The email may already "
                        "be registered."
                    )
    st.stop()


account_column, logout_column = st.columns([4, 1])
with account_column:
    st.caption(f"Signed in as: {st.session_state.user_email}")
with logout_column:
    if st.button("Logout", use_container_width=True):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass
        for session_key in [
            "supabase_client",
            "user_id",
            "user_email",
            "generated_pack",
        ]:
            st.session_state.pop(session_key, None)
        st.rerun()


language = st.selectbox(
    "Analysis Language / ÙØºØ© Ø§ÙØªØ­ÙÙÙ",
    ["English", "Ø§ÙØ¹Ø±Ø¨ÙØ©"],
)

if language == "Ø§ÙØ¹Ø±Ø¨ÙØ©":
    copy = {
        "intro": "Ø£Ø¯Ø®Ù ÙØ¹ÙÙÙØ§Øª Ø§ÙÙØ´Ø±ÙØ¹ ÙØ¥ÙØ´Ø§Ø¡ Ø­Ø²ÙØ© Ø£ÙÙÙØ© ÙÙØ¸ÙØ© ÙÙØ§Ø¨ÙØ© ÙÙØªØ¹Ø¯ÙÙ.",
        "project_types": [
            "Ø³ÙÙÙ",
            "ØªØ¬Ø§Ø±Ù",
            "ÙÙØ§ØªØ¨",
            "Ø¶ÙØ§ÙØ© ÙÙÙØ§Ø¯Ù",
            "ØªØ¹ÙÙÙÙ",
            "ØµØ­Ù",
            "Ø«ÙØ§ÙÙ",
            "ÙØªØ¹Ø¯Ø¯ Ø§ÙØ§Ø³ØªØ®Ø¯Ø§ÙØ§Øª",
            "ÙØ´Ø±ÙØ¹ Ø¢Ø®Ø±",
        ],
        "project_type": "ÙÙØ¹ Ø§ÙÙØ´Ø±ÙØ¹",
        "project_name": "Ø§Ø³Ù Ø§ÙÙØ´Ø±ÙØ¹",
        "location": "Ø§ÙÙØ¯ÙÙØ© ÙØ§ÙØ¯ÙÙØ©",
        "plot_area": "ÙØ³Ø§Ø­Ø© Ø§ÙØ£Ø±Ø¶ Ø§ÙØªÙØ±ÙØ¨ÙØ© (ÙÂ²)",
        "floors": "Ø¹Ø¯Ø¯ Ø§ÙØ·ÙØ§Ø¨Ù",
        "budget": "Ø§ÙÙÙØ²Ø§ÙÙØ© Ø§ÙØªÙØ±ÙØ¨ÙØ© (Ø§Ø®ØªÙØ§Ø±Ù)",
        "description": "ÙØªØ·ÙØ¨Ø§Øª ÙÙØµÙ Ø§ÙÙØ´Ø±ÙØ¹",
        "location_placeholder": "ÙØ«Ø§Ù: Ø§ÙØ±ÙØ§Ø¶Ø Ø§ÙØ³Ø¹ÙØ¯ÙØ©",
        "budget_placeholder": "ÙØ«Ø§Ù: 3,000,000 Ø±ÙØ§Ù Ø³Ø¹ÙØ¯Ù",
        "description_placeholder": (
            "Ø§Ø°ÙØ± Ø§ÙÙØ³ØªØ®Ø¯ÙÙÙ ÙØ§ÙÙØ±Ø§ØºØ§Øª ÙØ§ÙØ·Ø±Ø§Ø² ÙØ§ÙÙÙØ§Ø® ÙØ§ÙØ®ØµÙØµÙØ© "
            "ÙØ£Ù Ø§Ø­ØªÙØ§Ø¬Ø§Øª Ø®Ø§ØµØ©."
        ),
        "assumptions": "Ø§ÙØªØ±Ø§Ø¶Ø§Øª Ø­Ø³Ø§Ø¨ Ø§ÙÙØ³Ø§Ø­Ø§Øª",
        "assumptions_help": (
            "ÙØ°Ù ÙØ³Ø¨ Ø£ÙÙÙØ© ÙØ§Ø¨ÙØ© ÙÙØªØ¹Ø¯ÙÙ ÙÙÙØ³Øª ÙØªØ·ÙØ¨Ø§Øª ÙÙØ¯ ÙØ¹ØªÙØ¯Ø©."
        ),
        "circulation": "ÙØ³Ø¨Ø© Ø§ÙØ­Ø±ÙØ© (%)",
        "services": "ÙØ³Ø¨Ø© Ø§ÙØ®Ø¯ÙØ§Øª (%)",
        "walls": "ÙØ³Ø¨Ø© Ø§ÙØ¬Ø¯Ø±Ø§Ù ÙØ§ÙØ¥ÙØ´Ø§Ø¡ (%)",
        "button": "Ø¥ÙØ´Ø§Ø¡ Ø­Ø²ÙØ© ÙØ§ ÙØ¨Ù Ø§ÙØªØµÙÙÙ",
        "warning": "ÙØ±Ø¬Ù Ø¥Ø¯Ø®Ø§Ù Ø§Ø³Ù Ø§ÙÙØ´Ø±ÙØ¹ ÙÙØµÙÙ.",
        "spinner": "Ø¬Ø§Ø±Ù Ø¥Ø¹Ø¯Ø§Ø¯ Ø§ÙØ­Ø²ÙØ© Ø§ÙÙØ¹ÙØ§Ø±ÙØ© ÙØ§ÙØ­Ø³Ø§Ø¨Ø§Øª...",
        "success": "ØªÙ Ø¥ÙØ´Ø§Ø¡ Ø­Ø²ÙØ© ÙØ§ ÙØ¨Ù Ø§ÙØªØµÙÙÙ Ø¨ÙØ¬Ø§Ø­!",
        "limit": "ÙÙØ¯ Ø§Ø³ØªØ®Ø¯ÙØª Ø­Ø²ÙØªÙ Ø§ÙÙØ¬Ø§ÙÙØ©. Ø³ØªØªÙÙØ± Ø§ÙØ®Ø·Ø· Ø§ÙÙØ¯ÙÙØ¹Ø© ÙØ±ÙØ¨ÙØ§.",
        "error": "Ø­Ø¯Ø« Ø®Ø·Ø£ Ø£Ø«ÙØ§Ø¡ Ø¥ÙØ´Ø§Ø¡ Ø§ÙØ­Ø²ÙØ©",
        "program": "Ø¨Ø±ÙØ§ÙØ¬ Ø§ÙÙØ³Ø§Ø­Ø§Øª Ø§ÙÙÙØªØ±Ø­",
        "summary": "ÙÙØ®Øµ Ø§ÙÙØ³Ø§Ø­Ø§Øª",
        "net": "Ø§ÙÙØ³Ø§Ø­Ø© Ø§ÙØµØ§ÙÙØ©",
        "gross": "Ø§ÙÙØ³Ø§Ø­Ø© Ø§ÙØ¨ÙØ§Ø¦ÙØ© Ø§ÙØªÙØ±ÙØ¨ÙØ©",
        "efficiency": "Ø§ÙÙÙØ§Ø¡Ø© Ø§ÙØªÙØ±ÙØ¨ÙØ©",
        "pdf": "ð ØªØ­ÙÙÙ Ø§ÙØ­Ø²ÙØ© PDF",
        "excel": "ð ØªØ­ÙÙÙ Ø¨Ø±ÙØ§ÙØ¬ Ø§ÙÙØ³Ø§Ø­Ø§Øª Excel",
    }
else:
    copy = {
        "intro": (
            "Enter the project information to create a structured, "
            "editable pre-design pack."
        ),
        "project_types": [
            "Residential",
            "Commercial",
            "Office",
            "Hospitality",
            "Educational",
            "Healthcare",
            "Cultural",
            "Mixed-use",
            "Other",
        ],
        "project_type": "Project Type",
        "project_name": "Project Name",
        "location": "City and Country",
        "plot_area": "Approximate Plot Area (mÂ²)",
        "floors": "Number of Floors",
        "budget": "Approximate Budget (Optional)",
        "description": "Project Description and Requirements",
        "location_placeholder": "Example: Riyadh, Saudi Arabia",
        "budget_placeholder": "Example: SAR 3,000,000",
        "description_placeholder": (
            "Describe users, required spaces, style, climate, privacy, "
            "and any special needs."
        ),
        "assumptions": "Area Calculation Assumptions",
        "assumptions_help": (
            "These are editable early-stage allowances, not verified "
            "building-code requirements."
        ),
        "circulation": "Circulation Allowance (%)",
        "services": "Service Allowance (%)",
        "walls": "Walls and Structure Allowance (%)",
        "button": "Create Pre-Design Pack",
        "warning": "Please enter the project name and description.",
        "spinner": "Preparing the architectural pack and calculations...",
        "success": "Pre-design pack created successfully!",
        "limit": (
            "You have used your free pack. Paid plans will be available soon."
        ),
        "error": "An error occurred while creating the pack",
        "program": "Suggested Space Program",
        "summary": "Area Summary",
        "net": "Programmed Net Area",
        "gross": "Approx. Gross Built-up Area",
        "efficiency": "Approx. Efficiency",
        "pdf": "ð Download Pack as PDF",
        "excel": "ð Download Space Program as Excel",
    }

st.write(copy["intro"])

left_column, right_column = st.columns(2)
with left_column:
    project_type = st.selectbox(copy["project_type"], copy["project_types"])
    project_name = st.text_input(copy["project_name"])
    location = st.text_input(
        copy["location"],
        placeholder=copy["location_placeholder"],
    )
    plot_area = st.number_input(
        copy["plot_area"],
        min_value=0,
        value=0,
        step=50,
    )
with right_column:
    floors = st.number_input(
        copy["floors"],
        min_value=1,
        value=1,
        step=1,
    )
    budget = st.text_input(
        copy["budget"],
        placeholder=copy["budget_placeholder"],
    )
    project_description = st.text_area(
        copy["description"],
        height=178,
        placeholder=copy["description_placeholder"],
    )

with st.expander(copy["assumptions"]):
    st.caption(copy["assumptions_help"])
    percentage_columns = st.columns(3)
    with percentage_columns[0]:
        circulation_percentage = st.number_input(
            copy["circulation"],
            min_value=0,
            max_value=50,
            value=15,
            step=1,
        )
    with percentage_columns[1]:
        service_percentage = st.number_input(
            copy["services"],
            min_value=0,
            max_value=50,
            value=10,
            step=1,
        )
    with percentage_columns[2]:
        walls_percentage = st.number_input(
            copy["walls"],
            min_value=0,
            max_value=50,
            value=8,
            step=1,
        )

if st.button(copy["button"], type="primary"):
    if not project_name.strip() or not project_description.strip():
        st.warning(copy["warning"])
    else:
        try:
            usage_response = supabase.rpc("consume_analysis").execute()
            allowed = usage_response.data is True

            if not allowed:
                st.warning(copy["limit"])
            else:
                client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                area_information = (
                    f"{plot_area} mÂ²" if plot_area > 0 else "Not provided"
                )
                budget_information = budget.strip() or "Not provided"
                location_information = location.strip() or "Not provided"
                project_information = f"""
Output Language: {language}
Project Type: {project_type}
Project Name: {project_name}
Location: {location_information}
Approximate Plot Area: {area_information}
Number of Floors: {floors}
Approximate Budget: {budget_information}

Project Description:
{project_description}
"""

                with st.spinner(copy["spinner"]):
                    pack = generate_pack(
                        client,
                        project_information,
                        language,
                    )
                    dataframe, metrics = calculate_space_program(
                        pack["spaces"],
                        circulation_percentage,
                        service_percentage,
                        walls_percentage,
                        language,
                    )
                    percentages = (
                        circulation_percentage,
                        service_percentage,
                        walls_percentage,
                    )
                    report_markdown = build_report_markdown(
                        pack,
                        dataframe,
                        metrics,
                        percentages,
                        language,
                    )
                    st.session_state.generated_pack = {
                        "project_name": project_name,
                        "language": language,
                        "pack": pack,
                        "dataframe": dataframe,
                        "metrics": metrics,
                        "percentages": percentages,
                        "report_markdown": report_markdown,
                    }
        except Exception as error:
            st.error(f"{copy['error']}: {error}")


if "generated_pack" in st.session_state:
    result = st.session_state.generated_pack
    if result["language"] == language:
        st.success(copy["success"])
        metrics = result["metrics"]

        st.subheader(copy["summary"])
        metric_columns = st.columns(3)
        metric_columns[0].metric(copy["net"], f"{metrics['net_area']:.1f} mÂ²")
        metric_columns[1].metric(
            copy["gross"],
            f"{metrics['built_up_area']:.1f} mÂ²",
        )
        metric_columns[2].metric(
            copy["efficiency"],
            f"{metrics['efficiency_ratio']:.1f}%",
        )

        st.subheader(copy["program"])
        st.dataframe(
            result["dataframe"],
            use_container_width=True,
            hide_index=True,
        )

        st.divider()
        st.markdown(result["report_markdown"])

        try:
            pdf_file = create_pdf(
                result["project_name"],
                result["report_markdown"],
                language,
            )
            excel_file = create_excel(
                result["dataframe"],
                result["metrics"],
                result["percentages"],
                language,
            )
            download_columns = st.columns(2)
            with download_columns[0]:
                st.download_button(
                    label=copy["pdf"],
                    data=pdf_file,
                    file_name="architectural_pre_design_pack.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            with download_columns[1]:
                st.download_button(
                    label=copy["excel"],
                    data=excel_file,
                    file_name="architectural_space_program.xlsx",
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),
                    use_container_width=True,
                )
        except Exception as export_error:
            st.warning(f"Export could not be created: {export_error}")
