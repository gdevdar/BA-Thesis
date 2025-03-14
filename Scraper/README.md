# The Scraper
We are scraping this url:
https://www.myhome.ge/s/iyideba-bina-Tbilisshi/?deal_types=1&real_estate_types=1&cities=1&urbans=38,39,40,41,42,43,44,45,46,47,101,28,30,48,106,111,121,29&districts=4&currency_id=1&CardView=2&page={n}  
At the end of the link you see {n}, which is simply a number corresponding to the page that is being scraped. (If you want to open the link you need to replace {n} with an actual number)

The pages from this link contain statements from myhome.ge.  
However, to simplify the problem the statements are filtered to only include: Apartments that are being sold at Vake-Saburtalo.

You can find the code for the scraper itself in 
this folder as "Scraper.ipynb".
It includes two main functions.  

The first function goes through the pages of 
the url provided above. It creates a webdriver to 
simulate human behavior and then fetches the 
website. After fetching the website it finds 
the relevant links (links leading to 
individual pages for the statements) and 
stores them in a list. And the final output 
is basically a huge list of links to the statement 
pages.

The second function goes through the links from the 
first function. Finds the data and places them in a dataframe
 which will then be used for training the model.

The data from scraping is stored in the file: "data.csv"
# The Data
In many cases some of the data is not available.
This is because when a house doesn't have a balcony, 
for example, it doesn't show up, and therefore is 
stored as NA. Therefore, NAs should be interpreted
as not having in some cases and in others as 0s.

Below I will explain what each variable corresponds to:  
- price (ფასი):  
  - "price_total_1" - price in Lari (ფასი ლარებში) 
  - "price_total_2" - price in US dollars (ფასი დოლარებში)
  - "price_total_3" - price in Euros (ფასი ევროებში) 
- "Area (sq m)" - Area of apartment in square meters (ფართი მ^2)
- "area_type_id" - Area type id (Have to figure out)
- Area vs price (ფართი vs ფასი):
  - "price_square_1" - How much does 1 square meter cost in Lari (1 მ^2 - x ლარი)
  - "price_square_2" - How much does 1 square meter cost in US dollars (1 მ^2 - x დოლარი)
  - "price_square_3" - How much does 1 square meter cost in Euros (1 მ^2 - x ევრო)
- "owner_name" - Name of the owner (გამყიდვლის სახელი)
- "user_phone_number" - Phone number of the owner (გამყიდვლის ნომერი)
- "ID" - Unique identifier for the houses. https://www.myhome.ge/pr/{ID}. Can be used to navigate to the statement pages.
- "dynamic_title" - Title in Georgian
- "dynamic_slug" - Title but with latin letters
- "created_at" - Date of creation for the statement (შექმნის თარიღი)
- "last_updated" - Last update date of the statement (ბოლო განახლების თარიღი)
- "views" - Num of Views (ნახვები)
- "address" - Address of the house (მისამართი)
- Other Variables for Location:
  - "Latitude", "Longitude", "point_coordinates" - Coordinates (კოორდინატები)
  - "street_id" - Street ID (ქუჩის ID)
  - "City" - City the apartment is located in (ქალაქი)
  - "city_id" - City ID (ქალაქის ID)
  - "District" - District of the house (რაიონი)
  - "district_id" - District ID (რაიონის ID)
  - "Urban" - The urban area of the house (უბანი)
  - "urban_id" - Urban ID (უბნის ID)
  - "nearby_places" - List of nearby places such as schools, hospitals etc. (This one needs further research)
  - "metro_station_name" - The metro station the house is near to (ახლოსმდებარე მეტრო)
  - "metro_station_id" - ID of the metro station (მეტროს ID)
- "room_type_id" - Number of rooms in the apartment (Not actually an ID) (ოთახი (რაოდენობა))
- "bedroom_type_id" - Number of bedrooms in the apartment (Not ID) (საძინებელი (რაოდენობა))
- "Floor" - The floor on which the apartment is (სართული (რომელზეც ბინაა))
- "Total Floors" - The number of floors the whole building has (ჯამში სართულების რაოდენობა)
- "comment" - Short description of the apartment (მოკლე აღწერა)
- "status_id" - Status of the building (1 - ძველი აშენებული (Old building), 2 - ახალი აშენებული (New Building), 3 - მშენებარე (Being Built))
- "condition", "condition_id" - Condition of the apartment (მდგომარეობა)
- Project type:
  - "project_type_id" - Project Type ID (პროექტის ტიპის ID) (Needs to be researched)
  - "project_id" - Project ID (პროექტის ID)
  - "project_uuid" - Project UUID (პროექტის UUID)
- "bathroom_type_id" - Number of bathrooms (სვ. წერტილები (რაოდენობა))
- "build_year" - Time period when built (აშენების წელი (ტექსტური მონაცემი, წლების შუალედები))
- "height" - Height of the ceiling in meters (ჭერის სიმაღლე (მ))
- "heating_type_id" - The heating system type (გათბობა (გათბობის სისტემა)) (1 - ცენტრალური გათბობა, 6 - გათბობის გარეშე)
- "parking_type_id" - Type of parking available (პარკირება) (2 - პარკინგის ადგილი, 4 - ეზოს პარკინგი)
- "hot_water_type" - Hot water type written in Georgian (ცხელი წყალი)
- "hot_water_type_id" - Hot water type ID
- "material_type_id" - Building material (სამშენებლო მასალა) (Needs to be mapped)
- "balconies" - Number of balconies (აივანი (რაოდენობა))
- "balcony_area" - Area of balconies in square meters (აივანი (ფართობი მ^2))
- "storeroom_type_id" - Type of storeroom (სათავსოს ტიპი)
- "storeroom_area" - Area of store room (სათავსოს ფართობი)
- "Parameter_name" - Contains the furniture, or some other characteristic that the apartment has. For example: an oven, water, electricity etc.
- "Parameter_ID" - Contains IDs instead of names
- "Parameter_type" - Contains types of the parameters to easily group them
- "deal_type_id" - What type of deal it is (In this case all should just be selling deal) (გარიგების ტიპი)
- "real_estate_type_id" - Type of real estate (In this case apartment for all) (უძრავი ქონების ტიპი)
- "yard_area" - Area of the yard (ეზოს ფართი)
# Permission to Scrape
In this folder there's a pdf file: "ISET Mail - ინფორმაციის გამოთხოვნა.pdf"
that contains the email exchanges 
with myhome.ge. There they allow us to 
use a scraper to gather the publicly available 
data on their website.