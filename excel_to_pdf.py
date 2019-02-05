from pathlib import Path
import sys

import win32com.client


def main():
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = False

    for wb_name in sys.argv[1:]:  # type: str
        wb_path = Path(wb_name)
        pdf_path = Path(wb_name.replace('xlsx', 'pdf'))

        wb = excel.Workbooks.Open(wb_path)
        wb.WorkSheets(1).Select()
        wb.ActiveSheet.ExportAsFixedFormat(0, pdf_path)


if __name__ == '__main__':
    main()
