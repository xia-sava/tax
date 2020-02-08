import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import List

"""
"""


def main():
    credit_card_last4s = ['5189', '2600']
    m_range = [
        datetime(2018, 11,  7),  # 1月
        datetime(2018, 12,  9),  # 2月
        datetime(2019,  1,  8),  # 3月
        datetime(2019,  2, 12),  # 4月
        datetime(2019,  3,  9),  # 5月
        datetime(2019,  4,  6),  # 6月
        datetime(2019,  5,  8),  # 7月
        datetime(2019,  6, 12),  # 8月
        datetime(2019,  8,  9),  # 9月
        datetime(2019,  9,  1),  # 10月
        datetime(2019, 10,  3),  # 11月
        datetime(2019, 11,  3),  # 12月
        datetime(2019, 11, 29),  # 最後尾の次の日
    ]
    excluded_order = [
    ]

    data_dir = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
    data = [[] for i in range(12)]
    for csvfile in sorted(data_dir.glob('amazon-order_*.csv')):
        with open(csvfile, 'r', encoding='utf-8') as w_month:
            reader = csv.reader(w_month)
            header = next(reader)
            incomp_data = []  # type: List[List]
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
