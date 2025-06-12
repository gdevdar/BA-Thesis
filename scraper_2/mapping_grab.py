import cloudscraper
from bs4 import BeautifulSoup
import json
def map_grab():
    url = "https://www.myhome.ge/"

    scraper = cloudscraper.create_scraper()
    page = scraper.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    script_tag = soup.find('script', type='application/json')
    string = script_tag.string
    json_data = json.loads(string)


    filter_parameters = json_data["props"]['pageProps']['_nextI18Next']['initialI18nStore']['ka']['filter-parameters']
    dumps = json.dumps(filter_parameters, indent=4)

    with open('scrape_files/mapping.json', 'w') as f:
        f.write(dumps)