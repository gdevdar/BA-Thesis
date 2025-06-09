def clean_mistakes(df):
    df = df[(df['price_2_price_square']>=300) & (df['price_2_price_square']<=8000)]
    df = df[(df['area']>=20) & (df['area']<=1000)]
    return df

def main():
    print("hi")

if __name__ == "__main__":
    main()