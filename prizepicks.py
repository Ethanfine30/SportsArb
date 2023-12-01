import requests
import cloudscraper
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
url = 'https://api.prizepicks.com/projections'
scraper = cloudscraper.create_scraper()
res = scraper.get(url)
print(res.status_code)