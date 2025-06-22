# Train isolation forest locally
import boto3
import pandas as pd
import s3fs
import io
import pickle
from sklearn.ensemble import IsolationForest

s3 = boto3.client('s3')

def load_s3_csv(bucket, key):
    obj = s3.get_object(Bucket=bucket, Key=key)
    return pd.read_csv(io.BytesIO(obj['Body'].read())) 

# Load dataset from S3 bucket
iso_train = load_s3_csv("noumi-datasets", "iso_train.csv")
iso_test = load_s3_csv("noumi-datasets", "iso_test.csv")

# Store transaction_id and date for later use, ensure they are from the test set
# and align with X_test before it's modified (e.g. dropping columns).
# It's crucial that store_date and store_ids are taken *before* X_test is redefined with only feature columns.
iso_test_original_indices = iso_test.index # Keep original indices if any shuffling or reindexing happens
store_date = iso_test['date'].copy()
store_ids = iso_test['transaction_id'].copy() # Assuming 'transaction_id' is present for identifying transactions


# Features - Updated to reflect merge_dataset.csv structure
# We need to select numerical features that are suitable for Isolation Forest.
# Categorical features like 'merchant_name', 'merchant_category' would need encoding (e.g., one-hot or target encoding).
# For now, let's select a revised set of numerical and potentially some easily encodable categoricals if necessary,
# or focus on numerical ones first.
# Date components like month, day, day_of_week can be extracted if deemed useful.

# Convert 'date' to datetime and extract features
iso_train['date'] = pd.to_datetime(iso_train['date'])
iso_test['date'] = pd.to_datetime(iso_test['date'])

iso_train['month'] = iso_train['date'].dt.month
iso_train['day'] = iso_train['date'].dt.day
iso_train['day_of_week'] = iso_train['date'].dt.dayofweek # Monday=0, Sunday=6

iso_test['month'] = iso_test['date'].dt.month
iso_test['day'] = iso_test['date'].dt.day
iso_test['day_of_week'] = iso_test['date'].dt.dayofweek

# One-hot encode 'day_of_week'
iso_train = pd.get_dummies(iso_train, columns=['day_of_week'], prefix='dow')
iso_test = pd.get_dummies(iso_test, columns=['day_of_week'], prefix='dow')

# Define features to use for the model
# Focusing on numerical features from merge_dataset.csv
# 'amount' is key. 'balance_at_txn_time' could be useful.
# Calculated features like 'days_since_txn', 'total_spent_30d', 'total_income_30d',
# 'txn_count_30d', 'avg_txn_amt_30d', 'std_txn_amt_30d', 'net_cash_flow_30d', 'savings_delta'
# are likely very informative.
columns_to_keep = [
    'amount', 'balance_at_txn_time', 'monthly_income',
    'suggested_savings_amount', 'available', 'days_since_txn',
    'total_spent_30d', 'total_income_30d', 'txn_count_30d',
    'avg_txn_amt_30d', 'std_txn_amt_30d', 'net_cash_flow_30d', 'savings_delta',
    'month', 'day', # Extracted date features
    # Add one-hot encoded day_of_week columns (example, adjust based on actual dummy columns created)
    # These will be like dow_0, dow_1, ..., dow_6
]
# Add dow columns dynamically
dow_cols_train = [col for col in iso_train.columns if 'dow_' in col]
dow_cols_test = [col for col in iso_test.columns if 'dow_' in col]
# Ensure consistency in columns between train and test after one-hot encoding
common_dow_cols = list(set(dow_cols_train) & set(dow_cols_test))
columns_to_keep.extend(common_dow_cols)

# Align columns for train and test sets to ensure they are identical
# This handles cases where a particular day of week might not be in one of the splits
all_possible_dow_cols = [f'dow_{i}' for i in range(7)]
for col in all_possible_dow_cols:
    if col not in iso_train.columns:
        iso_train[col] = 0
    if col not in iso_test.columns:
        iso_test[col] = 0
# Re-ensure common_dow_cols includes all dow_0 to dow_6 if they were added.
columns_to_keep = [c for c in columns_to_keep if 'dow_' not in c] # remove previous dow entries
columns_to_keep.extend(all_possible_dow_cols) # add all possible ones
columns_to_keep = list(set(columns_to_keep)) # Remove duplicates if any


# Handle potential missing columns if a feature is not present in the dataset
# (e.g. if 'std_txn_amt_30d' is all NaN for some reason and gets dropped, or if merge_dataset is different)
final_columns_to_keep_train = [col for col in columns_to_keep if col in iso_train.columns]
final_columns_to_keep_test = [col for col in columns_to_keep if col in iso_test.columns]

# Ensure X_train and X_test have the exact same columns in the same order
# This is critical if some features were entirely missing in one set after preproc, or if a dow wasn't present.
common_features = list(set(final_columns_to_keep_train) & set(final_columns_to_keep_test))

X_train = iso_train[common_features].astype(float).fillna(0) # Fill NaNs with 0, a common strategy
X_test = iso_test[common_features].astype(float).fillna(0)   # Fill NaNs with 0

# Re-align store_date and store_ids with X_test's final indices if any filtering/dropping happened
# This is important because train_test_split shuffles, and further operations might re-index.
# Using .loc with original indices of iso_test ensures correct alignment.
store_date = iso_test.loc[X_test.index, 'date']
store_ids = iso_test.loc[X_test.index, 'transaction_id']


# Initialize isolation forest from sklearn
clf = IsolationForest(contamination=0.05, random_state=100) # Contamination can be tuned
clf.fit(X_train)

# Store model.pkl
model_path = '../Models/isolation_forest_model.pkl'
with open(model_path, 'wb') as f:
    pickle.dump(clf, f)
print(f"Model saved to {model_path}")

# Compute anomaly scores 
scores = clf.decision_function(X_test) # Predicts the anomalous score
preds = clf.predict(X_test) # Binary classification (anomaly / non-anomaly), -1 for outliers, 1 for inliers

# Align anomaly scores with date and transaction_id
result_df = pd.DataFrame({
    'transaction_id': store_ids,
    'date': store_date,
    'anomaly_score': scores,
    'anomaly_label': preds
})

# Save to CSV locally in Database/Anomaly_Scores
output_dir = "../Database/Anomaly_Scores"
import os
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
output_path = os.path.join(output_dir, "isolation_forest_anomaly_scores.csv")

result_df.to_csv(output_path, index=False)
print(f"Anomaly scores saved to {output_path}")

# Upload to S3 (Commented out as per request to save locally first)
# csv_buffer = io.StringIO()
# result_df.to_csv(csv_buffer, index=False)
# s3.put_object(
#     Bucket='noumi-datasets', # S3 bucket remains the same if needed in future
#     Key='iso_results/anomaly_scores.csv', # S3 key remains the same
#     Body=csv_buffer.getvalue()
# )
# print("Anomaly scores also uploaded to S3: s3://noumi-datasets/iso_results/anomaly_scores.csv")