import re

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
    amount = line.split()[-1]

    # parse concept
    concept = ' '.join(line.split()[2:-1])

    transaction = {
        'day': day,
        'month': month,
        'amount': amount,
        'concept': concept
    }

    return transaction


def parse_transaction(line: str)-> dict:

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
    amount = line.split()[-1]

    # parse concept
    concept = ' '.join(line.split()[2:-1])


    transaction = {
        'day': day,
        'month': month,
        'amount': amount,
        'concept': concept
    }

    return transaction


