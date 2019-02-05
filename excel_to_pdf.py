from pathlib import Path
import sys

import win32com.client


def main():
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = False

    try:
        for wb_name in sys.argv[1:]:  # type: str
            print(f'Processing: {wb_name}')
            wb_name = wb_name.replace('\\\\', '\\').replace('/', '\\')
            wb_path = Path(wb_name).absolute()
            pdf_path = Path(wb_name.replace('xlsx', 'pdf')).absolute()
            if pdf_path.exists():
                pdf_path.unlink()

            wb = excel.Workbooks.Open(str(wb_path))
            try:
                wb.WorkSheets(1).Select()
                wb.ActiveSheet.ExportAsFixedFormat(0, str(pdf_path))
            finally:
                wb.Close(True)
                wb = None
    finally:
        excel.Quit()
        excel = None


if __name__ == '__main__':
    main()
