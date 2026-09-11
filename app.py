import streamlit as st
from openai import OpenAI

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
        st.warning("Please enter the project name and description.")
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
                        f"Project Description:\n{project_description}"
                    )
                )

            st.success("Analysis completed successfully!")

            st.divider()

            with st.container(border=True):
                st.markdown(response.output_text)

        except Exception as error:
            st.error(f"An error occurred: {error}")