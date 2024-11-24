# sqlite3
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import sqlite3

def fetch_page():
    url = "https://www.mercadolivre.com.br/apple-iphone-16-pro-titnio-preto-128-gb-8-gb/p/MLB1040287850?product_trigger_id=MLB1040287849&pdp_filters=item_id%3AMLB3846002353&applied_product_filters=MLB1040287849&quantity=1"
    response = requests.get(url)
    return response.text

def parse_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    product_name = soup.find('h1', class_ = 'ui-pdp-title').get_text()
    prices: list= soup.find_all('span', class_ = 'andes-money-amount__fraction')
    old_price: int = int(prices[0].get_text().replace('.', ''))  
    new_price: int = int(prices[1].get_text().replace('.', ''))  
    installment_price: int = int(prices[2].get_text().replace('.', ''))

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    return {
        'product_name': product_name,
        'old_price': old_price,
        'new_price': new_price,
        'installment_price': installment_price,
        'timestamp': timestamp
    }

def create_connection(db_name='prices.db'):
    """Cria uma conexão com o banco de dados."""
    conn = sqlite3.connect(db_name)
    return conn

def setup_database(conn):
    """Cria uma tabela de preços no banco de dados se não existir."""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            old_price INTEGER,
            new_price INTEGER,
            installment_price INTEGER,
            timestamp TEXT
        )
    ''')
    conn.commit()


def save_to_database(conn, product_info):
    new_row = pd.DataFrame([product_info])
    new_row.to_sql('prices', conn, if_exists='append', index=False)
    

if __name__ == "__main__":
    
    conn = create_connection()
    setup_database(conn)

    while True:
        page_content = fetch_page()
        produto_info = parse_page(page_content)
        save_to_database(conn, produto_info)
        print("Dados salvos no banco de dados: ", produto_info)
        time.sleep(10)