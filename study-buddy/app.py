import streamlit as st
import fitz
import google.generativeai as genai
from graphviz import Digraph

# ====================================
# Gemini API
# ====================================

genai.configure(api_key="AIzaSyDdl-pMnKQ5ufDydmo4vc0Wb8uiCbhZUYA")

model = genai.GenerativeModel("gemini-2.0-flash")

# ====================================
# Title
# ====================================

st.title("🎓 AI Study Buddy")

st.write(
    "Upload materi PDF lalu AI akan membuat:"
)

st.write("""
✅ Ringkasan  
✅ Penjelasan sederhana  
✅ Quiz otomatis  
✅ Mind Map  
""")

# ====================================
# Upload PDF
# ====================================

uploaded_file = st.file_uploader(
    "Upload PDF",
    type=["pdf"]
)

# ====================================
# Process
# ====================================

if uploaded_file:

    text = ""

    pdf = fitz.open(
        stream=uploaded_file.read(),
        filetype="pdf"
    )

    for page in pdf:
        text += page.get_text()

    st.success("PDF berhasil diproses")

    shortened_text = text[:12000]

    # ====================================
    # SUMMARY
    # ====================================

    with st.spinner("Membuat ringkasan..."):

        summary_prompt = f"""
        Jelaskan materi berikut dengan bahasa sederhana.

        Materi:
        {shortened_text}

        Berikan:
        1. Ringkasan
        2. Poin penting
        3. Penjelasan sederhana
        """

        summary_response = model.generate_content(
            summary_prompt
        )

        st.subheader("📘 Ringkasan Materi")

        st.write(summary_response.text)

    # ====================================
    # QUIZ
    # ====================================

    with st.spinner("Membuat quiz..."):

        quiz_prompt = f"""
        Buat 5 soal pilihan ganda dari materi berikut.

        Materi:
        {shortened_text}

        Format:
        Soal
        A.
        B.
        C.
        D.

        Jawaban:
        Pembahasan:
        """

        quiz_response = model.generate_content(
            quiz_prompt
        )

        st.subheader("❓ Quiz Otomatis")

        st.write(quiz_response.text)

    # ====================================
    # MIND MAP
    # ====================================

    with st.spinner("Membuat mind map..."):

        mindmap_prompt = f"""
        Dari materi berikut, buat struktur mind map.

        Format:
        Topik Utama -> Subtopik

        Contoh:
        Machine Learning -> Supervised Learning

        Materi:
        {shortened_text}
        """

        mindmap_response = model.generate_content(
            mindmap_prompt
        )

        st.subheader("🧠 Mind Map")

        st.code(mindmap_response.text)

        # ====================================
        # Generate Graph
        # ====================================

        dot = Digraph()

        lines = mindmap_response.text.split("\n")

        for line in lines:

            if "->" in line:

                parts = line.split("->")

                parent = parts[0].strip()
                child = parts[1].strip()

                dot.node(parent)
                dot.node(child)

                dot.edge(parent, child)

        st.graphviz_chart(dot)