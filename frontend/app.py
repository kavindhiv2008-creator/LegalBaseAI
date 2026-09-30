import os
import html
from datetime import date

import requests
import streamlit as st

from dotenv import load_dotenv


load_dotenv()


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
)


st.set_page_config(

    page_title="LegalEase",

    page_icon="⚖️",

    layout="wide",

    initial_sidebar_state="expanded",
)


# -----------------------------
# Custom CSS
# -----------------------------

st.markdown(
    """
<style>

.hero {

    padding: 1.2rem 1.4rem;

    border-radius: 18px;

    background:
        linear-gradient(
            135deg,
            #111827,
            #312e81
        );

    color: white;

    margin-bottom: 1.2rem;
}


.hero h1 {

    margin: 0;

    font-size: 2.25rem;

}


.hero p {

    margin: .35rem 0 0;

    opacity: .86;

}


.preview {

    background: #0b1020;

    color: #f3f4f6;

    border: 1px solid #26304a;

    border-radius: 14px;

    padding: 1.1rem;

    max-height: 650px;

    overflow-y: auto;

    line-height: 1.65;

    font-family:
        Georgia,
        "Times New Roman",
        serif;
}


.small-note {

    color: #6b7280;

    font-size: .88rem;

}

</style>
""",
    unsafe_allow_html=True
)


# -----------------------------
# Session State
# -----------------------------

if "generated" not in st.session_state:

    st.session_state.generated = ""


if "document_type" not in st.session_state:

    st.session_state.document_type = ""


# -----------------------------
# Sidebar
# -----------------------------

with st.sidebar:

    st.markdown(
        "### LegalEase"
    )

    st.caption(
        "AI-powered legal document drafting"
    )

    st.divider()

    st.markdown(
        "**Supported drafts**"
    )

    st.write(
        "• Agreements"
    )

    st.write(
        "• Contracts"
    )

    st.write(
        "• NDAs"
    )

    st.write(
        "• Lease agreements"
    )

    st.write(
        "• Employment letters"
    )

    st.write(
        "• Custom legal drafts"
    )

    st.divider()

    st.warning(
        "LegalEase produces drafts and "
        "legal information, not legal advice. "
        "Review important documents with a "
        "qualified lawyer before signing."
    )


# -----------------------------
# Header
# -----------------------------

st.markdown(
    """
<div class="hero">

    <h1>⚖️ LegalEase</h1>

    <p>
        Create editable AI-assisted legal
        document drafts and export them
        in multiple formats.
    </p>

</div>
""",
    unsafe_allow_html=True
)


# -----------------------------
# Layout
# -----------------------------

left, right = st.columns(
    [0.95, 1.05],
    gap="large"
)


# -----------------------------
# INPUT SECTION
# -----------------------------

