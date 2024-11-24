# requests
import requests

def fetch_page(url):
    response = requests.get(url)
    return response.text

if __name__ == "__main__":
    url = "https://www.mercadolivre.com.br/apple-iphone-16-pro-titnio-preto-128-gb-8-gb/p/MLB1040287850?product_trigger_id=MLB1040287849&pdp_filters=item_id%3AMLB3846002353&applied_product_filters=MLB1040287849&quantity=1"
    page_content = fetch_page(url)
    print(page_content)