import streamlit as st

st.set_page_config(
    page_title="AI Architecture Tool",
    page_icon="🏗️",
    layout="centered"
)

st.title("🏗️ AI Architecture Tool")
st.subheader("Your AI assistant for architectural projects")

st.write(
    "Describe your architectural project below. "
    "The AI will help you analyze the requirements and organize your project."
)

project_name = st.text_input("Project Name")

project_description = st.text_area(
    "Describe your project",
    placeholder="Example: Residential building, 5 floors, 20 apartments..."
)

if st.button("Analyze Project"):
    if project_description:
        st.success("Project received successfully!")
        st.write("### Project")
        st.write(project_name)
        st.write("### Description")
        st.write(project_description)
    else:
        st.warning("Please describe your project first.")