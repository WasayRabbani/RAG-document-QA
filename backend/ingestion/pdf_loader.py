import json
from pathlib import Path
import pymupdf


class PDFLoader:

    # 1. Load PDF files
    def __init__(self, path: str):
        self.path = Path(path)

        if not self.path.exists():
            raise FileNotFoundError(f"Path does not exist: {self.path}")

        # B0
        if self.path.is_file():
            self.pdf_files = [self.path] # pdf_files stores address of every single pdf in a list

        elif self.path.is_dir():
            self.pdf_files = list(self.path.glob("*.pdf"))

        else:
            raise ValueError("Invalid path")

        if not self.pdf_files:
            raise FileNotFoundError("No PDF files found")

        # B0

    # 2. Process all PDF files
    def process_all(self):
        documents = {}
        errors = {}

        for pdf_path in self.pdf_files:
            try:
                document = self.process_pdf(pdf_path)
                documents[pdf_path.name] = document

            except Exception as exc:
                errors[pdf_path.name] = str(exc)

        return {
            "documents": documents,
            "errors": errors
        }

    # 3. Process one PDF file
    def process_pdf(self, pdf_path: Path):
        with pymupdf.open(pdf_path) as doc:

            document = self.extract_document_metadata(doc, pdf_path)

            for page_num, page in enumerate(doc, start=1):
                page_record = self.build_page_record(page, page_num)
                document["pages"].append(page_record)

            self.validate_document(document)

            output_path = Path("output") / f"{pdf_path.stem}.json"
            self.save_json(document, output_path)

            return document

    # 4. Extract document metadata
    def extract_document_metadata(self, doc, pdf_path: Path):
        return {
            "file_name": pdf_path.name,
            "total_pages": doc.page_count,
            "metadata": doc.metadata or {},
            "pages": [],
            "warnings": []
        }

    # 5. Extract tables and their coordinates
    def extract_tables_from_page(self, page):
        found_tables = page.find_tables()

        tables = []
        table_bboxes = []

        for table_num, table in enumerate(found_tables.tables, start=1):
            tables.append({
                "table_num": table_num,
                "data": table.extract()
            })

            table_bboxes.append(table.bbox)

        return tables, table_bboxes

    # 6. Extract text while excluding table areas
    def extract_text_excluding_tables(self, page, table_bboxes):
        words = page.get_text("words", sort=True)

        lines = {}

        for word in words:
            x0, y0, x1, y1, text, block_num, line_num, word_num = word[:8]

            center_x = (x0 + x1) / 2
            center_y = (y0 + y1) / 2

            inside_table = False

            for bbox in table_bboxes:
                tx0, ty0, tx1, ty1 = bbox

                if tx0 <= center_x <= tx1 and ty0 <= center_y <= ty1:
                    inside_table = True
                    break

            if not inside_table:
                line_key = (block_num, line_num)

                if line_key not in lines:
                    lines[line_key] = []

                lines[line_key].append((word_num, text))

        text_lines = []

        for line_words in lines.values():
            line_words.sort(key=lambda item: item[0])
            text_lines.append(
                " ".join(word for word_num, word in line_words)
            )

        return "\n".join(text_lines)

    # 7. Build one page record
    def build_page_record(self, page, page_num):
        tables, table_bboxes = self.extract_tables_from_page(page)

        text = self.extract_text_excluding_tables(page, table_bboxes)

        return {
            "page_num": page_num,
            "text": text,
            "character_count": len(text),
            "tables": tables,
            "warnings": []
        }

    # 8. Validate the document
    def validate_document(self, document):
        if len(document["pages"]) != document["total_pages"]:
            document["warnings"].append("Page count mismatch")

        for page in document["pages"]:
            if not page["text"].strip() and not page["tables"]:
                page["warnings"].append(
                    "No text or tables extracted"
                )

    # 9. Save JSON file
    def save_json(self, document, output_path):
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(document, file, indent=2, ensure_ascii=False)


# Run the pipeline
obj = PDFLoader("/home/wasay-rabbani/Desktop/Test Pdfs")

result = obj.process_all()


print("Processed PDFs:", list(result["documents"].keys()))
print("Errors:", result["errors"])