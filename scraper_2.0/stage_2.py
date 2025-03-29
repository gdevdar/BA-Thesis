
def read_lines(file_path):
    """
    :param file_path: Reads a txt file
    :return: Returns a list of lines from the txt file
    """
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    lines = [line.strip() for line in lines]
    return lines

def scrape(link,scraper):
    """
    :param scraper: The scraper class
    :param link: Scrapes the inputted link
    :return: returns the contents of the link page
    """
    response = scraper.get(link)
    page = response.text
    del response
    return page

def extract_data(page):
    """
    :param page: parses the inputted page
    :return: grabs the json part of the page that matters to us
    """
    soup = BeautifulSoup(page, 'html.parser')
    script_tag = soup.find('script', type='application/json')
    string = script_tag.string
    json_data = json.loads(string)
    queries = json_data['props']['pageProps']['dehydratedState']['queries']
    return queries

def trim_data(data):
    """
    :param data: The data to be trimmed
    :return: Only return the useful data
    """
    main_data = data[0]['state']['data']['data']['statement']
    data_update_count = data[0]['state']['dataUpdateCount']
    full_data = {"main_data":main_data, "data_update_count":data_update_count}
    return full_data

def full_process(link,scraper):
    """
    Scrapes the page - tries to scrape multiple times if it doesn't scrape properly
    Grabs json portion from the page
    Then trims the data
    Also returns whether the scraping failed or not (usually means that the listing was removed)
    """
    try_count = 0
    full_data = {}
    failed = False
    except_count = 0
    while True:
        try:
            page = scrape(link,scraper)
            try_count += 1
            data = extract_data(page)
            is_empty = data == []
            if is_empty:
                if try_count > 10:
                    #print(f"Didn't have the needed data: {link}")
                    failed = True
                    break
                else:
                    #time.sleep(5)
                    continue
            else:
                full_data = trim_data(data)
                #if try_count > 1:
                    #print(f"success for {link}")
                break
        except Exception as e:
            print(f"An error occurred: {e}")
            except_count += 1
            if except_count > 10:
                failed = True
                print(f"Errored too many times: {link}")
                break
            #time.sleep(2)
    return full_data, failed

def data_collector(url_batch):
    """
    :param url_batch: A list of urls to scrape
    :return: A list of json_files from those urls
    """
    start_time = time.time()
    failed_links = []
    collected_data = []
    i = 0
    batch_identifier = url_batch[0][22:33]
    batch_size = len(url_batch)
    scraper = cloudscraper.create_scraper(delay=10, interpreter='nodejs')
    for url in url_batch:
        i+=1
        #print(f"processing {i}/{batch_size} of batch {batch_identifier} \n {url}")
        json_data, failed = full_process(url,scraper)
        if failed:
            failed_links.append(url)
        else:
            collected_data.append(json_data)
        if i % 300 == 0:
            print(f"Finished {i} out of {batch_size} for batch {batch_identifier}")
            execution_time = time.time() - start_time
            formatted_time = str(timedelta(seconds=execution_time))
            print(f"Execution time: {formatted_time}")
            time_per_link = execution_time/i
            remaining_links = batch_size - i
            remaining_time = remaining_links * time_per_link
            formatted_time = str(timedelta(seconds=remaining_time))
            print(f"Approximate completion in: {formatted_time}")

    # Saving the failed links
    failed_link_collector(batch_identifier, failed_links)
    print(f"Batch {batch_identifier} has completed")
    execution_time = time.time() - start_time
    formatted_time = str(timedelta(seconds=execution_time))
    print(f"Execution time: {formatted_time}")
    return collected_data

def failed_link_collector(batch_identifier, failed_links):
    """
    :param batch_identifier: Unique identifier of the batch
    :param failed_links: list of urls we failed to gain data from
    :return: Does not return anything. Instead, creates a txt document that stores those links
    """
    failed_file = open(f'./FailedLinks/failed_links_{batch_identifier.replace("/", "")}.txt', 'w')
    for link in failed_links:
        failed_file.write(link + "\n")
    failed_file.close()

def split(a, n):
    """
    :param a: List to split into smaller lists
    :param n: Number of parts to split the list
    :return: returns smaller lists of the original list
    """
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

def parallel_data_collector(all_urls, num_of_workers):
    """
    :param all_urls: The urls to scrape for our project
    :param num_of_workers: How many threads to use (or how many parallel processes to use)
    :return: returns a list containing json_files from executing the data collector.
    It should be a list of 3*num_of_workers lists. And those lists should contain json_files
    """
    batches = list(split(all_urls,num_of_workers*10))
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_of_workers) as executor:
        results = list(executor.map(data_collector, batches))
    return results

def main():
    start_time = time.time()
    urls = read_lines("itemsV2.txt")
    results = parallel_data_collector(urls, 6)
    combined_data = []

    for item in results:
        for elements in item:
            combined_data.append(elements)

    combined_json = json.dumps(combined_data, indent=4)

    with open('working_data.json', 'w') as f:
        f.write(combined_json)

    end_time = time.time()
    execution_time = end_time - start_time
    formatted_time = str(timedelta(seconds=execution_time))
    print(f"Execution Time: {formatted_time}")


from datetime import timedelta
import time
import cloudscraper
from bs4 import BeautifulSoup
import json
import requests
import concurrent.futures

if __name__ == '__main__':
    main()