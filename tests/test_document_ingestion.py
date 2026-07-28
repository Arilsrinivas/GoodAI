import base64
import zipfile
from io import BytesIO
import unittest

from backend.app.domain.models import DocumentAnalyzeRequest, DocumentFormat
from backend.app.infrastructure.document_parsers import DocumentIngestionService


class DocumentIngestionServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.service = DocumentIngestionService()

    def test_markdown_parser_preserves_title_and_text(self) -> None:
        request = DocumentAnalyzeRequest(
            filename="story.md",
            content_base64=base64.b64encode(b"# A Good Road\n\nMira found a letter.").decode("ascii"),
        )

        story_request, parsed = self.service.parse_request(request)

        self.assertEqual(parsed.document_format, DocumentFormat.markdown)
        self.assertEqual(story_request.title, "A Good Road")
        self.assertIn("Mira found a letter", story_request.text)

    def test_html_parser_extracts_readable_text(self) -> None:
        parsed = self.service.parse_bytes(
            "story.html",
            b"<html><head><title>Harbor</title><script>bad()</script></head><body><p>Asha waited.</p></body></html>",
        )

        self.assertEqual(parsed.title, "Harbor")
        self.assertIn("Asha waited", parsed.text)
        self.assertNotIn("bad()", parsed.text)

    def test_docx_parser_reads_document_xml(self) -> None:
        content = BytesIO()
        document_xml = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            "<w:body><w:p><w:r><w:t>Mira crossed the bridge.</w:t></w:r></w:p></w:body>"
            "</w:document>"
        )
        with zipfile.ZipFile(content, "w") as archive:
            archive.writestr("word/document.xml", document_xml)

        parsed = self.service.parse_bytes("sample.docx", content.getvalue())

        self.assertEqual(parsed.document_format, DocumentFormat.docx)
        self.assertIn("Mira crossed the bridge", parsed.text)


if __name__ == "__main__":
    unittest.main()

