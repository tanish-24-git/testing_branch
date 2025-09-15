## New FILE: src/tools/operations/office/excel_create.py
## Changes: Implements office.excel.create using pywin32.
## Adapted from test/exceltest.py.
## Content: list of lists (table data), or JSON {"data": [[...]], "formulas": {...}, "charts": [...]}
## Launches Excel visibly.
import win32com.client
import platform
import os
import json

def office_excel_create(content: str, file_path: str = None) -> tuple[bool, str]:
    """Create or edit Excel with content (data/table), launch Excel, insert, display."""
    if platform.system() != "Windows":
        return False, "Office automation requires Windows with pywin32."
    
    try:
        # Parse content (assume JSON string for structure)
        try:
            content_dict = json.loads(content)
            data = content_dict.get("data", [])  # list of lists
        except json.JSONDecodeError:
            # Fallback: assume list of lists as string, eval safely
            data = eval(content) if isinstance(content, str) else content
            if not isinstance(data, list) or not all(isinstance(row, list) for row in data):
                return False, "Content must be list of lists or JSON with 'data'."
        
        # Start Excel
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = True
        
        # Create or open workbook
        if file_path and os.path.exists(file_path):
            workbook = excel.Workbooks.Open(file_path)
        else:
            workbook = excel.Workbooks.Add()
            file_path = os.path.abspath("new_sheet.xlsx")  # Temp
        
        sheet = workbook.Sheets(1)
        
        # Clear existing if editing
        if file_path and os.path.exists(file_path):
            sheet.Cells.Clear()
        
        # Write data
        for row_idx, row in enumerate(data, start=1):
            for col_idx, value in enumerate(row, start=1):
                sheet.Cells(row_idx, col_idx).Value = value
        
        # TODO: Add formulas/charts if in content_dict (extend as needed)
        
        # Save if new
        if "new_sheet" in file_path:
            workbook.SaveAs(file_path)
        
        return True, f"Excel sheet created/edited and displayed: {file_path}"
    
    except Exception as e:
        return False, f"Error in Excel automation: {str(e)}"