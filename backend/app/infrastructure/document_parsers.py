import base64
import html
import re
import zipfile
from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree

from bs4 import BeautifulSoup

from backend.app.domain.models import DocumentAnalyzeRequest, DocumentFormat, StoryRequest


class DocumentParserError(ValueError):
    pass


class UnsupportedDocumentError(DocumentParserError):
    pass


class ParsedSourceDocument:
    def __init__(self, title: str | None, text: str, document_format: DocumentFormat, metadata: dict[str, str]) -> None:
        self.title = title
        self.text = text
        self.document_format = document_format
        self.metadata = metadata


class BaseDocumentParser(ABC):
    document_format: DocumentFormat

    @abstractmethod
    def parse(self, filename: str, content: bytes) -> ParsedSourceDocument:
        ...

    def _decode_text(self, content: bytes) -> str:
        for encoding in ("utf-8-sig", "utf-8", "utf-16", "cp1252"):
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue
        raise DocumentParserError("Unable to decode text document")

    def _title_from_filename(self, filename: str) -> str:
        return Path(filename).stem.replace("_", " ").replace("-", " ").strip().title() or "Untitled Story"


class TextDocumentParser(BaseDocumentParser):
    document_format = DocumentFormat.txt

    def parse(self, filename: str, content: bytes) -> ParsedSourceDocument:
        return ParsedSourceDocument(
            title=self._title_from_filename(filename),
            text=self._decode_text(content),
            document_format=self.document_format,
            metadata={"parser": "text"},
        )


class MarkdownDocumentParser(BaseDocumentParser):
    document_format = DocumentFormat.markdown

    def parse(self, filename: str, content: bytes) -> ParsedSourceDocument:
        raw = self._decode_text(content)
        headings = re.findall(r"^#\s+(.+)$", raw, flags=re.MULTILINE)
        text = re.sub(r"```.*?```", " ", raw, flags=re.DOTALL)
        text = re.sub(r"`([^`]+)`", r"\1", text)
        text = re.sub(r"!\[[^\]]*]\([^)]+\)", " ", text)
        text = re.sub(r"\[([^\]]+)]\([^)]+\)", r"\1", text)
        text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"[*_~>#-]", " ", text)
        return ParsedSourceDocument(
            title=headings[0].strip() if headings else self._title_from_filename(filename),
            text=text,
            document_format=self.document_format,
            metadata={"parser": "markdown", "heading_count": str(len(headings))},
        )


class HtmlDocumentParser(BaseDocumentParser):
    document_format = DocumentFormat.html

    def parse(self, filename: str, content: bytes) -> ParsedSourceDocument:
        soup = BeautifulSoup(self._decode_text(content), "html.parser")
        for node in soup(["script", "style", "noscript"]):
            node.decompose()
        title = soup.title.string.strip() if soup.title and soup.title.string else self._title_from_filename(filename)
        text = soup.get_text("\n")
        text = html.unescape(re.sub(r"\n{3,}", "\n\n", text))
        return ParsedSourceDocument(
            title=title,
            text=text,
            document_format=self.document_format,
            metadata={"parser": "html"},
        )


class ScriptDocumentParser(BaseDocumentParser):
    document_format = DocumentFormat.script

    def parse(self, filename: str, content: bytes) -> ParsedSourceDocument:
        raw = self._decode_text(content)
        scene_headings = re.findall(r"^(?:INT\.|EXT\.|INT/EXT\.).+$", raw, flags=re.MULTILINE)
        return ParsedSourceDocument(
            title=self._title_from_filename(filename),
            text=raw,
            document_format=self.document_format,
            metadata={"parser": "script", "scene_heading_count": str(len(scene_headings))},
        )


class DocxDocumentParser(BaseDocumentParser):
    document_format = DocumentFormat.docx

    def parse(self, filename: str, content: bytes) -> ParsedSourceDocument:
        paragraphs: list[str] = []
        try:
            with zipfile.ZipFile(BytesIO(content)) as archive:
                xml_bytes = archive.read("word/document.xml")
        except (KeyError, zipfile.BadZipFile) as exc:
            raise DocumentParserError("Invalid DOCX document") from exc

        root = ElementTree.fromstring(xml_bytes)
        namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        for paragraph in root.findall(".//w:p", namespace):
            parts = [node.text or "" for node in paragraph.findall(".//w:t", namespace)]
            text = "".join(parts).strip()
            if text:
                paragraphs.append(text)
        return ParsedSourceDocument(
            title=self._title_from_filename(filename),
            text="\n\n".join(paragraphs),
            document_format=self.document_format,
            metadata={"parser": "docx", "paragraph_count": str(len(paragraphs))},
        )


