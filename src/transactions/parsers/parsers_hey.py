import re
import pdfplumber
import pandas as pd

from typing import List


def is_transaction(line: str) -> bool:

    pattern = r'\d{2}\/\w{3}\s\d{2}/\w{3}\s'
    match = re.match(pattern, line)

    return match is not None

def parse_transaction(line: str) -> dict:

    # parse date
    months_map = {
        'Ene': 1,
        'Feb': 2,
        'Mar': 3,
        'Abr': 4,
        'May': 5,
        'Jun': 6,
        'Jul': 7,
        'Ago': 8,
        'Sep': 9,
        'Oct': 10,
        'Nov': 11,
        'Dic': 12
    }
    date_text = re.match(r'\d{2}\/\w{3}', line).group()
    day, month = date_text.strip().split('/')
    day = int(day)
    month = int(months_map[month])

    # parse amount
    amount_pattern = r'(\(-\)|)\s(\d{1,3},|)\d{1,3}\.\d{2}$'
    amount = re.search(amount_pattern, line).group()
    amount = float(amount.replace('(-) ', '-').replace(',', ''))

    # parse concept
    date_pattern = r'\d{2}\/\w{3}\s\d{2}/\w{3}\s'
    begin_idx = re.match(date_pattern, line).span()[1]
    end_idx = re.search(amount_pattern, line).span()[0]
    concept = line[begin_idx:end_idx]

    transaction = {
        'month': month,
        'day': day,
        'amount': amount,
        'concept': concept
    }

    return transaction


def process_transactions(lines: List[str]) -> List[dict]:

    transactions = []
    for line in lines:

        if is_transaction(line):
            transactions.append(parse_transaction(line))
        elif line.startswith('CR'):
            transactions[-1]['amount'] *= -1

    return transactions


def get_transactions(pages) -> List[dict]:

    transactions = []
    transaction_break_string = 'Resumen de Movimientos'

    for page in pages:
        page_text = page.extract_text()

        if transaction_break_string in page_text:
            break

        lines = page_text.split('\n')
        page_transactions = process_transactions(lines)
        transactions += page_transactions

    return transactions


def parse_file(file_path: str) -> pd.DataFrame:

    def make_date(row: pd.DataFrame) -> str:
        return f'{row.year}-{row.month:0>2d}-{row.day:0>2d}'

    file_name = file_path.split('/')[-1].strip('.pdf')
    account, year, month = file_name.split('_')

    pdf = pdfplumber.open(file_path)
    pages = pdf.pages

    period_pattern = r'Periodo del \d{2}/\w{3}/\d{4}al \d{2}/\w{3}/\d{4}'
    period = re.search(period_pattern, pages[0].extract_text()).group()
    period = period.replace('Periodo del ', '').replace('al ', '-')
    transactions = get_transactions(pages)

    df = pd.DataFrame(transactions)
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
