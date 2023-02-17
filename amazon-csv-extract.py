import csv
import sys
from datetime import datetime
from pathlib import Path

# language=markdown
"""
1. Amazon履歴フィルタでクレカ請求に入ってきてそうな月の範囲を CSV 出力して c:/tmp/A に配置
2. 出力された extracted_all.csv を見てこれはちゃうやろってのを excluded_order に並べて繰り返す
3. 注文履歴フィルタを全月分にして criteria.txt の1行ずつで絞り込み，領収証を PDF 出力する
4. 年初の注文分は年を跨ぐので前年分も出すこと
"""


def main():
    credit_card_last4s = ['2600']
    year = datetime.now().year
    m_range = [datetime(year - 2, 12, 1)] + [datetime(year - 1, m, 1) for m in range(1, 13)]
    excluded_order = [
    ]

    data_dir = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
    data = [[] for _ in range(12)]
    for csvfile in sorted(data_dir.glob('amazon-order_*.csv')):
        with open(csvfile, 'r', encoding='utf-8') as w_month:
            reader = csv.reader(w_month)
            header = next(reader)
            incomp_data: list[list] = []
            for row in reader:
                order_no = row[1]
                name = row[2]
                if name == '（クレジットカードへの請求）':
                    charge_date_str = row[12]
                    charge_date = datetime.strptime(charge_date_str, '%Y/%m/%d')
                    month = [i for i in range(12) if m_range[i] <= charge_date < m_range[i + 1]]
                    if not month:
                        continue
                    for record in incomp_data:
                        data[month[0]].append([charge_date_str] + record)
                    incomp_data = []
                    continue
                author = row[3]
                if row[4] == '':
                    continue
                price = int(row[4])
                credit_card = row[14]
                if order_no in excluded_order:
                    continue
                if any(f'下4けたが{last4}' in credit_card for last4 in credit_card_last4s):
                    incomp_data.append([order_no, price, name, author])

    with open(data_dir / 'extracted_all.csv', 'w', newline='', encoding='utf_8_sig') as w_all:
        with open(data_dir / 'criteria.txt', 'w') as w_cri:
            for m, month_data in enumerate(data):
                month_data.sort(key=lambda r: r[0])
                csv.writer(w_all).writerows(month_data)
                print(' OR '.join([r[1] for r in month_data]), file=w_cri)


if __name__ == '__main__':
    main()
