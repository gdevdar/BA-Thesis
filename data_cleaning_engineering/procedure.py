# First should come dropping columns

# Then we drop the useless observations

# Then we fix the coordinates

# Then we fix the urban stuff

# Then we do the duplicates stuff

# Deal with NAs

def procedure(path,reference_date):
    df = read_json(path)
    df = clean(df)
    df = coordinate_fix(df)
    df = clean_mistakes(df)
    df = urban_fix(df)
    df = dup.deduplicate(df)
    #df = df.drop_duplicates(subset = 'id')
    df = df.drop(['images_large'], axis=1)
    df = drop_useless(df)
    df = fill_na(df) # Replaces NAs with -1
    df = location_clean_up(df)
    df = create_location_features(df)
    df = engineer(df,reference_date = reference_date)
    df = create_comment_cols(df)

    #dup.full_procedure(path)
    #df = read_json("for_duplicate/duplicate_free.json")
    #df = read_json(path) # Importing the base data
    #df = clean(df) # Removing inconsistent data using deal_type_id, real_estate_type_id and rent_type_id
    #df = drop_useless(df) # Dropping features that were deemed useless
    #df = coordinate_fix(df) # Removing coordinates outside of Tbilisi, and fixing inconsistencies
    #df = urban_fix(df) # Creating new Urban variable and dropping bad observations


    #dup.full_procedure(path)
    # The duplicate procedure should run last. And I think it should take as input the df I generate here.
    return df

def main():
    path = input("What is the name of the data file?\n")
    reference_date = input("What is the reference date/Scraping date of the data file?\n")
    #path = '2025-04-19.json'
    #reference_date = '2025-04-19'
    df = procedure(path,reference_date)
    print(df.head())
    for col in df.columns:
        print(col)
    print(df.shape[0])

from pandas import read_json
from data_cleaning_engineering.clean_data import clean
from data_cleaning_engineering.clean_data import drop_useless
from data_cleaning_engineering.coordinate_fix import coordinate_fix
from data_cleaning_engineering.urban_fix import urban_fix
from data_cleaning_engineering.na_fix import fill_na
from data_cleaning_engineering import duplicate_v2 as dup
from data_cleaning_engineering.location import create_location_features
from data_cleaning_engineering.engineer import engineer
from data_cleaning_engineering.mistakes import clean_mistakes
from data_cleaning_engineering.comments import create_comment_cols
from data_cleaning_engineering.urban_clean_up import location_clean_up

if __name__ == "__main__":
    main()