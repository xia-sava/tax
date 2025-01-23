import csv
import re
from pathlib import Path

import pdfplumber

# language=markdown
"""
1. アマゾン注文適格請求書＆領収書一括取得で請求書 pdf を出力して c:/tmp/A に展開
2. 同範囲の CSV を出力して c:/tmp/A に展開
3. このスクリプトを実行して extracted_all.csv を出力
4. extracted_all.csv を見て先頭カラムに，消耗品費に 1 を，非対象に 0 を入れる
5. 再度このスクリプトを実行して extracted_all.csv を読み込んで分類していく


"""


DATA_DIR = Path("c:/tmp/A")
EXTRACT_CSV = DATA_DIR / "extracted_all.csv"
CREDIT_CARD_LAST4 = "2600"


def main():
    if not EXTRACT_CSV.exists():
        extract_pdf()
    else:
        distribute_files()


def extract_pdf():
    exclude_orders = []
    for csv_file in DATA_DIR.iterdir():
        if re.match(r"order.*.csv", csv_file.name):
            with csv_file.open() as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    if CREDIT_CARD_LAST4 not in row[5]:
                        exclude_orders.append(row[0])
    results = []
    for pdf_file in DATA_DIR.iterdir():
        if pdf_file.suffix == ".pdf":
            print(f"Extracting data from {pdf_file}")
            ret = parse_invoice_data(pdf_file)
            if ret is None:
                continue
            if ret[3] in exclude_orders:
                continue
            results.append(["", *ret, pdf_file.name])
    with EXTRACT_CSV.open("w", newline="\n") as output:
        writer = csv.writer(output)
        writer.writerow(["分類", "請求書発行日", "合計金額", "購入内容", "注文番号", "ファイル名"])
        writer.writerows(sorted(results, key=lambda x: x[1]))


def distribute_files():
    with EXTRACT_CSV.open() as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            month = row[1][:7]
            match row[0]:
                case "1":
                    dest_dir = mkdir(month, "消耗品費")
                case "":
                    dest_dir = mkdir(month, "書籍")
                case _:
                    continue
            pdf = DATA_DIR / row[5]
            pdf.rename(dest_dir / pdf.name)
            print(f"Moved {pdf} to {dest_dir}/{pdf.name}")


def mkdir(month, category):
    month_dir = DATA_DIR / month
    if not month_dir.exists():
        month_dir.mkdir()
    category_dir = month_dir / category
    if not category_dir.exists():
        category_dir.mkdir()
    return category_dir


def parse_invoice_data(pdf_path):
    invoice_date = None
    total_amount = None
    purchase_content = None
    order_number = None

    with pdfplumber.open(pdf_path) as pdf:
        all_text = []
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                all_text.append(extracted)
        text = "\n".join(all_text)

    if re.search(r"合計 -￥", text):
        return None

    if m := re.search(r"請求(?:書発行)?日 ([-0-9]+)", text):
        invoice_date = m.group(1)

    if m := re.search(r"合計 ￥([\d,]+)", text):
        total_amount = m.group(1).replace(",", "")

    if m := re.search(r"税抜 税込 税込\n(.+) [\d,]+ ￥[\d,]+ [\d,]+% ￥[\d,]+ ￥[\d,]+", text):
        purchase_content = m.group(1)

    if m := re.search(r"注文番号\s*([-0-9]+)", text):
        order_number = m.group(1)

    if not all([invoice_date, total_amount, purchase_content, order_number]):
        raise ValueError(f"Failed to extract all necessary data from {pdf_path}")

    return invoice_date, total_amount, purchase_content, order_number

if __name__ == '__main__':
    main()
