# telegram and postgres
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import sqlite3
import asyncio
from telegram import Bot
import os
from dotenv import load_dotenv

load_dotenv()

# Configuracao do bot Telegram
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
bot = Bot(token=TOKEN)

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
    """Cria uma conexão com o banco de dados SQLite."""
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
    """Salva uma linha de dados no banco de dados SQLite usando pandas."""
    new_row = pd.DataFrame([product_info]) # Converte o dicionário em um DataFrame de uma linha
    new_row.to_sql('prices', conn, if_exists='append', index=False) # Salva o DataFrame no banco de dados
    
def get_max_price(conn):
    """Consulta o maior preco registrado no banco de dados."""
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(new_price), timestamp FROM prices")
    result = cursor.fetchone()
    if result and result[0] is not None:
        return result[0], result[1]
    else:
        return None, None

async def send_telegram_message(text):
    """Envia uma mensagem para o Telegram."""
    await bot.send_message(chat_id=CHAT_ID, text=text)

async def main():
    conn = create_connection()
    setup_database(conn)

    try:
        while True:
            # Faz a requisição e parseia a página
            page_content = fetch_page()
            product_info = parse_page(page_content)
            current_price = product_info['new_price']
            
            # Obtém o maior preço já salvo
            max_price, max_price_timestamp = get_max_price(conn)
            
            # Comparação de preços
            if max_price is None or current_price > max_price:
                message = f"Novo preço maior detectado: {current_price}"
                print(message)
                await send_telegram_message(message)
                max_price = current_price
                max_price_timestamp = product_info['timestamp']
            else:
                message = f"O maior preço registrado é {max_price} em {max_price_timestamp}"
                print(message)
                await send_telegram_message(message)

            # Salva os dados no banco de dados SQLite
            save_to_database(conn, product_info)
            print("Dados salvos no banco:", product_info)
            
            # Aguarda 10 segundos antes da próxima execução
            await asyncio.sleep(10)

    except KeyboardInterrupt:
        print("Parando a execução...")
    finally:
        conn.close()

# Executa o loop assíncrono
asyncio.run(main())