### clean_data.py
```python
import clean_data as dc
importlib.reload(dc) # You will need to install this package

# Example of usage
df = pd.read_json("05_04_2025.json")
df = dc.full_transform(df, reference_date = '2025-04-05')
```