with left:

    st.subheader(
        "1. Document details"
    )


    document_type = st.text_input(

        "Document type",

        value=
        st.session_state.document_type,

        placeholder=
        "e.g. Freelance Work Contract"
    )


    parties = st.text_area(

        "Parties involved",

        placeholder=
        "e.g. Jane Doe (Service Provider), "
        "TechNova Inc. (Client)",

        height=110
    )


    terms = st.text_area(

        "Terms & conditions",

        placeholder=(
            "Separate terms with semicolons.\n"
            "Payment within 30 days; "
            "Confidentiality must be maintained; "
            "Either party may terminate with "
            "30 days notice"
        ),

        height=170
    )


    effective_date = st.text_input(

        "Effective date",

        value=
        date.today().isoformat(),

        placeholder=
        "YYYY-MM-DD or a written date"
    )


    generate = st.button(

        "✨ Generate Document",

        type="primary",

        use_container_width=True
    )


    # -----------------------------
    # Generate
    # -----------------------------

    if generate:

        missing = []


        if not document_type.strip():

            missing.append(
                "Document type"
            )


        if not parties.strip():

            missing.append(
                "Parties involved"
            )


        if not terms.strip():

            missing.append(
                "Terms & conditions"
            )


        if not effective_date.strip():

            missing.append(
                "Effective date"
            )


        if missing:

            st.error(
                "Please fill: "
                + ", ".join(missing)
            )


        else:

            payload = {

                "document_type":
                    document_type.strip(),

                "parties":
                    parties.strip(),

                "terms":
                    terms.strip(),

                "effective_date":
                    effective_date.strip(),
            }


            try:

                with st.spinner(
                    "Generating your legal draft..."
                ):

                    response = requests.post(

                        f"{BACKEND_URL}/generate",

                        json=payload,

                        timeout=120
                    )


                if response.ok:

                    data = response.json()


                    st.session_state.generated = (
                        data["content"]
                    )


                    st.session_state.document_type = (
                        document_type.strip()
                    )


                    st.success(
                        "Document generated successfully."
                    )


                else:

                    try:

                        detail = (
                            response
                            .json()
                            .get(
                                "detail",
                                response.text
                            )
                        )

                    except Exception:

                        detail = response.text


                    st.error(
                        f"Backend error "
                        f"({response.status_code}): "
                        f"{detail}"
                    )


            except requests.RequestException as exc:

                st.error(

                    "Could not connect to FastAPI. "

                    f"Make sure the backend is running "
                    f"at {BACKEND_URL}. "

                    f"Details: {exc}"
                )


# -----------------------------
# OUTPUT SECTION
# -----------------------------

with right:

    st.subheader(
        "2. Editable document"
    )


    if st.session_state.generated:

        edited = st.text_area(

            "Edit the generated document "
            "before export",

            value=
            st.session_state.generated,

            height=520,

            key="editor"
        )


        st.session_state.generated = (
            edited
        )


        # -----------------------------
        # Preview
        # -----------------------------

        st.markdown(
            "**Live preview**"
        )


        preview = (
            html.escape(
                edited
            )
            .replace(
                "\n\n",
                "</p><p>"
            )
            .replace(
                "\n",
                "<br>"
            )
        )


        st.markdown(

            f"""
            <div class="preview">
                <p>{preview}</p>
            </div>
            """,

            unsafe_allow_html=True
        )


        # -----------------------------
        # Downloads
        # -----------------------------

        st.subheader(
            "3. Download"
        )


        export_payload = {

            "document_type":
                (
                    st.session_state.document_type
                    or "Legal Document"
                ),

            "content":
                st.session_state.generated
        }


        cols = st.columns(3)


        export_options = [

            (
                cols[0],
                "⬇️ TXT",
                "export/txt",
                "legal_document.txt",
                "text/plain"
            ),

            (
                cols[1],
                "⬇️ DOCX",
                "export/docx",
                "legal_document.docx",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ),

            (
                cols[2],
                "⬇️ PDF",
                "export/pdf",
                "legal_document.pdf",
                "application/pdf"
            ),
        ]


        for (
            col,
            label,
            endpoint,
            filename,
            mime
        ) in export_options:

            try:

                result = requests.post(

                    f"{BACKEND_URL}/{endpoint}",

                    json=export_payload,

                    timeout=60
                )


                if result.ok:

                    with col:

                        st.download_button(

                            label,

                            data=result.content,

                            file_name=filename,

                            mime=mime,

                            use_container_width=True
                        )


                else:

                    col.error(
                        f"{label} export failed."
                    )


            except requests.RequestException:

                col.error(
                    "Backend offline."
                )


    else:

        st.info(
            "Your generated document "
            "will appear here."
        )


        st.markdown(

            """
            <p class="small-note">
            Tip: Use semicolons to separate
            the specific terms you want included
            in the draft.
            </p>
            """,

            unsafe_allow_html=True
        )


# -----------------------------
# Footer
# -----------------------------

st.divider()


st.caption(
    "LegalEase • Drafting assistant • "
    "Always verify important legal documents "
    "with a qualified professional."
)