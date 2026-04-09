import pymupdf
from typing import Dict


class CVParserService:

    @staticmethod
    def extract_text(file_path: str) -> str:
        """
        Extract full text from PDF
        """
        try:
            doc = pymupdf.open(file_path)
            text = ""

            for page in doc:
                text += page.get_text()

            doc.close()
            return text.strip()

        except Exception as e:
            raise Exception(f"Error extracting text from CV: {str(e)}")


    @staticmethod
    def extract_structured(file_path: str) -> Dict:
        """
        Extract structured blocks (future use: NLP parsing)
        """
        try:
            doc = pymupdf.open(file_path)
            data = []

            for page_num, page in enumerate(doc):
                blocks = page.get_text("blocks")

                for block in blocks:
                    data.append({
                        "page": page_num + 1,
                        "text": block[4],
                        "bbox": block[:4]  # position
                    })

            doc.close()
            return {"blocks": data}

        except Exception as e:
            raise Exception(f"Error extracting structured CV: {str(e)}")