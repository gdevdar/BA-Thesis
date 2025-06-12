from scraper_2.scraper_2 import scraper_2
from data_cleaning_engineering.procedure import procedure
from datetime import date

def answer_collector():
    while True:
        Q1 = input("Do you want to Scrape myhome.ge? \n(Y/N):")
        if Q1.upper() in ["Y","YES"]:
            while True:
                Q2 = input("Do you also want to apply cleaning and engineering to the scraped data?\n(Y/N):")
                if Q2.upper() in ["Y","YES"]:
                    print("Will start to scrape, then clean and engineer the data! after you input the parameters:")
                    return 1
                elif Q2.upper() in ["N","NO"]:
                    print("Will start to scrape, without cleaning nor engineering! after you input the parameters:")
                    return 2
                else:
                    print("invalid input try again!\n")
        elif Q1.upper() in ["N","NO"]:
            while True:
                Q3 = input("Do you want to engineer or clean previously scraped data?\n(Y/N):")
                if Q3.upper() in ["Y","YES"]:
                    return 3
                elif Q3.upper() in ["N","NO"]:
                    print("There are no functionalities other than scraping, cleaning and engineering, so this is the end")
                    return 0
                else:
                    print("Invalid input try again\n")
        else:
            print("invalid input try again!\n")
def main():
    answer = answer_collector()
    date_today = date.today()
    if answer == 1:
        scraper_2(date_today)
        df = procedure(f"scrape_files/{date_today}.json",date_today)
        df.to_json(f"ce_{date_today}.json")
    elif answer == 2:
        scraper_2(date_today)
    elif answer == 3:
        name = input("What's the name of your file (including .json, e.g. 2025-05-02.json)? (Make sure to put it in scrape_files)\n")
        scrape_date = input("When was this data collected (Format: YYYY-MM-DD, e.g. 2025-05-21)\n")
        print("Cleaning and Engineering your existing data!")
        df = procedure(f"scrape_files/{name}",scrape_date)
        df.to_json(f"ce_{date_today}.json")
    else:
        pass
    #scraper_2()
    # Let's give them three options.
    # Only the scraping
    # Use it on already scraped data
    # Scraping + data cleaning & engineering
    ## if data cleaning & engineering
    #df = procedure('scrape_files/base_data_2025-05-02.json','2025-05-02')
    #df.to_json('2025-05-02.json')

if __name__ == "__main__":
    main()

# Plan is simple
# Take the dataset that I was sharing
# Take the raw dataset
# Take the inner join of the two and keep the rows of the raw dataset
