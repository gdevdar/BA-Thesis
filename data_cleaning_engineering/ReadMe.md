### clean_data.py
```python
import importlib
import pandas as pd
import clean_data as dc
importlib.reload(dc) # You will need to install this package

# Example of usage
df = pd.read_json("05_04_2025.json")
df = dc.full_transform(df, reference_date = '2025-04-05')
```

# How to apply all the procedures


# Initial Cleaning (dropping observations and columns)

# Removing Duplicates
There are two sources for duplicates. First one 
emerges due  to the nature of our scraper.
The second one is due to one user or multiple users
posting the same apartment for sale many times.

Dealing with the first problem is trivial. 
Every statement has a unique ID. And simply removing
duplicates in terms of that ID solves the 
first problem entirely.

The second problem is much more tricky. 
There are two main problems: 1. It is possible for 
almost identical apartments to be sold 
at the same time (e.g. two apartments on the 
same floor, constructed in the same manner.) 2. 
The duplicate  statements don't necessarily have 
identical values for every feature. 
(e.g. one of the apartments may be missing some 
features. So instead of True there could be False,
or instead of some value there could be NAs)

The main challenge is differentiating whether 
the apartments have similar features because 
they are duplicates or because they are simply similar.

First we pick variables that are almost 
guaranteed to be the same across duplicated statements
these are: 'lat', 'lng', 'floor', 'total_floors', 'area', 'bedroom_type_id', 'room_type_id'.

After finding duplicates with these features. Give each
set of duplicates an ID. For example, ID = 1 will contain
the first set of duplicates, meaning they all have the same values
for the above-mentioned features. However, it is too soon
to claim them to be duplicates. To separate duplicates 
and simply similar apartments we relied on their images.

We have noticed that duplicate statements have identical images.
So we wrote an algorithm that fetches their images, 
converts them into hashes. Then measures the distance 
between the image hashes. If the images are too similar
then they are considered to be duplicates, if they are not
then they are deemed as separate statements.

This way we removed around 45% of our dataset.
# Inconsistent Values
## Inconsistency in the target variable

## Inconsistency in the coordinates
Inconsistency in the coordinates is dealt with using coordinate_fix.py.
Most of the coordinates in the data is reversed. latitude
is in the longitude column and vice versa.

First step to fixing is reversing latitude and longitude.
However, there are a few observations which didn't need reversing.
Then some observations still end up outside Tbilisi's coordinates.
Those that end up outside are either wrong coordinates, or some of them didn't need reversing.
We reverse the coordinates of those observations that are outside of Tbilisi.
And finally if after that reversion the coordinates of some observations are outside of Tbilisi.
Then those observations are dropped from the data.
## Inconsistency in balconies


# Missing Values
'condition_id' and 'condition'. They have missing values as the publisher of the statement
didn't provide the information. (After accounting for duplicates around 10% of the dataset has this problem).
This is too important of a variable to drop, therefore not having condition specified will be a separate input
into the model.

'district_id' and 'district_name'. Somehow there's 1 missing for district_id while 87 for district name (in my current dataset). 
MyHome.ge automatically fills in this kind of data after giving it the address, therefore this
is an error on their part.  
To tackle the issue we simply use the district_name and district_id
of the nearest apartment (based on coordinates) to fill out the missing values.

'urban_id' and 'urban_name'. Exactly same issue as district_id and district_name.
This also means they have the exact same solution.

'bedroom_type_id', missing value because they didn't provide a number.
However, when NA, the actual number of bedrooms can be 1,2,3 or any number.
We will replace NA with -1, and hope that model learns using this information.

'bathroom_type_id' and 'bathroom_type'. These variables are NA because the user didn't specify them.
NA doesn't mean that the apartment doesn't have a bathroom. Instead, we will give value -1 and
let the model learn the relationship.

'project_type_id'. This is NA when the user didn't input it.
We will assign -1 to capture some information.

'project_id'. This is mostly NA, and I think we shouldn't use it.

'hot_water_type_id' and 'hot_water_type'. When NA I will give it 0 or -1.

'heating_type_id' and 'heating_type'. When NA I will give it 0 or -1.

'parking_type_id' and 'parking_type'. Half of observations are NA. Parking types are many.
We think it's better to create a simpler variable called "has_parking"

'balconies' and 'balcony_area'. Even though it's NA half the time.
Most of the NAs have balconies. We will replace NA with -1.

'storeroom_type_id' and 'storeroom_type'. Very few are not NA.
Using many categories for something that only a few have doesn't sound optimal.
Therefore, it is better to have a "has_storeroom" variable instead.

'material_type_id' and 'material_type'. Replace Nans with -1.

'storeroom_area' mostly NA. I think should be dropped.

'swimming_pool_type'. We already have has swimming pool variable. Differentiating between types is not needed.

'living_room_type'. Mostly NA, and we don't think it is that useful.

'build_year'. Mostly NA as well. NA means that the user didn't specify it.
Plan to replace NA with -1 or 0.

'living_room_area', 'loggia_area', 'porch_area', 'waiting_space_area'. These variables are mostly NA.
They should either be dropped or replaced with a variable such as has_living_room, has_loggia, has_porch.



# Engineering Variables
'urban' - Engineered from 'urban_id' and 'urban_name'.
If there were missing values for both urban_id and urban_name, we dropped them.
If the urban was one of these 'კაკლები','კიკეთი','კოჯორი','ოქროყანა',
'ტაბახმელა','შინდისი','წავკისი','წყნეთი','ზემო ლისი', 'მუხათგვერდი','მუხათწყარო','თხინვალი'.
Then these observations were dropped.
Else we clustered the small urbans into bigger urbans, and gave them an English name.

# Resulting Set of Variables