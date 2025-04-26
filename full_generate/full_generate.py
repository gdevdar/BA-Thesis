def main():
    start_date =date.today()
    scraper_2(start_date)
    df = procedure(f"{start_date}.json",start_date)
    df.to_json('engineered.json',orient='records')

from scraper_2 import scraper_2
from datetime import date
from procedure import procedure

if __name__ == "__main__":
    main()