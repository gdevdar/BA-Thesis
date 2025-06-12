
import pandas as pd

def main():
    df = pd.read_csv("tbilisi_k12_schools.csv")
    #print(df)
    # The name should include: "school" or "სკოლა".
    # And I will filter it that way

    condition = df['name'].str.contains(r'\bschool\b', case=False, na=False) \
                | df['name'].str.contains(r'\bსკოლა\b', case=False, na=False) \
                | df['name'].str.contains(r'\bschool\b', case=False, na=False) \
                | df['name'].str.contains(r'\bskola\b', case=False, na=False) \
                | df['name'].str.contains(r'\bსცჰოოლ\b', case=False, na=False)
    filtered_df = df[condition]
    filtered_df.to_csv('tbilisi_schools.csv', index = False)

if __name__ == "__main__":
    main()
