# pandas
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

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

def save_to_dataframe(produto_info, df):
    new_row = pd.DataFrame([produto_info])
    df = pd.concat([df, new_row], ignore_index=True)
    return df

if __name__ == "__main__":
    
    df = pd.DataFrame()

    while True:
        page_content = fetch_page()
        produto_info = parse_page(page_content)
        df = save_to_dataframe(produto_info, df)
        print(df)
        time.sleep(10)