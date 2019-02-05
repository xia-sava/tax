import csv
from datetime import datetime
from pathlib import Path

"""
"""


def main():
    credit_card_last4 = '5189'
    m_range = [
        datetime(2016, 11, 7),  # 1月
        datetime(2016, 12, 8),  # 2月
        datetime(2017, 1, 6),  # 3月
        datetime(2017, 2, 7),  # 4月
        datetime(2017, 3, 7),  # 5月
        datetime(2017, 4, 11),  # 6月
        datetime(2017, 5, 6),  # 7月
        datetime(2017, 6, 6),  # 8月
        datetime(2017, 7, 13),  # 9月
        datetime(2017, 8, 8),  # 10月
        datetime(2017, 9, 6),  # 11月
        datetime(2017, 10, 12),  # 12月
        datetime(2017, 11, 2),  # 最後尾の次の日
    ]
    excluded_order = [
        '250-4891768-6491822',
    ]

    data = [[] for i in range(12)]
    for csvfile in sorted(Path('.').glob('amazon-order_*.csv')):
        with open(csvfile, 'r', encoding='utf-8') as w_month:
            reader = csv.reader(w_month)
            header = next(reader)
            for row in reader:
                order_no = row[1]
                name = row[2]
                author = row[3]
                price = int(row[4])
                charge_date_str = row[12]
                credit_card = row[14]
                if order_no in excluded_order:
                    continue
                if f'下4けたが{credit_card_last4}' not in credit_card:
                    continue
                if not charge_date_str:
                    continue
                charge_date = datetime.strptime(charge_date_str, '%Y/%m/%d')
                month = [i for i in range(12) if m_range[i] <= charge_date < m_range[i + 1]]
                if not month:
                    continue
                data[month[0]].append([charge_date, order_no, price, name, author])

    with open('extracted_all.csv', 'w', newline='', encoding='utf_8_sig') as w_all:
        with open('criteria.txt', 'w') as w_cri:
            for m, month_data in enumerate(data):
                month_data.sort(key=lambda r: r[0])
                csv.writer(w_all).writerows(month_data)
                print(' OR '.join([r[1] for r in month_data]), file=w_cri)


if __name__ == '__main__':
    main()