class EpubDocumentParser(BaseDocumentParser):
    document_format = DocumentFormat.epub

    def parse(self, filename: str, content: bytes) -> ParsedSourceDocument:
        chapters: list[str] = []
        try:
            with zipfile.ZipFile(BytesIO(content)) as archive:
                names = [
                    name
                    for name in archive.namelist()
                    if name.lower().endswith((".xhtml", ".html", ".htm"))
                ]
                for name in names:
                    soup = BeautifulSoup(archive.read(name), "html.parser")
                    for node in soup(["script", "style", "nav"]):
                        node.decompose()
                    chapter_text = soup.get_text("\n").strip()
                    if chapter_text:
                        chapters.append(chapter_text)
        except zipfile.BadZipFile as exc:
            raise DocumentParserError("Invalid EPUB document") from exc
        return ParsedSourceDocument(
            title=self._title_from_filename(filename),
            text="\n\n".join(chapters),
            document_format=self.document_format,
            metadata={"parser": "epub", "html_file_count": str(len(chapters))},
        )


class PdfDocumentParser(BaseDocumentParser):
    document_format = DocumentFormat.pdf

    def parse(self, filename: str, content: bytes) -> ParsedSourceDocument:
        try:
            from pypdf import PdfReader
        except ModuleNotFoundError as exc:
            raise UnsupportedDocumentError("PDF parsing requires the optional 'pypdf' package") from exc

        reader = PdfReader(BytesIO(content))
        pages = [(page.extract_text() or "").strip() for page in reader.pages]
        return ParsedSourceDocument(
            title=self._title_from_filename(filename),
            text="\n\n".join(page for page in pages if page),
            document_format=self.document_format,
            metadata={"parser": "pdf", "page_count": str(len(reader.pages))},
        )


class DocumentIngestionService:
    def __init__(self) -> None:
        self.parsers: dict[DocumentFormat, BaseDocumentParser] = {
            DocumentFormat.txt: TextDocumentParser(),
            DocumentFormat.markdown: MarkdownDocumentParser(),
            DocumentFormat.html: HtmlDocumentParser(),
            DocumentFormat.script: ScriptDocumentParser(),
            DocumentFormat.docx: DocxDocumentParser(),
            DocumentFormat.epub: EpubDocumentParser(),
            DocumentFormat.pdf: PdfDocumentParser(),
        }

    def parse_request(self, request: DocumentAnalyzeRequest) -> tuple[StoryRequest, ParsedSourceDocument]:
        try:
            b64_str = request.content_base64.strip()
            if "," in b64_str:
                b64_str = b64_str.split(",")[1]
            padding = len(b64_str) % 4
            if padding:
                b64_str += "=" * (4 - padding)
            content = base64.b64decode(b64_str)
        except ValueError as exc:
            raise DocumentParserError("content_base64 must be valid base64") from exc
        parsed = self.parse_bytes(request.filename, content)
        story_request = StoryRequest(
            title=request.title or parsed.title,
            text=parsed.text,
            video_style=request.video_style,
            narration_style=request.narration_style,
            target_model=request.target_model,
        )
        return story_request, parsed

    def parse_bytes(self, filename: str, content: bytes) -> ParsedSourceDocument:
        document_format = self._detect_format(filename, content)
        parser = self.parsers.get(document_format)
        if parser is None:
            raise UnsupportedDocumentError(f"Unsupported document format: {document_format}")
        parsed = parser.parse(filename, content)
        if not parsed.text.strip():
            raise DocumentParserError("Parsed document did not contain readable text")
        return parsed

    def _detect_format(self, filename: str, content: bytes) -> DocumentFormat:
        suffix = Path(filename).suffix.lower()
        if suffix == ".pdf":
            return DocumentFormat.pdf
        if suffix == ".docx":
            return DocumentFormat.docx
        if suffix == ".epub":
            return DocumentFormat.epub
        if suffix in {".md", ".markdown"}:
            return DocumentFormat.markdown
        if suffix in {".html", ".htm"}:
            return DocumentFormat.html
        if suffix in {".fountain", ".script", ".screenplay"}:
            return DocumentFormat.script
        if suffix == ".txt":
            text = content[:2048].decode("utf-8", errors="ignore")
            if re.search(r"^(?:INT\.|EXT\.|INT/EXT\.).+$", text, flags=re.MULTILINE):
                return DocumentFormat.script
            return DocumentFormat.txt
        raise UnsupportedDocumentError(f"Unsupported file extension: {suffix or '<none>'}")
