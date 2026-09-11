import re
import streamlit as st
from openai import OpenAI
from fpdf import FPDF


def clean_text_for_pdf(text):
    text = re.sub(r"#{1,6}\s*", "", text)
    text = text.replace("**", "")
    text = text.replace("*", "")
    text = text.replace("•", "-")
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = text.replace("’", "'")
    text = text.replace("“", '"')
    text = text.replace("”", '"')

    return text.encode(
        "latin-1",
        errors="replace"
    ).decode("latin-1")


def create_pdf(project_name, analysis):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(22, 50, 79)
    pdf.multi_cell(
        0,
        10,
        "AI Architecture Tool"
    )

    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(37, 99, 235)
    pdf.multi_cell(
        0,
        8,
        clean_text_for_pdf(project_name)
    )

    pdf.ln(5)

    pdf.set_font("Helvetica", size=11)
    pdf.set_text_color(30, 30, 30)

    clean_analysis = clean_text_for_pdf(analysis)

    for line in clean_analysis.splitlines():
        pdf.set_x(pdf.l_margin)

        if line.strip():
            pdf.multi_cell(
                0,
                7,
                line
            )
        else:
            pdf.ln(3)

    return bytes(pdf.output())


st.set_page_config(
    page_title="AI Architecture Tool",
    page_icon="🏗️",
    layout="centered"
)

st.markdown("""
<style>
    .stApp {
        background-color: #f7f9fc;
    }

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

    .stButton > button {
        width: 100%;
        background-color: #2563eb;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px;
        font-size: 17px;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #1d4ed8;
        color: white;
    }

    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="main-title">🏗️ AI Architecture Tool</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Professional AI-powered architectural project analysis'
    '</div>',
    unsafe_allow_html=True
)

st.info(
    "Describe your architectural project below to receive a "
    "structured professional analysis."
)

project_name = st.text_input(
    "Project Name",
    placeholder="Example: Modern Family Villa in Riyadh"
)

project_description = st.text_area(
    "Project Description",
    height=220,
    placeholder=(
        "Describe the location, plot size, building type, spaces, "
        "design requirements, climate, style, and special needs."
    )
)

if st.button("Analyze Project", type="primary"):
    if not project_name.strip() or not project_description.strip():
        st.warning(
            "Please enter the project name and description."
        )
    else:
        try:
            client = OpenAI(
                api_key=st.secrets["OPENAI_API_KEY"]
            )

            with st.spinner(
                "Analyzing your architectural project..."
            ):
                response = client.responses.create(
                    model="gpt-4.1-mini",
                    instructions="""
You are a professional architectural consultant.

Analyze the project using only the information provided by
the user. Do not invent dimensions, site conditions, budgets,
building codes, or client requirements.

Format the answer using clean Markdown.

Begin with:
# Architectural Project Analysis

Then show the project name in bold.

Use these exact section headings:

## 1. Project Overview
## 2. Design Concept
## 3. Space Planning Recommendations
## 4. Circulation and Accessibility
## 5. Environmental and Sustainability Strategy
## 6. Materials and Façade Recommendations
## 7. Risks and Missing Information
## 8. Recommended Next Steps

Use short paragraphs and bullet points.
Make important recommendations bold.
Keep every section clear, practical, and easy to scan.
Clearly identify assumptions and missing information.
Use professional but easy-to-understand language.
Do not add a conclusion after section 8.
""",
                    input=(
                        f"Project Name: {project_name}\n\n"
                        f"Project Description:\n"
                        f"{project_description}"
                    )
                )

            analysis = response.output_text

            st.success("Analysis completed successfully!")
            st.divider()

            with st.container(border=True):
                st.markdown(analysis)

            pdf_file = create_pdf(
                project_name,
                analysis
            )

            st.download_button(
                label="📄 Download Analysis as PDF",
                data=pdf_file,
                file_name="architectural_analysis.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        except Exception as error:
            st.error(f"An error occurred: {error}")