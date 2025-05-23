# "აქსის"
# "ბაგებში"
# "სასწრაფოდ", "სასწრაფოოდ"
# "უცხოვრებელი"
# "მეორადი"
# "რემონტით"
# "პრესტიჟული","პრესტიჟულ", "ძვირადღირებული", "პრემიუმ", "უმაღლესი", "უნიკალური", "ულამაზესი","ექსკლუზიური","არაჩვეულებრივი"
# "გამორჩეული"
# "კომპლექსში", "კომპლექსია"
# "ხედი", "გადაჰყურებს", "ხედით"
# "იაფად"
# "ჭკვიანი"
# "მოპირკეთებულია"
# "ევროპული"

# The plan
# Create variables from these comments
# Variable should start with: word_{comment}
# Apply the comment creation to the dataset
# add this comment creation code to the data cleaning engineering folder
# Add documentation for the code
# Commit to githup
from pandas import Series
import re

def comment_columns(comment):
    if not comment:
        comment = ""
    has_comment_list = []
    # Each word list in the list corresponds to a feature
    words_list = [["აქსის","აქსისი"],
             ["ბაგებ","ბაგებში","ბაგები"],
             ["სასწრაფოდ","სასწრაფოოდ"],
             ["უცხოვრებელი"],
             ["მეორადი"],
             ["რემონტით"],
             ["პრესტიჟული","პრესტიჟულ", "ძვირადღირებული", "პრემიუმ", 
              "უმაღლესი", "უნიკალური", "ულამაზესი","ექსკლუზიური",
              "არაჩვეულებრივი","გამორჩეულ"],
             ["კომპლექს","კომპლექსში", "კომპლექსია"],
             ["იაფად","იაფი"],
             ["ჭკვიანი"],
             ["მოპირკეთებულია","მოპირკეთებული"],
             ["ევროპული"]
            ]
    # Goes through each set of words
    for words in words_list:
        for word in words:
            # Checks if this comment contains such a word
            check = 1 if re.search(r'\b' + re.escape(word) + r'\b', comment) else 0
            if check == 1:
                break
        # If it contained the word 1 is added to the list if not a 0 is added
        has_comment_list.append(check)
    return has_comment_list

def create_comment_cols(df):
    col_names = [
        'word_Axis',
        'word_Bagebi',
        'word_Urgent',
        'word_Unlived',
        'word_Secondary',
        'word_with_renovation',
        'word_prestigeous',
        'word_complex',
        'word_cheap',
        'word_smart',
        'word_paved',
        'word_european'
    ]
    df[col_names] = df['comment'].apply(lambda txt: Series(comment_columns(txt), index=col_names))
    return df

def main():
    from pandas import read_json
    df = read_json("new_2025-05-02.json")
    df = create_comment_cols(df)
    col_names = [
        'word_Axis',
        'word_Bagebi',
        'word_Urgent',
        'word_Unlived',
        'word_Secondary',
        'word_with_renovation',
        'word_prestigeous',
        'word_complex',
        'word_cheap',
        'word_smart',
        'word_paved',
        'word_european'
    ]
    counts = {col: df[col].value_counts() for col in col_names}
    value_counts_df = df[col_names] \
    .apply(lambda s: s.value_counts()) \
    .fillna(0).astype(int)
    for col in value_counts_df.columns:
        print(value_counts_df[col])
    #print(value_counts_df)
    #comment_columns(df['comment'][0])

if __name__ == "__main__":
    main()
