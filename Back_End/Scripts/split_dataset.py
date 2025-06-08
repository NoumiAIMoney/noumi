import boto3
import pandas as pd
import s3fs
import io
import numpy as np
from sklearn.model_selection import train_test_split

s3 = boto3.client('s3')

def load_s3_csv(bucket, key):
    obj = s3.get_object(Bucket=bucket, Key=key)
    return pd.read_csv(io.BytesIO(obj['Body'].read())) # Return bytes

# LSTM dataset
df_lstm = load_s3_csv("noumi-datasets", "processed_50000_for_lstm.csv") # Load as a dictionary

# Isolation Forest dataset
df_iso = load_s3_csv("noumi-datasets", "processed_5000.csv")

# Split the dataset
df_lstm = df_lstm.sort_values('date')
train_lstm, val_lstm, test_lstm = np.split(df_lstm, [int(.7*len(df_lstm)), int(.85*len(df_lstm))])

train_iso, test_iso = train_test_split(df_iso, test_size=0.2, random_state=100)

# Save split files back to S3 for training
fs = s3fs.S3FileSystem()

train_lstm.to_csv('s3://noumi-datasets/lstm_train.csv', index=False)
val_lstm.to_csv('s3://noumi-datasets/lstm_val.csv', index=False)
test_lstm.to_csv('s3://noumi-datasets/lstm_test.csv', index=False)

train_iso.to_csv('s3://noumi-datasets/iso_train.csv', index=False)
test_iso.to_csv('s3://noumi-datasets/iso_test.csv', index=False)