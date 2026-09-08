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
    "Describe your architectural project below and receive "
    "an organized professional analysis."
)

project_name = st.text_input("Project Name")

project_description = st.text_area(
    "Describe your project",
    placeholder="Example: Residential building, 5 floors, 20 apartments, Riyadh..."
)

if st.button("Analyze Project"):

    if not project_description:
        st.warning("Please describe your project first.")

    else:
        try:
            client = OpenAI(
                api_key=st.secrets["OPENAI_API_KEY"]
            )

            with st.spinner("Analyzing your project..."):

                response = client.responses.create(
                    model="gpt-5.6-luna",
                    input=f"""
You are a professional architectural consultant.

Analyze the following architectural project.

Project Name:
{project_name}

Project Description:
{project_description}

Prepare a clear professional report including:

1. Project Overview
2. Main Architectural Requirements
3. Suggested Spaces and Functions
4. Design Considerations
5. Circulation and Accessibility
6. Sustainability Recommendations
7. Potential Design Challenges
8. Recommended Next Steps

Make the analysis useful for an architect preparing an early-stage project proposal.
"""
                )

            st.success("Analysis completed!")

            st.write("## AI Architectural Analysis")
            st.write(response.output_text)

        except Exception as e:
            st.error("Something went wrong.")
            st.error(str(e))
