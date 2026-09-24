import streamlit as st
import google.generativeai as genai
from PIL import Image
import fitz  # PyMuPDF

st.set_page_config(page_title="H2 Chem MCQ Topic Identifier", layout="wide")

st.title("🧪 Singapore 9476 H2 Chemistry MCQ Classifier")
st.write("Upload an MCQ paper (PDF) to automatically tag questions with 9476 syllabus topics.")

# Check Streamlit secrets first; if not found, use sidebar input
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    with st.sidebar:
        st.header("Settings")
        api_key = st.text_input("Enter Gemini API Key", type="password")

if not api_key:
    st.warning("Please enter or configure your Gemini API Key to start.")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-3.6-flash')

    uploaded_file = st.file_uploader("Upload MCQ Question Paper (PDF)", type=["pdf"])

    if uploaded_file is not None:
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        st.success(f"Uploaded paper with {len(doc)} pages.")
        
        SYLLABUS = """
        1. Atomic Structure (Subshells, orbitals, ionisation energy)
        2. Chemical Bonding & Structure (VSEPR, intermolecular forces, metallic/ionic/covalent)
        3. The Gaseous State (Ideal gas equation pV=nRT, real gas deviations)
        4. Theories of Acids and Bases (Arrhenius, Brønsted-Lowry, Lewis acids/bases)
        5. The Periodic Table & Periodicity (Period 3 trends, Group 2, Group 17)
        6. The Mole Concept & Stoichiometry (Titration calculations, empirical formulas)
        7. Chemical Energetics (Enthalpy ΔH, Entropy ΔS, Gibbs Free Energy ΔG, Born-Haber cycles)
        8. Reaction Kinetics (Rate equations, orders of reaction, activation energy, catalysts)
        9. Chemical Equilibria (Kc, Kp, Le Chatelier's Principle)
        10a. Acid-Base Equilibria (pH calculations, Ka, Kb, Kw, Buffer solutions, Salt hydrolysis, Titration curves)
        10b. Solubility Equilibria (Solubility Product Ksp, Ionic Product, Common Ion Effect, Selective precipitation)
        11a. Electrochemistry: Galvanic/Voltaic Cells (Standard electrode potentials E°, Nernst, Feasibility ΔG° = -nFE°)
        11b. Electrochemistry: Electrolysis (Faraday's laws, electrolysis calculations, industrial applications)
        12. Introduction to Organic Chemistry & Isomerism (Functional groups, Structural isomerism, Stereoisomerism)
        13. Hydrocarbons (Alkanes, Alkenes, Arenes)
        14. Halogen Derivatives (Halogenoalkanes SN1/SN2, Halogenoarenes)
        15. Hydroxy Compounds (Alcohols, Phenols)
        16. Carbonyl Compounds (Aldehydes, Ketones, Tri-iodomethane, Tollens/Fehling's)
        17. Carboxylic Acids & Derivatives (Carboxylic acids, Acyl chlorides, Esters)
        18. Nitrogen Compounds (Amines, Amides, Amino Acids, Zwitterions)
        19. Polymers (Addition polymerisation, Condensation polymerisation)
        20. Transition Elements (Complexes, Ligand exchange, Variable oxidation states, Colour)
        """

        prompt = f"""
        You are an expert Singapore GCE A-Level H2 Chemistry (Syllabus 9476) tutor.
        Analyze all pages of this MCQ exam paper. Extract EVERY question across all pages and format as Markdown.

        For each question:
        - **Question Number**
        - **Primary Topic**: Must be the EXACT matching topic from: {SYLLABUS}
        - **Secondary Topics**: Any cross-topic tags
        - **Reasoning**: 1 sentence explaining why this topic was selected.
        """

        if st.button("Analyze Entire Paper"):
            with st.spinner("Processing all pages in a single request..."):
                # Collect images of all pages into one list
                contents = [prompt]
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    pix = page.get_pixmap(dpi=150)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    contents.append(f"\n--- PAGE {page_num + 1} ---\n")
                    contents.append(img)

                try:
                    response = model.generate_content(contents)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error processing paper: {e}")
