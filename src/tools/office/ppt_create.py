## New FILE: src/tools/operations/office/ppt_create.py
## Changes: Implements office.ppt.create using pywin32.
## Adapted from test/ppttest.py.
## Content: list of dicts {title: str, content: str, notes: str (optional)}
## Launches PowerPoint visibly.
import win32com.client
import platform
import os
import json

def office_ppt_create(content: str, file_path: str = None) -> tuple[bool, str]:
    """Create or edit PPT with slides content, launch PowerPoint, insert, display."""
    if platform.system() != "Windows":
        return False, "Office automation requires Windows with pywin32."
    
    try:
        # Parse content (assume JSON string: list of dicts)
        try:
            slides = json.loads(content)
            if not isinstance(slides, list) or not all(isinstance(s, dict) for s in slides):
                return False, "Content must be list of dicts {title, content, notes?}."
        except json.JSONDecodeError:
            return False, "Invalid content format; must be JSON list of slides."
        
        # Start PowerPoint
        ppt = win32com.client.Dispatch("PowerPoint.Application")
        ppt.Visible = True
        
        # Create or open presentation
        if file_path and os.path.exists(file_path):
            presentation = ppt.Presentations.Open(file_path)
            # Clear existing slides if editing
            while presentation.Slides.Count > 0:
                presentation.Slides(1).Delete()
        else:
            presentation = ppt.Presentations.Add()
            file_path = os.path.abspath("new_ppt.pptx")  # Temp
        
        # Add slides
        for slide_data in slides:
            slide = presentation.Slides.Add(presentation.Slides.Count + 1, 1)  # ppLayoutText
            slide.Shapes[0].TextFrame.TextRange.Text = slide_data.get("title", "Title")  # Title
            slide.Shapes[1].TextFrame.TextRange.Text = slide_data.get("content", "")  # Content
            if "notes" in slide_data:
                slide.NotesPage.Shapes[1].TextFrame.TextRange.Text = slide_data["notes"]
        
        # Save if new
        if "new_ppt" in file_path:
            presentation.SaveAs(file_path)
        
        return True, f"PowerPoint created/edited and displayed: {file_path}"
    
    except Exception as e:
        return False, f"Error in PPT automation: {str(e)}"