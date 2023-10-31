import requests
import pandas as pd
import re

# Testing Beats functions

class Beats:

    def __init__(self, date=''):
        ready_date = self.check_date(date)
        url_start = 'https://api.beatsaver.com/maps/latest?' 
        url_end = '&pageSize=50'
        self.full_url = f'{url_start}{ready_date}{url_end}'


    def check_date(self, date):
        try:
            date_pattern = r'\d{4}-\d{2}-\d{2}'
            if re.match(date_pattern, date):
                if int(date[:4]) < 2019:
                    return f'after={date}T12%3A02%3A36.874Z'
                else:
                    return f'before={date}T12%3A02%3A36.874Z'
        except:
            return ''

if __name__ == '__main__':
    query_date = input('enter YYYY-MM-DD for a specific date. improper date formats will show most recent songs') ## This will turn into a button on streamlit
    b = Beats(query_date)
    print(b.full_url)