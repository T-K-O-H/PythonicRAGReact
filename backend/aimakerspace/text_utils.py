import os
from typing import List
import PyPDF2


class TextFileLoader:
    def __init__(self, path: str, encoding: str = "utf-8"):
        self.documents = []
        self.path = path
        self.encoding = encoding

    def load(self):
        if os.path.isdir(self.path):
            self.load_directory()
        elif os.path.isfile(self.path) and self.path.endswith(".txt"):
            self.load_file()
        else:
            raise ValueError(
                "Provided path is neither a valid directory nor a .txt file."
            )

    def load_file(self):
        with open(self.path, "r", encoding=self.encoding) as f:
            self.documents.append(f.read())

    def load_directory(self):
        for root, _, files in os.walk(self.path):
            for file in files:
                if file.endswith(".txt"):
                    with open(
                        os.path.join(root, file), "r", encoding=self.encoding
                    ) as f:
                        self.documents.append(f.read())

    def load_documents(self):
        self.load()
        return self.documents


class CharacterTextSplitter:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        assert (
            chunk_size > chunk_overlap
        ), "Chunk size must be greater than chunk overlap"

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str) -> List[str]:
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunks.append(text[i : i + self.chunk_size])
        return chunks

    def split_texts(self, texts: List[str]) -> List[str]:
        chunks = []
        for text in texts:
            chunks.extend(self.split(text))
        return chunks


class PDFLoader:
    def __init__(self, path: str):
        self.documents = []
        self.path = path
        print(f"PDFLoader initialized with path: {self.path}")

    def load(self):
        print(f"Loading PDF from path: {self.path}")
        print(f"Path exists: {os.path.exists(self.path)}")
        print(f"Is file: {os.path.isfile(self.path)}")
        print(f"Is directory: {os.path.isdir(self.path)}")
        print(f"File permissions: {oct(os.stat(self.path).st_mode)[-3:]}")
        
        try:
            # Try to open the file first to verify access
            with open(self.path, 'rb') as test_file:
                pass
            
            # If we can open it, proceed with loading
            self.load_file()
            
        except IOError as e:
            print(f"IOError accessing file at '{self.path}': {str(e)}")
            raise ValueError(f"Cannot access file at '{self.path}': {str(e)}")
        except Exception as e:
            print(f"Error processing file at '{self.path}': {str(e)}")
            raise ValueError(f"Error processing file at '{self.path}': {str(e)}")

    def load_file(self):
        try:
            with open(self.path, 'rb') as file:
                # Create PDF reader object
                pdf_reader = PyPDF2.PdfReader(file)
                
                if len(pdf_reader.pages) == 0:
                    raise ValueError("PDF file is empty")
                
                # Extract text from each page
                text = ""
                for page in pdf_reader.pages:
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    except Exception as e:
                        print(f"Error extracting text from page: {str(e)}")
                
                if not text.strip():
                    raise ValueError("No text could be extracted from the PDF")
                
                self.documents.append(text)
                print(f"Successfully extracted {len(text)} characters from PDF")
                
        except PyPDF2.PdfReadError as e:
            print(f"PDF read error: {str(e)}")
            raise ValueError(f"Error reading PDF file: {str(e)}")
        except Exception as e:
            print(f"Error in load_file: {str(e)}")
            raise ValueError(f"Error processing PDF file: {str(e)}")

    def load_directory(self):
        for root, _, files in os.walk(self.path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'rb') as f:
                            pdf_reader = PyPDF2.PdfReader(f)
                            
                            # Extract text from each page
                            text = ""
                            for page in pdf_reader.pages:
                                try:
                                    page_text = page.extract_text()
                                    if page_text:
                                        text += page_text + "\n"
                                except Exception as e:
                                    print(f"Error extracting text from page in {file}: {str(e)}")
                            
                            if text.strip():
                                self.documents.append(text)
                                print(f"Successfully extracted {len(text)} characters from {file}")
                            else:
                                print(f"No text could be extracted from {file}")
                                
                    except Exception as e:
                        print(f"Error processing {file}: {str(e)}")

    def load_documents(self):
        self.load()
        return self.documents 