import re
import pdfplumber
import pandas as pd

from typing import List


def parse_transaction(record: list) -> dict:

    date, category, concept, amount = record

    # parse date
    months_map = {
        'ENE': 1,
        'FEB': 2,
        'MAR': 3,
        'ABR': 4,
        'MAY': 5,
        'JUN': 6,
        'JUL': 7,
        'AGO': 8,
        'SEP': 9,
        'OCT': 10,
        'NOV': 11,
        'DIC': 12
    }
    day, month = date.split()
    day = int(day)
    month = int(months_map[month])

    # parse amount
    amount = float(amount.replace('$', '').replace(',', '').replace(' ', ''))

    transaction = {
        'month': month,
        'day': day,
        'amount': amount,
        'concept': concept
    }

    return transaction


def get_transactions(pages) -> List[dict]:

    def is_transaction(x):
        return all(i is not None for i in x[1:3])

    all_transactions = []
    transaction_break_string = 'INFORMACIÓN DE COSTOS'

    for page in pages:
        page_text = page.extract_text()

        if transaction_break_string in page_text:
            break

        transactions = page.extract_table()
        transactions = filter(is_transaction, transactions)
        transactions = [
            [j for j in i if j not in ['', None]] for i in transactions
        ]

        transactions = [parse_transaction(i) for i in transactions]

        all_transactions += transactions

    return all_transactions


def parse_file(file_path: str) -> pd.DataFrame:

    def make_date(row: pd.DataFrame) -> str:
        # TO-DO: parse date column
        return f'{row.year}-{row.month:0>2d}-{row.day:0>2d}'

    file_name = file_path.split('/')[-1].strip('.pdf')
    account, year, month = file_name.split('_')

    pdf = pdfplumber.open(file_path)
    pages = pdf.pages

    period = pages[0].extract_text().split('\n')[3]
    period = re.search(r'\d{1,2}\s\w{3}\s-\s\d{1,2}\s\w{3}', period).group()

    transactions = get_transactions(pages[2:])

    columns = ['month', 'day', 'category', 'concept', 'amount']
    df = pd.DataFrame(transactions, columns=columns)
    df['account'] = account
    df['year'] = year
    df['date'] = df[['year', 'month', 'day']].apply(make_date, axis=1)
    df['period'] = period

    out_columns = [
        'account',
        'period',
        'date',
        'amount',
        'concept'
    ]

    return df[out_columns]
