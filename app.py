import streamlit as st
import fitz
import google.generativeai as genai
from graphviz import Digraph
import time

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="🎓",
    layout="wide"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>
.main {
    padding-top: 2rem;
}

.stButton button {
    width: 100%;
    border-radius: 10px;
    height: 50px;
    font-size: 16px;
    font-weight: bold;
}

.block-container {
    padding-top: 2rem;
}

[data-testid="stMetricValue"] {
    font-size: 20px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# API CONFIG
# =====================================================

API_KEY = st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=API_KEY)

# =====================================================
# MODEL
# =====================================================

model = genai.GenerativeModel(
    "gemini-1.5-flash"
)

# =====================================================
# TITLE
# =====================================================

st.title("🎓 AI Study Buddy")

st.markdown("""
AI assistant untuk membantu siswa memahami materi PDF secara otomatis.

### Features
- 📘 Ringkasan materi
- 📌 Poin penting
- ❓ Quiz otomatis
- 🧠 AI Mind Map
- 💬 Chat dengan PDF
""")

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("⚙️ Pengaturan")

difficulty = st.sidebar.selectbox(
    "Tingkat Penjelasan",
    [
        "Anak SD",
        "SMP",
        "SMA",
        "Mahasiswa"
    ]
)

# =====================================================
# FILE UPLOADER
# =====================================================

uploaded_file = st.file_uploader(
    "Upload PDF Materi",
    type=["pdf"]
)

# =====================================================
# EXTRACT PDF TEXT
# =====================================================

def extract_text_from_pdf(pdf_file):

    text = ""

    pdf = fitz.open(
        stream=pdf_file.read(),
        filetype="pdf"
    )

    for page in pdf:
        text += page.get_text()

    return text

# =====================================================
# GENERATE AI CONTENT
# =====================================================

@st.cache_data(show_spinner=False)
def generate_ai_content(text, difficulty_level):

    shortened_text = text[:4000]

    combined_prompt = f"""
    Kamu adalah AI tutor pendidikan.

    Jelaskan materi berikut untuk level:
    {difficulty_level}

    Materi:
    {shortened_text}

    Berikan output dengan format berikut:

    # RINGKASAN
    Buat ringkasan singkat dan jelas.

    # POIN PENTING
    Buat poin-poin utama materi.

    # QUIZ
    Buat 5 soal pilihan ganda beserta jawaban dan pembahasan.

    # MINDMAP
    Buat format:
    Topik Utama -> Subtopik

    Contoh:
    Machine Learning -> Supervised Learning
    """

    try:

        response = model.generate_content(
            combined_prompt,
            generation_config={
                "temperature": 0.5,
                "max_output_tokens": 1024
            }
        )

        return response.text

    except Exception as e:

        return f"ERROR: {str(e)}"

# =====================================================
# GENERATE CHAT RESPONSE
# =====================================================

def ask_question(question, context):

    shortened_context = context[:3000]

    prompt = f"""
    Jawab pertanyaan berdasarkan materi berikut.

    Materi:
    {shortened_context}

    Pertanyaan:
    {question}
    """

    try:

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.5,
                "max_output_tokens": 512
            }
        )

        return response.text

    except Exception as e:

        return f"ERROR: {str(e)}"

# =====================================================
# MAIN PROCESS
# =====================================================

if uploaded_file:

    with st.spinner("📄 Membaca PDF..."):

        pdf_text = extract_text_from_pdf(
            uploaded_file
        )

        time.sleep(1)

    st.success("PDF berhasil diproses")

    # =================================================
    # GENERATE CONTENT
    # =================================================

    with st.spinner("🤖 AI sedang menganalisa materi..."):

        result = generate_ai_content(
            pdf_text,
            difficulty
        )

        time.sleep(1)

    # =================================================
    # ERROR HANDLING
    # =================================================

    if result.startswith("ERROR"):

        st.error(result)

        st.warning("""
        Kemungkinan penyebab:
        - Quota Gemini habis
        - API Key salah
        - PDF terlalu besar
        - Terlalu banyak request
        """)

        st.stop()

    # =================================================
    # DISPLAY RESULT
    # =================================================

    tabs = st.tabs([
        "📘 Ringkasan",
        "❓ Quiz",
        "🧠 Mind Map",
        "💬 Chat PDF"
    ])

    # =================================================
    # SUMMARY TAB
    # =================================================

    with tabs[0]:

        st.markdown(result)

    # =================================================
    # QUIZ TAB
    # =================================================

    with tabs[1]:

        if "# QUIZ" in result:

            quiz_section = result.split("# QUIZ")[1]

            if "# MINDMAP" in quiz_section:
                quiz_section = quiz_section.split("# MINDMAP")[0]

            st.markdown(quiz_section)

        else:

            st.warning("Quiz tidak ditemukan")

    # =================================================
    # MINDMAP TAB
    # =================================================

    with tabs[2]:

        if "# MINDMAP" in result:

            mindmap_section = result.split("# MINDMAP")[1]

            st.code(mindmap_section)

            dot = Digraph()

            lines = mindmap_section.split("\n")

            for line in lines:

                if "->" in line:

                    try:

                        parts = line.split("->")

                        parent = parts[0].strip()
                        child = parts[1].strip()

                        dot.node(parent)
                        dot.node(child)

                        dot.edge(parent, child)

                    except:
                        pass

            st.graphviz_chart(dot)

        else:

            st.warning("Mind map tidak ditemukan")

    # =================================================
    # CHAT PDF
    # =================================================

    with tabs[3]:

        st.subheader("💬 Tanya AI")

        user_question = st.text_input(
            "Tanyakan isi materi"
        )

        if st.button("Kirim Pertanyaan"):

            if user_question:

                with st.spinner("AI sedang menjawab..."):

                    answer = ask_question(
                        user_question,
                        pdf_text
                    )

                    st.write(answer)

    # =================================================
    # DOWNLOAD RESULT
    # =================================================

    st.download_button(
        label="⬇️ Download Hasil",
        data=result,
        file_name="study_buddy_result.txt",
        mime="text/plain"
    )

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.caption("""
Built with:
- Gemini API
- Streamlit
- Graphviz
- PyMuPDF
""")