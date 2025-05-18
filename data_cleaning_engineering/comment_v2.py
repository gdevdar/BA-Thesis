import re
from collections import Counter
import pandas as pd


def compute_word_price_correlations(df, word_cols, target_col='price_per_square'):
    """
    Returns a pandas Series of Pearson correlations between each boolean word_col
    and the numeric target_col.
    """
    corrs = {}
    # Ensure target variable is numeric and drop rows where it's missing
    series_y = pd.to_numeric(df[target_col], errors='coerce')
    for col in word_cols:
        # Drop rows where y is NaN
        valid = series_y.notna()
        x = df.loc[valid, col].astype(int)  # convert bool → 0/1
        y = series_y[valid]
        corrs[col] = x.corr(y)
    # Build a Series and sort ascending (so strongest negative first, positive last)
    corr_series = pd.Series(corrs).sort_values()
    return corr_series


import re
import pandas as pd

def add_boolean_word_cols(df, text_col, words):
    """
    Builds one Boolean Series per word, then concatenates them all at once.
    """
    # Pre-compile word boundary regexes
    regexes = {
        word: re.compile(rf'\b{re.escape(word)}\b', flags=re.IGNORECASE)
        for word in words
    }

    # Build a dict of column_name -> Series
    flag_series = {}
    filled = df[text_col].fillna('').astype(str)
    for word, regex in regexes.items():
        col_name = f'col_{word}'
        # Apply once, store Series
        flag_series[col_name] = filled.str.contains(regex)

    # Create a DataFrame of flags
    flags_df = pd.DataFrame(flag_series, index=df.index)

    # Concatenate all at once
    df = pd.concat([df, flags_df], axis=1)

    # (Optional) de-fragment if you'll do more inserts later
    df = df.copy()

    return df


def count_observations(comments):
    df_counter = Counter()
    for comment in comments:
        # here we KNOW comment is str
        words = re.findall(r'\w+', comment.lower())
        df_counter.update(set(words))
    return dict(df_counter)


def main():
    df = pd.read_json('new_2025-05-02.json')
    # cleanse your text column
    comments = df['comment'].dropna().astype(str)

    # safe to call now
    doc_freq = count_observations(comments)

    # rest of your workflow…
    frequent_words = [w for w, f in doc_freq.items() if f >= 100]
    df = add_boolean_word_cols(df, text_col='comment', words=frequent_words)
    corr_series = compute_word_price_correlations(df, [f'col_{w}' for w in frequent_words])
    # 1) Sort from highest to lowest
    corr_series = corr_series.sort_values(ascending=False)
    # 2) Save to CSV
    corr_series.to_csv('word_price_correlations_sorted_desc.csv', header=['correlation'])
    sig_corrs = corr_series[corr_series.abs() > 0.04]
    print(sig_corrs)


if __name__ == "__main__":
    main()
