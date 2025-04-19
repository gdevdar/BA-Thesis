from datetime import timedelta
import time
import cloudscraper
from bs4 import BeautifulSoup
import json
import concurrent.futures

def read_lines(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    lines = [line.strip() for line in lines]
    return lines

def scrape(link,scraper):
    response = scraper.get(link)
    page = response.text
    del response
    return page

def extract_data(page):
    soup = BeautifulSoup(page, 'html.parser')
    script_tag = soup.find('script', type='application/json')
    string = script_tag.string
    json_data = json.loads(string)
    queries = json_data['props']['pageProps']['dehydratedState']['queries']
    return queries

def trim_data(data):
    main_data = data[0]['state']['data']['data']['statement']
    data_update_count = data[0]['state']['dataUpdateCount']
    full_data = {"main_data":main_data, "data_update_count":data_update_count}
    return full_data

def full_process(link,scraper):
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

def data_collector(url_batch,batch_identifier):
    start_time = time.time()
    failed_links = []
    collected_data = []
    i = 0
    #batch_identifier = url_batch[0][22:33]
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
            execution_time = time.time() - start_time
            formatted_time = str(timedelta(seconds=execution_time))
            print(f"Finished {i} out of {batch_size} for batch {batch_identifier} in {formatted_time}")
            time_per_link = execution_time/i
            remaining_links = batch_size - i
            remaining_time = remaining_links * time_per_link
            formatted_time = str(timedelta(seconds=remaining_time))
            print(f"Approximate completion in: {formatted_time}")

    # Saving the failed links
    #failed_link_collector(batch_identifier, failed_links)

    execution_time = time.time() - start_time
    formatted_time = str(timedelta(seconds=execution_time))
    print(f"Batch {batch_identifier} has completed in {formatted_time}")
    return collected_data


def parallel_data_collector(batches, num_of_workers):
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_of_workers) as executor:
        results = list(executor.map(data_collector, batches,range(len(batches))))
    return results