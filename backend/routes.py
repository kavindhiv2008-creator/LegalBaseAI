from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from backend.schemas import (
    DocumentRequest,
    ExportRequest,
)

from backend.ai_core.gemini_generator import (
    GeminiConfigurationError,
    GeminiDocumentGenerator,
    GeminiGenerationError,
)

from backend.services.exporters import (
    export_docx,
    export_pdf,
    export_txt,
    build_filename,
)


router = APIRouter()


@router.post("/generate")
def generate_document(
    request: DocumentRequest
):

    try:

        generator = (
            GeminiDocumentGenerator()
        )

        content = (
            generator.generate_document(

                document_type=
                request.document_type,

                parties=
                request.parties,

                terms=
                request.terms,

                effective_date=
                request.effective_date,
            )
        )

        return {
            "document_type":
                request.document_type,

            "content":
                content,
        }

    except GeminiConfigurationError as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )

    except GeminiGenerationError as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc)
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=
            f"Unexpected server error: {exc}"
        )


@router.post("/export/txt")
def export_txt_file(
    request: ExportRequest
):

    return Response(

        content=
        export_txt(
            request.content
        ),

        media_type=
        "text/plain; charset=utf-8",

        headers={
            "Content-Disposition":
            (
                "attachment; "
                f'filename="{build_filename(request.document_type, "txt")}"'
            )
        },
    )


@router.post("/export/docx")
def export_docx_file(
    request: ExportRequest
):

    return Response(

        content=
        export_docx(
            request.document_type,
            request.content
        ),

        media_type=
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",

        headers={
            "Content-Disposition":
            (
                "attachment; "
                f'filename="{build_filename(request.document_type, "docx")}"'
            )
        },
    )


@router.post("/export/pdf")
def export_pdf_file(
    request: ExportRequest
):

    return Response(

        content=
        export_pdf(
            request.document_type,
            request.content
        ),

        media_type=
        "application/pdf",

        headers={
            "Content-Disposition":
            (
                "attachment; "
                f'filename="{build_filename(request.document_type, "pdf")}"'
            )
        },
    )