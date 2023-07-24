import re
import pdfplumber
import pandas as pd

from typing import List


def is_transaction(line: str) -> bool:

    pattern = r'\d{1,2}\sde\w+\s'
    match = re.match(pattern, line)

    return match is not None


def parse_transaction(line: str) -> dict:

    # parse date
    months_map = {
        'Enero': 1,
        'Febrero': 2,
        'Marzo': 3,
        'Abril': 4,
        'Mayo': 5,
        'Junio': 6,
        'Julio': 7,
        'Agosto': 8,
        'Septiembre': 9,
        'Octubre': 10,
        'Noviembre': 11,
        'Diciembre': 12
    }
    date_text = re.match(r'\d{1,2}\sde\w+\s', line).group()
    day, month = date_text.strip().split(' de')
    day = int(day)
    month = int(months_map[month])

    # parse amount
    amount = float(line.split()[-1].replace(',', ''))

    # parse concept
    concept = ' '.join(line.split()[2:-1])

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
    transaction_break_string = 'Resumen de Plan AMEX de Pagos Diferidos con Intereses y Meses sin Intereses'

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

    period = '_'.join(pages[1].extract_text().split('\n')[3].split()[-2:])
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
