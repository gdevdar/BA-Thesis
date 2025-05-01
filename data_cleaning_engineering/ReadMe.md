# Cleaning & Engineering
The scripts here reflect the procedures me 
([@gdevdar](https://github.com/gdevdar)) and 
[@MalkhazBirtvelishvili](https://github.com/MalkhazBirtvelishvili) 
decided to employ to prepare our dataset for modeling 
purposes.

## How to run
### Requirements
- You need the .json data file that results from running our [Scraper](https://github.com/gdevdar/BA-Thesis/tree/main/scraper_2). You can download a sample dataset [here](https://drive.google.com/drive/folders/1jynW33dtleAp4EEcYoQLCxGC5BzM70UE?usp=sharing) to test out the code.
- You need [python](https://www.python.org/downloads/) installed. I use python 3.12, although python 3.13 should work just fine as well 
### Instructions
- You either need to download "data_cleaning_engineering" folder, or clone the whole repository
- Then place in the "data_cleaning_engineering" folder the .json data file that we mentioned as the first requirement
- Then Open the folder using your IDE and open terminal. or open cmd and navigate to the folder
- It may be wise to create a virtual environment first using:
```bash
python -m venv .venv
```
- And then activating the environment using one of the three alternatives

1. Git Bash
```bash
source .venv/scripts/activate
```
2. cmd
```cmd
.venv\Scripts\activate
```
3. PowerShell
```powershell
.venv\Scripts\Activate.ps1
```
- Run the following in the terminal:
```bash
pip install -r requirements.txt
```
- Then run the following in the terminal:
```bash
py procedure.py
```
- When it asks the name of the data file, simply input the name. (For example if you are using the sample dataset input: 2025-04-27.json)
- When it asks you the reference that, you should give it the date at which the data was scraped. The format is as such YYYY-MM-DD. (For example if you are using the sample dataset input 2025-04-27)
- Enjoy the show!!!

# Procedure breakdown
procedure.py runs functions from the following python files or codes sequentially in this order:
1. clean from clean_data.py
2. coordinate_fix.py
3. mistakes.py
4. urban_fix.py
5. duplicate_v2.py
6. drop_useless from clean_data.py
7. na_fix.py
8. location.py
9. engineer.py

## clean_data.py
This file has to functions called 1. clean() and 2. drop_useless(). clean() removes observations
that are not apartment sales and somehow ended up in our data. drop_useless() is used to drop features that
were deemed to be unusable or unnecessary for our purpose.
## coordinate_fix.py
The coordinates were messed up in the data.

First latitude and longitude were reversed for most and normal for a few.

There were coordinates that were outside of Tbilisi.

This code fixes the coordinates and drops the observations that are outside of Tbilisi.

## urban_fix.py
Here we map urban_ids and urban_names to a new feature called 'urban'. We took the smaller administrative
units and combined them into bigger ones.

Additionally, the observations that were missing urban data were dropped.

## duplicate_v2.py
The script itself can be divided into three parts or stages which are further explained below
### Why not a simple drop_duplicates()?
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

### What does duplicate_v2.py do?
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

### How does the comparison work?

We have a feature called 'images_large' and it contains urls to images for that statement.
First we have a function that collects images using these links. 
Then to compare the images we have two methods.
#### Method 1
After collecting images we create hashes of the images. Then we calculate
the hash distance between the hashes of the observations we are comparing.
And based on the lowest distance between the hashes we decide whether the observations are duplicate or not.
#### Method 2
If method 1 claims that the observations are duplicates then method 2 doesn't activate.
However, if method 1 didn't detect duplicates then method 2 practically double checks its work.
Method 2 is slower than method 1 but it detects image similarity much better.

In this case after collecting images, it converts them to grayscale images.
And then it uses RANSAC homography to count inliers, which I don't fully understand.
However, this method works better than the first one.

#### parallel comparisons
The dataframe before conducting comparisons is divided into batches in such a manner
that the observations in a duplicate group end up in the same batch.
And then the comparisons happen with method 1 and method 2 in parallel to save time.

## na_fix.py
Simple function that replaces NAs with -1
## location.py
This was one of the major breakthroughs for this project.

It relies on the files generated by codes in the 'for_location' folder.
These codes are bus_stops.py, gyms.py, kindergarden.py, metro.py, parks.py, pharmacy.py, school.py,
school_clean.py and supermarket.py.

These codes basically generate coordinates for the respective establishments for Tbilisi.

And the purpose of the location.py is to calculate the distance from an observation in my data
to the nearest bus_stop, gym, kindergarden etc.
## engineer.py
This creates a few new variables from existing ones.
One is 'created_days_ago' which shows how many days ago the statement was created
Another is 'updated_days_ago' which shows how many days ago the statement was updated
There's also 'has_project_id' which shows whether the observation has a 'project_id' or not
and 'vip' which is True when either of these three is true: is_vip, is_vip_plus and is_super_vip