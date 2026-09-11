import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="AI Architecture Tool",
    page_icon="🏗️",
    layout="centered"
)

st.title("🏗️ AI Architecture Tool")
st.subheader("AI-powered architectural project analysis")

st.write(
    "Describe your architectural project below to receive "
    "an organized professional analysis."
)

project_name = st.text_input("Project Name")

project_description = st.text_area(
    "Project Description",
    height=200,
    placeholder=(
        "Example: A residential villa in Riyadh designed "
        "for a family of six..."
    )
)

if st.button("Analyze Project"):
    if not project_name or not project_description:
        st.warning("Please enter the project name and description.")
    else:
        try:
            client = OpenAI(
                api_key=st.secrets["OPENAI_API_KEY"]
            )

            with st.spinner("Analyzing your architectural project..."):
                response = client.responses.create(
                    model="gpt-4.1-mini",
                    instructions="""
You are a professional architectural consultant.

Analyze the project using only the information provided by
the user. Do not invent dimensions, site conditions, budgets,
building codes, or client requirements.

Organize the analysis under these headings:

1. Project Overview
2. Design Concept
3. Space Planning Recommendations
4. Circulation and Accessibility
5. Environmental and Sustainability Strategy
6. Materials and Façade Recommendations
7. Risks and Missing Information
8. Recommended Next Steps

Give practical and specific architectural recommendations.
Clearly identify assumptions and missing information.
Use professional but easy-to-understand language.
""",
                    input=(
                        f"Project Name: {project_name}\n\n"
                        f"Project Description:\n{project_description}"
                    )
                )

            st.success("Analysis completed!")
            st.markdown(response.output_text)

        except Exception as error:
            st.error(f"An error occurred: {error}")