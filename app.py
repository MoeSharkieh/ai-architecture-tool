import streamlit as st

st.set_page_config(
    page_title="AI Architecture Tool",
    page_icon="🏗️",
    layout="centered"
)

st.title("🏗️ AI Architecture Tool")
st.subheader("Your AI assistant for architectural projects")

st.write(
    "Describe your architectural project below and the AI will help you "
    "analyze the requirements and organize the project."
)

project_name = st.text_input("Project Name")

project_type = st.selectbox(
    "Project Type",
    [
        "Residential",
        "Commercial",
        "Office",
        "Hospitality",
        "Educational",
        "Healthcare",
        "Mixed Use",
        "Other"
    ]
)

project_description = st.text_area(
    "Describe your project",
    placeholder="Example: Design a modern 3-bedroom villa on a 500 sqm plot..."
)

if st.button("Generate Analysis"):
    if project_description:
        st.success("Project received successfully ✅")

        st.write("### Project Summary")
        st.write(f"**Project Name:** {project_name or 'Untitled Project'}")
        st.write(f"**Project Type:** {project_type}")
        st.write(f"**Description:** {project_description}")

        st.info(
            "AI analysis will be connected in the next step."
        )
    else:
        st.warning("Please enter a project description.")
