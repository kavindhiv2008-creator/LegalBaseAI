from google import genai
from google.genai import types

from backend.config import get_settings
from backend.utils.text import sanitize_text


class GeminiConfigurationError(
    RuntimeError
):
    pass


class GeminiGenerationError(
    RuntimeError
):
    pass


class GeminiDocumentGenerator:

    SYSTEM_INSTRUCTION = """
You are LegalEase, an AI legal-document drafting assistant.

Your task is to produce a professional LEGAL DOCUMENT DRAFT
from user-provided facts.

Do not invent personal details, dates, addresses, laws,
fees, or obligations that the user did not provide.

When an important legal detail is missing, use a clear
placeholder such as:

[INSERT DETAILS]

instead of guessing.

Rules:

1. Write in formal, clear legal language.

2. Preserve every material user-provided term.

3. Organize the document with a title and numbered sections.

4. Include practical sections appropriate to the requested
document type.

5. Include signature blocks when appropriate.

6. Do not claim that the document is legally valid in every
jurisdiction.

7. Do not provide commentary before or after the document.

8. Return only the document text.

9. Do not invent jurisdiction-specific laws.

10. If governing law is not supplied, use:

[GOVERNING LAW / JURISDICTION]

11. This is a legal-document draft, not legal advice.
"""

    def __init__(self):

        settings = get_settings()

        if not settings.gemini_api_key:

            raise GeminiConfigurationError(
                "GEMINI_API_KEY is missing. "
                "Add it to your .env file."
            )

        self.model = settings.gemini_model

        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
    ) -> str:

        prompt = f"""
Create a draft for this legal document.

DOCUMENT TYPE:
{document_type}

PARTIES:
{parties}

USER-SUPPLIED TERMS AND CONDITIONS:
{terms}

EFFECTIVE DATE:
{effective_date}

Required structure:

- Document title
- Parties / introductory paragraph
- Recitals or purpose when appropriate
- Clearly numbered substantive clauses
- The supplied terms incorporated accurately
- Term and termination where appropriate
- Governing law placeholder if jurisdiction
  was not supplied
- Signature blocks where appropriate

Important:

Do not make up jurisdiction-specific law.

Use:

[GOVERNING LAW / JURISDICTION]

when it was not provided.

Return only the document.
"""

        try:

            response = self.client.models.generate_content(

                model=self.model,

                contents=prompt,

                config=types.GenerateContentConfig(

                    system_instruction=
                    self.SYSTEM_INSTRUCTION,

                    temperature=0.2,

                    max_output_tokens=12000,
                ),
            )

            content = getattr(
                response,
                "text",
                None
            )

            if not content:

                raise GeminiGenerationError(
                    "Gemini returned an empty response."
                )

            return sanitize_text(
                content
            )

        except GeminiGenerationError:

            raise

        except Exception as exc:

            raise GeminiGenerationError(
                f"Gemini generation failed: {exc}"
            ) from exc