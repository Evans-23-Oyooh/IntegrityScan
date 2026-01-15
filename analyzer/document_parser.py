import os
import subprocess
import tempfile

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


class DocumentParser:
    @staticmethod
    def extract_text_from_file(file):
        file_extension = os.path.splitext(file.name)[1].lower()
        file.seek(0)
        
        if file_extension == '.txt':
            content = file.read()
            return content.decode('utf-8', errors='ignore').strip() if isinstance(content, bytes) else str(content).strip()
        
        if file_extension == '.pdf':
            return DocumentParser._extract_from_pdf_fallback(file)
        
        if file_extension in ['.doc', '.docx']:
            if not DOCX_AVAILABLE:
                raise ValueError("Word files not supported. Install: pip install python-docx")
            return DocumentParser._extract_from_docx(file)
        
        if file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            if not OCR_AVAILABLE:
                raise ValueError("Images not supported. Install: pip install Pillow pytesseract")
            return DocumentParser._extract_from_image(file)
        
        raise ValueError(f"Unsupported file type: {file_extension}")
    
    @staticmethod
    def _extract_from_pdf_fallback(file):
        if PDF_AVAILABLE:
            return DocumentParser._extract_from_pdf(file)
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                tmp.write(file.read())
                tmp_path = tmp.name
            
            try:
                result = subprocess.run(['pdftotext', tmp_path, '-'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except:
                pass
            
            raise ValueError("PDF extraction failed. Install: pip install PyPDF2")
        finally:
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    @staticmethod
    def _extract_from_pdf(file):
        text = ""
        try:
            file.seek(0)
            pdf_reader = PyPDF2.PdfReader(file)
            
            if len(pdf_reader.pages) == 0:
                raise ValueError("PDF has no pages")
            
            for page in pdf_reader.pages:
                try:
                    extracted = page.extract_text()
                    if extracted and extracted.strip():
                        text += extracted + "\n"
                except:
                    continue
        except Exception as e:
            raise ValueError(f"PDF extraction failed: {str(e)}")
        
        if not text.strip():
            raise ValueError("No readable text found in PDF")
        
        return text.strip()
    
    @staticmethod
    def _extract_from_docx(file):
        try:
            file.seek(0)
            doc = docx.Document(file)
            text = ""
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text += paragraph.text + "\n"
            
            if not text.strip():
                raise ValueError("No text found in document")
            
            return text.strip()
        except Exception as e:
            raise ValueError(f"DOCX extraction failed: {str(e)}")
    
    @staticmethod
    def _extract_from_image(file):
        try:
            file.seek(0)
            image = Image.open(file)
            text = pytesseract.image_to_string(image)
        except Exception as e:
            raise ValueError(f"Image extraction failed: {str(e)}")
        
        if not text.strip():
            raise ValueError("No text found in image")
        
        return text.strip()
