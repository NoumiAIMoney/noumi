import boto3
import pandas as pd
import s3fs
import io
import numpy as np
from sklearn.model_selection import train_test_split

s3 = boto3.client('s3')

def load_s3_csv(bucket, key):
    obj = s3.get_object(Bucket=bucket, Key=key)
    return pd.read_csv(io.BytesIO(obj['Body'].read()))

# Load the merged dataset
# df_iso = load_s3_csv("noumi-datasets", "merge_dataset.csv") # Assuming it's uploaded to S3
# For local testing, assuming merge_dataset.csv is in Back_End/Database/
try:
    df_iso = pd.read_csv('../Database/merge_dataset.csv')
except FileNotFoundError:
    print("Error: merge_dataset.csv not found. Make sure it's in the Back_End/Database/ directory or adjust the path.")
    exit()


# LSTM dataset (Commented out as per request)
# df_lstm = load_s3_csv("noumi-datasets", "processed_50000_for_lstm.csv")

# Isolation Forest dataset (using the new merge_dataset.csv)
# df_iso = load_s3_csv("noumi-datasets", "processed_5000.csv") # Old line

# Split the dataset
# df_lstm = df_lstm.sort_values('date') # LSTM part
# train_lstm, val_lstm, test_lstm = np.split(df_lstm, [int(.7*len(df_lstm)), int(.85*len(df_lstm))]) # LSTM part

# Ensure 'date' column is in datetime format if it's being used for sorting or time-based splits
# For Isolation Forest, if 'date' is not directly used in splitting strategy other than being a column,
# direct train_test_split is fine.
# If a chronological split is needed for iso as well, df_iso should be sorted by date first.
# Assuming a random split is acceptable for Isolation Forest as per the original script.
df_iso['date'] = pd.to_datetime(df_iso['date']) # Ensure date is in correct format for potential sorting
df_iso = df_iso.sort_values('date') # Optional: sort if a chronological split is preferred for consistency, though random_state is used.

train_iso, test_iso = train_test_split(df_iso, test_size=0.2, random_state=100) #Original split strategy for iso

# Save split files back to S3 for training
fs = s3fs.S3FileSystem() # This requires s3fs and appropriate AWS credentials configured

# LSTM part (Commented out)
# train_lstm.to_csv('s3://noumi-datasets/lstm_train.csv', index=False)
# val_lstm.to_csv('s3://noumi-datasets/lstm_val.csv', index=False)
# test_lstm.to_csv('s3://noumi-datasets/lstm_test.csv', index=False)

train_iso.to_csv('s3://noumi-datasets/iso_train.csv', index=False)
test_iso.to_csv('s3://noumi-datasets/iso_test.csv', index=False)

print("Dataset splitting complete. Isolation forest train and test sets saved to S3.")