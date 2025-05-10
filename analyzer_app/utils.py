import os


try:
    from docx import Document as DocxDocument
except ImportError:
    DocxDocument = None 

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None 


def extract_text_from_document(uploaded_file):
    """
    Extracts text from an uploaded file.
    Supports .txt, .pdf, .docx.
    Returns extracted text or an error message string.
    """
    text = ""
    file_name = uploaded_file.name
    file_ext = os.path.splitext(file_name)[1].lower()

    try:
        if file_ext == '.txt':
            text = uploaded_file.read().decode('utf-8', errors='replace')
        elif file_ext == '.docx':
            if DocxDocument:
                try:
                    doc = DocxDocument(uploaded_file)
                    for para in doc.paragraphs:
                        text += para.text + "\n"
                except Exception as e:
                    return f"Error processing DOCX: {e}. Ensure the file is a valid .docx file."
            else:
                return "python-docx library not installed. Cannot process .docx files."
        elif file_ext == '.pdf':
            if PdfReader:
                try:
                    reader = PdfReader(uploaded_file)
                    if reader.is_encrypted: 
                        try:
                            reader.decrypt('') 
                        except Exception:
                            return "Error: PDF is encrypted and cannot be read without a password."

                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text: 
                            text += page_text + "\n"
                    if not text and len(reader.pages) > 0: 
                         return "Could not extract text from PDF. The PDF might be image-based, scanned, or have non-standard text encoding."
                except Exception as e:
                    return f"Error processing PDF: {e}. Ensure the file is a valid .pdf file."
            else:
                return "PyPDF2 library not installed. Cannot process .pdf files."
        else:
            return f"Unsupported file type: {file_ext}. Please upload .txt, .pdf, or .docx."
    except Exception as e:
        return f"An unexpected error occurred during text extraction: {e}"

    if not text.strip(): 
        return "No text could be extracted from the document. It might be empty or in an unreadable format."
    return text
