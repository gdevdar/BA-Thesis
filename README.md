# Project Overview


## Table of Contents
- [Requirements](#requirements)
- [Setting up](#setting-up)
    - [Scraper Specific](#scraper-specific)

# Requirements
- Java 11 or higher needs to be installed (I downloaded from this [link](https://www.oracle.com/java/technologies/downloads/#jdk24-windows), the x64 installer one)
- Google Chrome browser needs to be installed
- Install the Selenium Server jar file. (I have it uploaded on GitHub and as long as you clone it there shouldn't be a problem)
- You need [python](https://www.python.org/downloads/) installed. I use python 3.13.

# Setting up
- Clone the repository (Or download the folder)
- Open the folder within your IDE, or navigate to it with your terminal
- Create virtual Environment using (Optional):
    ```bash
    python -m venv .venv
    ```
- Activate the virtual environment using one of these three commands (Optional):  
    Git Bash
    ```bash
    source .venv/scripts/activate
    ```
    cmd
    ```cmd
    .venv\Scripts\activate
    ```
    PowerShell
    ```powershell
    .venv\Scripts\Activate.ps1
    ```
- Run the following in the terminal (This downloads the packages that you need to run, if you activated your virtual environment it will download packages there locally, but if you didn't do that it will install globally):
    ```bash
    pip install -r requirements.txt
    ```

## Scraper specific
- The scraper uses Selenium Grid, therefore, in a separate terminal, you need to run:
    ```bash
    java -jar selenium-server-4.30.0.jar standalone
    ```

# Running the script
I have created a file called generate.py that allows you to do three things.  
Run the following code in the terminal:
```python
py generate.py
```
It will prompt two yes/no questions sequentially. It allows you to do 3 different things (4th one as well which is to do nothing):
1. To scrape myhome.ge and then applying the cleaning and engineering proceudres
2. To solely scrape and not apply anything extra
3. To apply cleaning and engineering to the previously scraped data

### Scenario 1 & Scenario 2
- Will prompt you to answer five questions that will affect the scraping procedure.
    - How many pages do you want to scrape?
    - How many selenium sessions do you want to run?
    - How many batches do you want per selenium session?
    - How many workers do you want for the link scraping phase?
    - How many batches do you want per worker?
### Scenario 3
- Will ask you two questions:
    - The name of the file that you want to apply the cleaning and engineering procedure (e.g. 2025-05-02.json )
    - The date at which the scraping was done (e.g. 2025-05-02), Important to correctly engineer some features

# Scraping Documentation
## The Scraper
### Parameter Choosing Phase
#### Pages to Scrape
How many pages do you want to scrape?

Answering this prompt by some integer "x", 
will result in the scraping of pages 1 to "x" for the url: 
"https://www.myhome.ge/s/iyideba-bina-Tbilisshi/?deal_types=1&real_estate_types=1&cities=1&currency_id=1&CardView=1&page="
#### Selenium sessions
How many selenium sessions do you want to run?

Here you are choosing how many sessions to run in parallel. 
Inputting "x" would result in "x" Chrome browsers running at the same time, improving the speed of scraping.
- Limitations:
  - The number of parallel processes you can run depends on the number of logical processors your device has. (Number of logical processors = Number of cores * 2). And this number is the maximum amount of parallel processes you can run.
  - The performance of your device. If your device can't handle running many Chrome sessions at the same time, even though you have many logical processors, it would be better to run fewer parallel sessions. (In my case I didn't see a significant improvement beyond running 2 parallel sessions)
  - The speed of your network. The speed of phase one depends on how fast the urls are loading, and if your internet is slow opening many urls at the same time may slow down the process instead of improving it.
#### Batches for Selenium sessions
How many batches do you want per selenium session?

At first the idea behind batches was to simply divide the urls 
into as many batches as the number of parallel processes. 
And give each batch to each process. However, there were two problems
: 1. When a webdriver ran for too long it timed out 2. And 
sometimes one process was significantly faster than the other 
and at the end for a few hours only one worker was scraping. By 
increasing the number of batches the webdriver no longer times out. (4 batches per two of the sessions, so 8 batches 
in total was the successful amount, I haven't tried other combinations). And it also reduced the chance of one worker doing hours of work in the end.

Another approach would be to start a new session (create a new WebDriver) 
for each url, however in my mind I thought it would be inefficient and 
tried to use one webdriver for many urls. This is why I don't increase 
the number of batches too much, to minimize the number of times I create 
a new WebDriver. 
#### Workers for link scraping
How many workers do you want for the link scraping phase?

This parameter is relevant for phase two of the scraping process. 
In theory, it is exactly the same as choosing the number of selenium sessions to run in parallel.
However, in phase two we no longer use Selenium. Instead, we use Cloudscraper. By choosing "x" you will run "x" scraping sessions in parallel.
- Limitations:
  - Number of workers capped at the number of logical processors
  - Performance does matter, but to a lesser extent compared to running selenium sessions. Here I run 6 parallel sessions.
  - Network also should matter, however it hasn't been a big problem in phase two.
#### Batches per worker
How many batches do you want per worker?

I tend to like giving big batches to each worker. However, one worker may be left with a huge batch to deal with in the end while others have finished, which is inefficient. So I recommend having 3x number of batches per worker. For each batch a new Cloudscraper Scraper is created, I tried to minimize the number of times we create a new scraper by using the same scraper for many links (Although I haven't tested the effect on performance).
### Phase One
Phase one takes as inputs: 1. Number of pages to Scrape 2. Number of Selenium sessions to run in parallel and 3. And number of batches to create

In scraper_2.0.py this phase is captured in main() by this code:  
stage_1(num_pages,num_selenium,num_batches)

stage_1() creates urls to scrape using "num_pages" and the base url. 
Then it splits it up in batches based on "num_batches". 
Then it starts the parallel scraping based on "num_selenium", with the help of concurrent.futures library and the "scrape" function from "link_gather.py".
After scraping, it saves the links in a text file called "links.txt".

I made it so stage_1() returns the time it took to execute, which is printed at the end.
#### link_gather.py
Contains only one functions called "scrape". It creates a Chrome WebDriver, 
the added options (Like setting for the WebDriver) were generated by DeepSeek to be able to avoid the website's bot defence.

The function takes in a batch of urls. For each url, it first loads and waits for a certain element to appear (The one that contains the information we want). This way we avoid cases when the url doesn't load in time, and we can't take the required data, plus the speed of scraping now is linked to the speed of loading, which is quite efficient.

Next it gathers the urls for each apartment listing and stores them in a list. 
This is done for all urls and finally the function returns the list of urls gathered from this batch.
### Phase Two
Phase two takes as inputs: 1. Number of workers and 2. Batches per work. Additionally, it also requires "links.txt" to be present, from where it extracts the links.

In scraper_2.0.py this phase is captured in main() by this code:  
stage_2(num_workers,batch_per_worker)

In phase one we saved the links in "links.txt".
Now we read this file and put the links in a list. 
Then we split them up in batches based on "num_workers"*"batch_per_worker". Then utilizing "parallel_data_collector" function from "link_scrape.py" we collect the necessary data from the pages. Then we write all these data into a json file called "raw.json".

stage_2() similarly to stage_1() returns the time it took to execute. Which is also printed at the end.
#### link_scrape.py
This module contains multiple functions. The function we call for is "parallel_data_collector(batches, num_of_workers)", This function parallelizes the scraping process and in turn relies on the function "data_collector(url_batch,batch_identifier)".

"data_collector" first creates a scraper and then goes through the urls of the url_batch one by one. It relies on another function called "full_process(link,scraper)", in case the scraping was successful "data_collector" will store the gathered data from the url in a list. At the end it returns the list of data for all urls in the batch.

"full_process" is built to ensure the scraping process is successful. It checks whether the website was scraped successfully (i.e. contains the target data). If it was not successful, it reattempts. After 10 reattempts it gives up and moves on to the next url.  
"full_process" relies on three functions "scrape", "extract_data" and "trim_data".  
"scrape" simply attempts to get the page.  
"extract_data" uses BeautifulSoup to grab the portion of the page that stores data.  
"trim_data" takes the output of "extract_data" and reduces it even further to only include the relevant information. This way we save RAM and Disk Space.

### Phase Three
Phase three does not take any inputs. However, it does rely on "raw.json" to generate its output.

This part of the code should only take minutes to run.

First we load the scraped data, by reading "raw.json". Additionally, we need data that interestingly is present in every myhome.ge page.
And this file contains mappings between IDs and what they stand for. (For example heating type id and then what this id means). 
We can grab this file that I call "mapping.json" using the 
"map_grab()" function from "mapping_grab.py".

When we read "raw.json" it creates a list that has one entry per page that we scraped.  
We go through each entry, and use them, along with data from mapping.json, as inputs to the "row_creator()" function imported from "data_extract.py".  
This creates a dictionary, that will be one row in the dataframe that we will be using later in the project.  
The created dictionaries are then stored in a list. Which is then written as a json file, that takes its name based on the current date (f"{date.today()}.json").

This concludes the Scraping Procedure.
#### mapping_grab.py
Contains one function called "map_grab()". It uses Cloudscraper to scrape myhome.ge. Then beautiful soup to extract the portion of the page that contains json data.
Then it finds the portion of the json data, that contains mappings. And then it creates the "mapping.json" file.
#### data_extract.py
"raw.json" can't directly be used as a row for a dataframe due to its structure.
It sometimes has dictionaries or lists nested inside of dictionaries. This code transforms the dictionaries inside "raw.json" to have a more usable structure.
## The Resulting Dataset
### Useless Variables
I don't know what some of these variables are supposed to be. However, it doesn't matter either way.

All the variables starting with "has_" was generated by me.
These variables take value "True" when a corresponding value or parameter is present
in the website's listing data. Otherwise, it takes value False. 
When such a variable only takes 1 value (False), it usually means that this parameter is not present in any of the apartments.

"data_update_count": Only takes 1 value  
"city_id" and "city_name": Only takes 1 value (Because we are scraping only Tbilisi)  
"published": Only takes 1 value  
"area_type_id": Only takes 1 value  
"is_owner": Only takes 1 value  
"is_active": Only takes 1 value  
"price_type_id": Only takes 1 value  
"has_asphalt_road": Only takes 1 value  
"can_be_divided_28": Only takes 1 value  
"with_building": Only takes 1 value  
"with_approved_project_30": Only takes 1 value  
"has_waiting_space": Only takes 1 value  
"has_cellar": Only takes 1 value  
"is_fenced": Only takes 1 value (This was generated similarly to "has_" variables)  
"has_gate": Only takes 1 value  
"has_fruit_trees": Only takes 1 value  
"has_yard_lighting": Only takes 1 value  
"has_yard": Only takes 1 value  
"for_party": only takes 1 value (This was generated similarly to "has_" variables)  
"allows_pets": only takes 1 value (This was generated similarly to "has_" variables)  
"with_approved_project_53": only takes 1 value (This was generated similarly to "has_" variables)  
"can_be_divided_54": only takes 1 value (This was generated similarly to "has_" variables)  
"owner_name": Personal information, not relevant for a price prediction model  
"user_phone_number": Personal information, not relevant for a price prediction model  
"rating": Always empty  
"gifts": Always empty  
"favorite": Always empty  
"price_negotiable": Always empty  
"price_from": Always empty  
"yard_area": Always empty (Because we are scraping only apartments)  
"lease_period": Always empty (Because we are scraping only sale deals)  
"lease_type_id": Always empty (Because we are scraping only sale deals)  
"lease_type": Always empty (Because we are scraping only sale deals)  
"lease_contract_type_id": Always empty (Because we are scraping only sale deals)  
"daily_rent_type_id": Always empty (Because we are scraping only sale deals)  
"daily_rent_type": Always empty (Because we are scraping only sale deals)  
"waiting_space_area": Always empty  
"grouped_street_id": Always empty  
"price_label": Always empty  
"dynamic_title": Generally includes number of rooms and district. We already have those variables.  
"dynamic_slug": Generally includes number of rooms and district. We already have those variables.  
"additional_information": Useless Variable
### Variables with Potential
Variables that start with "has_" or "is_", 
or any other True or False variable. 
They don't necessarily mean that an apartment has some 
attribute or not. It simply shows whether whoever posted the 
apartment for sale included that characteristic in parameters.

"id": Can be used to find the apartment statement. Every page of an apartment has such a structure "https://www.myhome.ge/pr/here_goes_your_id". Putting id after pr/ will lead you to the page of that specific apartment.  
"condition_id" - "condition": Condition of a building ("ახალი გარემონტებული": recently renovated, "შავი კარკასი":black frame etc.)  
"district_id" - "district_name": The district the apartment is in ("ვაკე-საბურთალო": Vake Saburtalo etc.)  
"urban_id" - "urban_name": Which Urban apartment is in ("ვაკე":Vake, "საბურთალო":Saburtalo etc.)  
"status_id" - "estate_status_types": Whether the building is old, new or being built("ძველი აშენებული": built long ago, "ახალი აშენებული": built recently etc.)  
"room_type_id": Number of rooms the apartment has (ID is a number)  
"bedroom_type_id": Number of bedrooms the apartment has (ID is a number)  
"bathroom_type_id" - "bathroom_type": Number of bathrooms the apartment has (ID is a type)  
"project_type_id" - "project_type": Shows the type of project, or the style of the apartment. ("იტალიური ეზო":Italian courtyard, "ქალაქური":Urban, "არასტანდარტული":Non-standard etc.)  
"hot_water_type_id" - "hot_water_type": How the water heating works in the apartment ("გაზის გამაცხელებელი": Gas heater, "ცენტრალური ცხელი წყალი":Central hot water etc.)  
"heating_type_id" - "heating_type": How the building is heated ("ცენტრალური გათბობა": Central heating etc.)  
"parking_type_id" - "parking_type": What type of parking is available ("ეზოს პარკინგი": Yard parking etc.)  
"height": Height of the ceiling  
"balconies": Number of balconies the apartment has  
"balcony_area": The total area of the balconies in square meters  
"last_updated": I think this shows when was the last time the page was modified  
"created_at": When the page was created  
"area": The area of the apartment in square meters  
"floor": On which floor the apartment is  
"total_floors": How many floors the building, in which the apartment is, has  
"views": How many times was the page viewed by people  
"is_old": I think this means whether the apartment or building is old  
"for_special_people": I think this means whether the apartment accommodates people with special needs  
"build_year": The period the building was built.  
"user_statements_count": How many statements has the user who is currently selling this house posted.  
"has_gas": Whether the apartment has gas or not  
"has_internet": Whether the apartment has internet or not  
"has_TV": Whether the apartment has TV or not  
"has_air_conditioner": Whether the apartment has air conditioner or not  
"has_alarms": Whether the apartment has alarms or not  
"has_elevator": Whether the apartment has elevators or not  
"has_ventilation": Whether the apartment has ventilation or not  
"has_freight_elevator": Whether the apartment has a freight elevator or not  
"has_furniture": Whether the apartment has furniture or not  
"has_telephone": Whether the apartment has a telephone or not  
"has_protection":Whether the apartment has protection or not  
"has_fridge": Whether the apartment has a fridge or not  
"has_washing_machine": Whether the apartment has a washing machine or not  
"has_dishwasher": Whether the apartment has a dishwasher  
"has_stove": Whether the apartment has a stove  
"has_oven": Whether the apartment has an oven  
"has_living_room": Whether the apartment has a living room  
"has_loggia": Whether the apartment has a loggia  
"has_veranda": Whether the apartment has a veranda  
"has_water": Whether the apartment has water  
"has_sewage": Whether the apartment has sewage  
"has_electricity": Whether the apartment has electricity  
"has_coded_door": Whether the apartment or building has a coded door  
"has_bed": Whether the apartment has a bed  
"has_sofa": Whether the apartment has a sofa  
"has_table": Whether the apartment has a table  
"has_chair": Whether the apartment has a char  
"has_kitchen_with_technology": Whether the apartment has a kitchen along with the technologies  
"has_storage_room": Whether the apartment has a storage room  
"for_investment": Maybe the characteristics of the apartment is different to be more attractive to investors compared to regular people.  
"user_type": What type of user is selling the house ("physical", "agent", "developer")    
"storeroom_type_id" - "storeroom_type": What type of storeroom does it have ("გარე სათავსო":Outdoor storage etc.)  
"storeroom_area": The are of the storeroom in square meters  
"material_type_id" - "material_type": What material is the building built with ("რკინა-ბეტონი":Reinforced concrete etc.)  
"rent_period": I don't know why a variable related to rent appeared  
"swimming_pool_type": Type of the swimming pool ("დახურული":Closed etc.)  
"living_room_type": Type of the living room ("სტუდიო":Studio, "გამოყოფილი":Separated etc.)  
"living_room_area": The area of the living room in square meters  
"porch_area": The of the porch in square meters  
"loggia_area": The area of the loggia in square meters  
"metro_station" - "metro_station_id": The nearby metro station  
"address" - "street_id": The address or the street of the building  
"Booking/AirBnb account": Boolean whether it has booking or airbnb account.  
"lat": Latitude coordinate of the Apartment  
"lng": Longitude coordinate of the Apartment  
"point_coordinates": Latitude and Longitude coordinates  
### Target Variable(s)
I think any of these variables could become a target variable to study.  
Be careful with using price and price per square meter in the same model, because price per square meter and area will easily explain price. Or price and area will easily explain price per square meter.  
"price_1_price_total": Price of Apartment in Lari based on the scraping date exchange rate  
"price_1_price_square": Price of Apartment in Lari per square meter  
"price_2_price_total": Price of Apartment in Dollars  
"price_2_price_square": Price of Apartment in Dollars per square meter  
"price_3_price_total": Price of Apartment in Euros (I think) based on the scraping date exchange rate  
"price_3_price_square": Price of Apartment in Euros per square meter  
"total_price": Price of Apartment in Dollars
### Trickier variables
"user_id": The id of the user who posted the statement for sale.  
"deal_type_id": Deal type should mean whether it's a sale or leasing or renting. This variable contains 2s other than 1s, which hints we may need to drop those observations.  
"real_estate_type_id": Has barely any variation, and don't know what the values mean   
"3d_url": Having a 3d_url may be a good sign, however too few apartments have it  
"youtube_link": A link to a youtube video for the apartment. Having a link good be a good sign. Only few apartments have it.  
"school_distance": A list of distances to nearby schools from the apartment. Only few have it  
"miscellaneous_distance": A list of distances to nearby establishments (could be a bank and many others). Only few have it  
"shop_distance": A list of distances to nearby shops. Only a few have it  
"fitness_distance": A list of distances to nearby fitness centers. Only a few have it  
"apothecary_distance": A list of distances to nearby apothecaries. Only a few have it  
"can_exchanged": Mostly False. I think it means that they are willing to exchange the apartment for another apartment or house  
"rent_type_id": Few houses have rent type. Most likely there's a mistake and these observations should be dropped.  
"currency_id": Mostly currency id is 2 (I think it means dollars). A few times it takes value 1 (Which most likely means Lari). Should be checked whether this causes problems or not in the data.  
"has_color": Mostly False. Maybe it means whether the apartment is painted or not.  
"is_vip": Mostly False. Could hint at a higher price apartment.  
"is_vip_plus": Mostly False. Could hint at a higher price apartment.  
"is_super_vip": Mostly False. Could hint at a higher price apartment.  
"has_chimney": Whether an apartment has a chimney. Mostly False  
"has_Jacuzzi": Whether an apartment has a jacuzzi. Mostly False  
"has_swimming_pool": Whether an apartment has a swimming pool. Mostly False  
"has_sauna": Whether an apartment has a sauna. Mostly False  
"has_spa": Whether an apartment has a spa. Mostly False  
"has_bar": Whether an apartment has a bar. Mostly False  
"has_gym": Whether an apartment has a gym. Mostly False  
"has_grill": Whether an apartment has a grill. Mostly False  
"airbnb_link": Link to airbnb account. Very few have it  
"booking_link": Link to booking account. Very few have it  
"uuid": Another ID, seems useless on the surface  
"project_id": Small number have a project_id. Having a project_id itself could be a variable.  
"project_uuid": Small number have a project_uuid. Having project_uidd itself could be a variable.  
"comment": The description of the apartment. Potentially contains extra info.  
"map_static_image": A 2D map image, maybe could locate nearby establishments  
"all_nearby_places_image": A 2D map image, maybe could locate nearby establishments  
"images_large": Pictures of an apartment. Out of scope for our project. Could be paired with neural networks.  
"images_blur": Pictures of an apartment. Out of scope for our project. Could be paired with neural networks.  
"images_thumb": Pictures of an apartment. Out of scope for our project. Could be paired with neural networks.  
"school_name": A list of nearby school names  
"school_lat": A list of nearby school latitude coordinate  
"school_lng": A list of nearby school longitude coordinate  
"miscellaneous_name": A list of various establishment names  
"miscellaneous_lat": A list of various establishment latitude coordinate  
"miscellaneous_lng": A list of various establishment longitude coordinate  
"shop_name": A list of nearby shop names  
"shop_lat": A list of nearby shop latitude coordinate  
"shop_lng": A list of nearby shop longitude coordinate  
"fitness_name": A list of nearby fitness names  
"fitness_lat": A list of nearby fitness latitude coordinate  
"fitness_lng": A list of nearby fitness longitude coordinate  
"apothecary_name": A list of nearby apothecary names  
"apothecary_lat": A list of nearby apothecary latitude coordinate  
"apothecary_lng": A list of nearby apothecary longitude coordinate  
"rs_code": I don't know what this is for  
"appear_rs_code": I don't know if this is useful  
"can_exchanged_comment": I think here there are comments like. Ready to trade it for another apartment or house in this location.  

# Data Cleaning and Engineering Documentation
The scripts here reflect the procedures me 
([@gdevdar](https://github.com/gdevdar)) and 
[@MalkhazBirtvelishvili](https://github.com/MalkhazBirtvelishvili) 
decided to employ to prepare our dataset for modeling 
purposes.

## Procedure breakdown
procedure.py runs functions from the following python files or codes sequentially in this order:
1. clean from clean_data.py
2. coordinate_fix.py
3. mistakes.py
4. urban_fix.py
5. duplicate_v2.py
6. drop_useless from clean_data.py
7. na_fix.py
8. urban_clean_up.py
9. location.py
10. engineer.py
11. comments.py

### clean_data.py
This file has to functions called 1. clean() and 2. drop_useless(). clean() removes observations
that are not apartment sales and somehow ended up in our data. drop_useless() is used to drop features that
were deemed to be unusable or unnecessary for our purpose.
### coordinate_fix.py
The coordinates were messed up in the data.

First latitude and longitude were reversed for most and normal for a few.

There were coordinates that were outside of Tbilisi.

This code fixes the coordinates and drops the observations that are outside of Tbilisi.

### urban_fix.py
Here we map urban_ids and urban_names to a new feature called 'urban'. We took the smaller administrative
units and combined them into bigger ones.

Additionally, the observations that were missing urban data were dropped.

### duplicate_v2.py
The script itself can be divided into three parts or stages which are further explained below
#### Why not a simple drop_duplicates()?
We are dealing with two types of duplicates: 1) Generated from the 
scraper fetching the same url twice 2) Different statements about 
the same apartment. Problem number one is straightforward to solve. 
In the case of the second problem Either an agent posts
the same sale many times to catch people's eyes, or an agent copies 
someone's statement reach a deal with the buyer instead
of the original seller for profit.

Such duplicates characteristically are not identical. They sometimes have
less or more parameters, depending on what the agent was feeling at the time.

However, there are a few variables that are consistently present, such as: 'lat', 'lng', 'floor', 'total_floors', 'area', 'room_type_id'.
So would the solution be to drop all the observations duplicated by these variables?

In a sense yes. Dropping this way is the safest method to ensure that all or most of the duplicates are removed
from the data. However, this method also removes statements that are not duplicates.
To avoid unnecessarily dropping data I have implemented duplicate_v2.py.

#### What does duplicate_v2.py do?
First it solves problem number one, dropping the same statements.

Then using these variables: 'lat', 'lng', 'floor', 'total_floors', 'area', 'room_type_id', it separates out the observations
that are duplicates based on these variables. Each duplicate group is assigned their own 'duplicate_group_id'.

Then within groups we compare pictures of the observations to each other.
For example a duplicate group that has 5 observations (They simply have the same values for
the features mentioned above). The first observation will be assigned its own unique id.
Then the second observation images are compared to the first one's. If the at least one image is the same
then the second observation takes the same id as the first observation. If they are not the same
second observation gets a unique id. Then the third observation is first compared to the first observation.
If they are the same it gets the id of the first observation, if not then it is compared to the second observation.
Same logic if same it gets the id of the second observation and if not it will get a unique id.
And so on with the fourth and fifth observations. Once all the observations in this groups are compared 
and give ids then the algorithm moves to another group of duplicates and does the same.

#### How does the comparison work?

We have a feature called 'images_large' and it contains urls to images for that statement.
First we have a function that collects images using these links. 
Then to compare the images we have two methods.
##### Method 1
After collecting images we create hashes of the images. Then we calculate
the hash distance between the hashes of the observations we are comparing.
And based on the lowest distance between the hashes we decide whether the observations are duplicate or not.
##### Method 2
If method 1 claims that the observations are duplicates then method 2 doesn't activate.
However, if method 1 didn't detect duplicates then method 2 practically double checks its work.
Method 2 is slower than method 1 but it detects image similarity much better.

In this case after collecting images, it converts them to grayscale images.
And then it uses RANSAC homography to count inliers, which I don't fully understand.
However, this method works better than the first one.

##### parallel comparisons
The dataframe before conducting comparisons is divided into batches in such a manner
that the observations in a duplicate group end up in the same batch.
And then the comparisons happen with method 1 and method 2 in parallel to save time.

### na_fix.py
Simple function that replaces NAs with -1
### urban_clean_up.py
There were observations that had coordinates that didn't match their urbans. Here the idea was to see whether the closest (based on coordinates) observations in the urban as this observation, and if not then this observation had the wrong urban, or wrong coordinates.  
After trial and error, removing observations that were more than 2 km away from the 30th closest observation within the same urban was the best.
### location.py
This was one of the major breakthroughs for this project.

It relies on the files generated by codes in the 'for_location' folder.
These codes are bus_stops.py, gyms.py, kindergarden.py, metro.py, parks.py, pharmacy.py, school.py,
school_clean.py and supermarket.py.

These codes basically generate coordinates for the respective establishments for Tbilisi.

And the purpose of the location.py is to calculate the distance from an observation in my data
to the nearest bus_stop, gym, kindergarden etc.  

location.py also calculates the number of nearby establishments, within a 1km, 500 meter, 200 meter or 100 meter radius. (e.g. number of schools nearby the apartment in a 500 meter radius would be one of the features created by location.py)
### engineer.py
This creates a few new variables from existing ones.
One is 'created_days_ago' which shows how many days ago the statement was created
Another is 'updated_days_ago' which shows how many days ago the statement was updated

### comments.py
Based on a list of words that appear in the comments the function create_comment_cols creates twelve  
new columns that take values 1 and 0 and are based on whether some words appear or not.  
The code is quite simple and for more details you can view comments.py itself.
