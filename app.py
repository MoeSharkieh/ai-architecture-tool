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
    "Describe your architectural project below, and the AI will generate "
    "an organized professional analysis."
)

project_name = st.text_input("Project Name")

project_description = st.text_area(
    "Project Description",
    height=200,
    placeholder=(
        "Example: A residential villa in Riyadh on a 600 m² plot, "
        "designed for a family of six..."
    )
)

if st.button("Analyze Project"):
    if not project_name or not project_description:
        st.warning("Please enter the project name and description.")
    else:
        try:
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

            with st.spinner("Analyzing your architectural project..."):
                response = client.responses.create(
                    model="gpt-4.1-mini",
                    instructions=(
                        "You are a professional architect and architectural consultant. "
                        "Analyze the project clearly and practically. "
                        "Organize the response using these sections: "
                        "1. Project Overview, "
                        "2. Design Concept, "
                        "3. Space Planning Recommendations, "
                        "4. Circulation and Accessibility, "
                        "5. Environmental and Sustainability Strategies, "
                        "6. Materials and Façade Recommendations, "
                        "7. Risks and Missing Information, "
                        "8. Recommended Next Steps. "
                        "Use professional language and do not invent regulations, "
                        "dimensions, or site information that the user did not provide."
                    ),
                    input=(
                        f"Project Name: {project_name}\n\n"
                        f"Project Description:\n{project_description}"
                    )
                )

            st.success("Analysis completed!")
            st.markdown(response.output_text)

        except Exception as error:
            st.error(f"An error occurred: {error}")