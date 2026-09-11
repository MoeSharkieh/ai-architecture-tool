import os
import re
import streamlit as st
from openai import OpenAI
from fpdf import FPDF
from matplotlib import font_manager


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
    return text


def create_pdf(project_name, analysis, language):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    is_arabic = language == "العربية"

    if is_arabic:
        regular_font = font_manager.findfont(
            font_manager.FontProperties(
                family="DejaVu Sans"
            )
        )

        bold_font = font_manager.findfont(
            font_manager.FontProperties(
                family="DejaVu Sans",
                weight="bold"
            )
        )

        if not os.path.exists(regular_font):
            raise FileNotFoundError(
                "Arabic font was not found."
            )

        if not os.path.exists(bold_font):
            raise FileNotFoundError(
                "Arabic bold font was not found."
            )

        pdf.add_font(
            "DejaVu",
            "",
            regular_font
        )

        pdf.add_font(
            "DejaVu",
            "B",
            bold_font
        )

        pdf.set_text_shaping(
            use_shaping_engine=True,
            direction="rtl",
            script="arab",
            language="ara"
        )

        font_name = "DejaVu"
        alignment = "R"

    else:
        font_name = "Helvetica"
        alignment = "L"

    pdf.set_font(font_name, "B", 18)
    pdf.set_text_color(22, 50, 79)

    pdf.multi_cell(
        0,
        10,
        "AI Architecture Tool",
        align=alignment
    )

    pdf.ln(3)

    pdf.set_font(font_name, "B", 14)
    pdf.set_text_color(37, 99, 235)

    pdf.multi_cell(
        0,
        8,
        clean_text_for_pdf(project_name),
        align=alignment
    )

    pdf.ln(5)

    pdf.set_font(font_name, size=11)
    pdf.set_text_color(30, 30, 30)

    clean_analysis = clean_text_for_pdf(analysis)

    for line in clean_analysis.splitlines():
        pdf.set_x(pdf.l_margin)

        if line.strip():
            pdf.multi_cell(
                0,
                7,
                line,
                align=alignment
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
    [data-testid="stTextArea"] textarea,
    [data-testid="stNumberInput"] input {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="main-title">'
    '🏗️ AI Architecture Tool'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-powered architectural project analysis'
    '</div>',
    unsafe_allow_html=True
)

language = st.selectbox(
    "Analysis Language / لغة التحليل",
    ["English", "العربية"]
)

if language == "العربية":
    intro_text = (
        "أدخل معلومات مشروعك المعماري للحصول "
        "على تحليل احترافي ومنظم."
    )

    project_types = [
        "سكني",
        "تجاري",
        "مكاتب",
        "ضيافة وفنادق",
        "تعليمي",
        "صحي",
        "ثقافي",
        "متعدد الاستخدامات",
        "مشروع آخر"
    ]

    project_type_label = "نوع المشروع"
    project_name_label = "اسم المشروع"
    location_label = "المدينة والدولة"
    plot_area_label = "مساحة الأرض التقريبية (م²)"
    floors_label = "عدد الطوابق"
    budget_label = "الميزانية التقريبية (اختياري)"
    description_label = "متطلبات ووصف المشروع"

    location_placeholder = "مثال: الرياض، السعودية"
    budget_placeholder = "مثال: 3,000,000 ريال سعودي"

    description_placeholder = (
        "اذكر الفراغات المطلوبة، عدد المستخدمين، "
        "الطراز، المناخ، الخصوصية والاحتياجات الخاصة."
    )

    button_label = "تحليل المشروع"
    warning_text = "يرجى إدخال اسم المشروع ووصفه."
    spinner_text = "جارٍ تحليل المشروع المعماري..."
    download_label = "📄 تحميل التحليل بصيغة PDF"
    success_text = "تم إنجاز التحليل بنجاح!"
    pdf_error_text = "تم التحليل، لكن تعذر إنشاء PDF"
    error_text = "حدث خطأ أثناء التحليل"

else:
    intro_text = (
        "Enter your project information below to receive "
        "a structured professional analysis."
    )

    project_types = [
        "Residential",
        "Commercial",
        "Office",
        "Hospitality",
        "Educational",
        "Healthcare",
        "Cultural",
        "Mixed-use",
        "Other"
    ]

    project_type_label = "Project Type"
    project_name_label = "Project Name"
    location_label = "City and Country"
    plot_area_label = "Approximate Plot Area (m²)"
    floors_label = "Number of Floors"
    budget_label = "Approximate Budget (Optional)"
    description_label = "Project Description and Requirements"

    location_placeholder = "Example: Riyadh, Saudi Arabia"
    budget_placeholder = "Example: SAR 3,000,000"

    description_placeholder = (
        "Describe the required spaces, number of users, "
        "style, climate, privacy, and special needs."
    )

    button_label = "Analyze Project"

    warning_text = (
        "Please enter the project name and description."
    )

    spinner_text = (
        "Analyzing your architectural project..."
    )

    download_label = "📄 Download Analysis as PDF"
    success_text = "Analysis completed successfully!"

    pdf_error_text = (
        "The analysis is complete, but the PDF "
        "could not be created"
    )

    error_text = "An error occurred during analysis"

st.write(intro_text)

project_type = st.selectbox(
    project_type_label,
    project_types
)

project_name = st.text_input(
    project_name_label
)

location = st.text_input(
    location_label,
    placeholder=location_placeholder
)

plot_area = st.number_input(
    plot_area_label,
    min_value=0,
    value=0,
    step=50
)

floors = st.number_input(
    floors_label,
    min_value=1,
    value=1,
    step=1
)

budget = st.text_input(
    budget_label,
    placeholder=budget_placeholder
)

project_description = st.text_area(
    description_label,
    height=220,
    placeholder=description_placeholder
)

if st.button(
    button_label,
    type="primary"
):
    if (
        not project_name.strip()
        or not project_description.strip()
    ):
        st.warning(warning_text)

    else:
        try:
            client = OpenAI(
                api_key=st.secrets["OPENAI_API_KEY"]
            )

            if language == "العربية":
                language_instructions = """
اكتب التحليل كاملًا باللغة العربية الفصحى الواضحة.

ابدأ بالعنوان:
# تحليل المشروع المعماري

ثم اعرض اسم المشروع بخط عريض.

استخدم عناوين الأقسام التالية حرفيًا:

## 1. نظرة عامة على المشروع
## 2. الفكرة التصميمية
## 3. توصيات توزيع الفراغات
## 4. الحركة وسهولة الوصول
## 5. الاستراتيجية البيئية والاستدامة
## 6. توصيات المواد والواجهات
## 7. المخاطر والمعلومات الناقصة
## 8. الخطوات التالية الموصى بها
"""
            else:
                language_instructions = """
Write the entire analysis in clear professional English.

Begin with:
# Architectural Project Analysis

Then show the project name in bold.

Use these exact section headings:

## 1. Project Overview
## 2. Design Concept
## 3. Space Planning Recommendations
## 4. Circulation and Accessibility
## 5. Environmental and Sustainability Strategy
## 6. Materials; Materials and Façade Recommendations
## 7. Risks and Missing Information
## 8. Recommended Next Steps
"""

            area_information = (
                f"{plot_area} m²"
                if plot_area > 0
                else "Not provided"
            )

            budget_information = (
                budget.strip()
                if budget.strip()
                else "Not provided"
            )

            location_information = (
                location.strip()
                if location.strip()
                else "Not provided"
            )

            project_information = f"""
Project Type: {project_type}
Project Name: {project_name}
Location: {location_information}
Approximate Plot Area: {area_information}
Number of Floors: {floors}
Approximate Budget: {budget_information}

Project Description:
{project_description}
"""

            with st.spinner(spinner_text):
                response = client.responses.create(
                    model="gpt-4.1-mini",
                    instructions=f"""
You are a professional architectural consultant.

Analyze the project using only the information
provided by the user.

Do not invent dimensions, site conditions, budgets,
building codes, or client requirements.

Format the answer using clean Markdown.

{language_instructions}

Use short paragraphs and bullet points.
Make important recommendations bold.
Keep every section clear and practical.
Clearly identify assumptions and missing information.
Do not add a conclusion after section 8.
""",
                    input=project_information
                )

            analysis = response.output_text

            st.success(success_text)
            st.divider()

            with st.container(border=True):
                st.markdown(analysis)

            try:
                pdf_file = create_pdf(
                    project_name,
                    analysis,
                    language
                )

                st.download_button(
                    label=download_label,
                    data=pdf_file,
                    file_name="architectural_analysis.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            except Exception as pdf_error:
                st.warning(
                    f"{pdf_error_text}: {pdf_error}"
                )

        except Exception as error:
            st.error(
                f"{error_text}: {error}"
            )