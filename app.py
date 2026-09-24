import streamlit as st
import google.generativeai as genai
from PIL import Image
import fitz  # PyMuPDF (runs smoothly in cloud environments without external tools)
import json

st.set_page_config(page_title="H2 Chem MCQ Topic Identifier", layout="wide")

st.title("🧪 Singapore 9476 H2 Chemistry MCQ Classifier")
st.write("Upload an MCQ paper (PDF) to automatically tag questions with 9476 syllabus topics.")

# Sidebar API Key configuration
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.markdown("[Get a free API key here](https://aistudio.google.com/)")

if not api_key:
    st.warning("Please enter your Gemini API Key in the sidebar to start.")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash-latest')

    uploaded_file = st.file_uploader("Upload MCQ Question Paper (PDF)", type=["pdf"])

    if uploaded_file is not None:
        # Convert PDF pages to PIL images using PyMuPDF
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        st.success(f"Uploaded paper with {len(doc)} pages.")
        
        SYLLABUS = """
        1. Atomic Structure
        2. Chemical Bonding & Structure
        3. The Gaseous State
        4. Theories of Acids and Bases
        5. The Periodic Table & Periodicity
        6. The Mole Concept & Stoichiometry
        7. Chemical Energetics
        8. Reaction Kinetics
        9. Chemical Equilibria
        10. Chemistry of Aqueous Solutions
        11. Electrochemistry
        12. Introduction to Organic Chemistry & Isomerism
        13. Hydrocarbons (Alkanes, Alkenes, Arenes)
        14. Halogen Derivatives
        15. Hydroxy Compounds (Alcohols & Phenols)
        16. Carbonyl Compounds (Aldehydes & Ketones)
        17. Carboxylic Acids & Derivatives
        18. Nitrogen Compounds (Amines, Amides, Amino Acids)
        19. Polymers
        20. Transition Elements
        """

        prompt = f"""
        You are an expert Singapore GCE A-Level H2 Chemistry (Syllabus 9476) tutor.
        Analyze this page from an MCQ exam paper. Extract every question visible on the page and output a JSON array of objects.
        
        For each question:
        - "question_number": Question label (e.g., "Q1", "Q2")
        - "primary_topic": Must be the EXACT matching topic title from this list: {SYLLABUS}
        - "secondary_topics": List of any secondary or cross-topic tags if applicable
        - "reasoning": 1 sentence explaining why this topic was selected based on key terms or diagrams in the question.

        Output ONLY valid JSON.
        """

        if st.button("Analyze MCQ Paper"):
            for page_num in range(len(doc)):
                page = doc[page_num]
                pix = page.get_pixmap(dpi=150)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                st.subheader(f"📄 Page {page_num + 1}")
                col1, col2 = st.columns([1, 1])

                with col1:
                    st.image(img, caption=f"Page {page_num + 1}", use_container_width=True)

                with col2:
                    with st.spinner("Classifying questions on this page..."):
                        try:
                            response = model.generate_content([prompt, img])
                            st.markdown(response.text)
                        except Exception as e:
                            st.error(f"Error processing page: {e}")
