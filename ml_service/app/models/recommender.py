from utils import get_latest_processed_dataset
import pandas as pd

df = pd.read_csv(get_latest_processed_dataset())
print(df.info())
print(df.dtypes)
