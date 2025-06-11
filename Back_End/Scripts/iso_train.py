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
store_date = iso_test['date'].copy()

# Features
columns_to_keep = [
    'amount', 'month', 'day',
    'rolling_spend_7d', 'prev_transaction_amt',
    'day_of_week_Friday', 'day_of_week_Monday', 'day_of_week_Saturday',
    'day_of_week_Sunday', 'day_of_week_Thursday', 'day_of_week_Tuesday', 'day_of_week_Wednesday',
    'local_time_bucket_Night', 'local_time_bucket_Morning', 'local_time_bucket_Afternoon',
    'local_time_bucket_Evening', 'local_time_bucket_Late Night',
    'is_weekend_False', 'is_weekend_True'
]

# Cast to float
X_train = iso_train[columns_to_keep].astype(float)
X_test = iso_test[columns_to_keep].astype(float)

# Initialize isolation forest from sklearn
clf = IsolationForest(contamination=0.05, random_state=100)
clf.fit(X_train)

# Store model.pkl
with open('../Models/isolation_forest_model.pkl', 'wb') as f:
    pickle.dump(clf, f)

# Compute anomaly scores 
scores = clf.decision_function(X_test) # Predicts the anomalous score
preds = clf.predict(X_test) # Binary classification (anomaly / non-anomaly) 

# Align anomaly scores with date
result_df = pd.DataFrame({
    'date': store_date,
    'anomaly_score': scores,
    'anomaly_label': preds  
})

# Save to CSV
csv_buffer = io.StringIO()
result_df.to_csv(csv_buffer, index=False)

# Upload to S3
s3.put_object(
    Bucket='noumi-datasets',
    Key='iso_results/anomaly_scores.csv',
    Body=csv_buffer.getvalue()
)