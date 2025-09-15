## New FILE: src/tools/operations/office/word_create.py
## Changes: Implements office.word.create using pywin32.
## Adapted from test/wordtest.py.
## Content: string or list of paragraphs.
## If file_path provided, edits existing; else creates new.
## Launches Word visibly.
import win32com.client
import platform
import os

def office_word_create(content: str, file_path: str = None) -> tuple[bool, str]:
    """Create or edit Word doc with content, launch Word, insert, display."""
    if platform.system() != "Windows":
        return False, "Office automation requires Windows with pywin32."
    
    try:
        # Parse content (string or list)
        if isinstance(content, str):
            paragraphs = content.split("\n\n")  # Simple split
        elif isinstance(content, list):
            paragraphs = content
        else:
            return False, "Content must be string or list of paragraphs."
        
        # Start Word
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = True
        
        # Create or open doc
        if file_path and os.path.exists(file_path):
            doc = word.Documents.Open(file_path)
        else:
            doc = word.Documents.Add()
            file_path = os.path.abspath("new_doc.docx")  # Temp if no path
        
        # Clear existing if editing
        if file_path and os.path.exists(file_path):
            doc.Content.Delete()
        
        # Add paragraphs
        for text in paragraphs:
            para = doc.Paragraphs.Add()
            para.Range.Text = text
            para.Range.InsertParagraphAfter()
        
        # Save if new
        if "new_doc" in file_path:
            doc.SaveAs(file_path)
        
        return True, f"Word document created/edited and displayed: {file_path}"
    
    except Exception as e:
        return False, f"Error in Word automation: {str(e)}"