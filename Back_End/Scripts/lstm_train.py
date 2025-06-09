"""
File overview:
- Trains the LSTM autoencoder on the training data.
- Uses the trained model to generate reconstructions for the validation data.
- Computes the reconstruction error per validation sample, and stores that as an anomaly score.
- Saves those anomaly scores alongside account IDs to CSV and uploads it to S3.
- Saves the trained model checkpoint.
"""

import os
import pandas as pd
import torch
import boto3
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

# LSTM model
class LSTMAnomalyDetector(nn.Module):
    def __init__(self, input_size, hidden_size=32, num_layers=1):
        super(LSTMAnomalyDetector, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.output = nn.Linear(hidden_size, input_size)

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        return self.output(lstm_out)
    
# Load datasets
train_df = pd.read_csv("/opt/ml/input/data/train/lstm_train.csv")
val_df = pd.read_csv("/opt/ml/input/data/val/lstm_val.csv")

# Drop unnecessary columns
val_store_id = val_df['account_id'] # Store account id for later
train_df = train_df.drop(columns=['account_id', 'date', 'merchant_name'])
val_df = val_df.drop(columns=['account_id', 'date', 'merchant_name'])

# Cast the types into float
train_df = train_df.select_dtypes(include=[float, int, bool]).astype('float32')
val_df = val_df.select_dtypes(include=[float, int, bool]).astype('float32')

# Convert to tensors & format it to suit NN
X_train = torch.tensor(train_df.values, dtype=torch.float32).unsqueeze(1)
X_val = torch.tensor(val_df.values, dtype=torch.float32).unsqueeze(1)

train_loader = DataLoader(TensorDataset(X_train, X_train), batch_size=32, shuffle=True) # Load training set as both inputs & labels

# Setup
input_size = X_train.shape[2]
model = LSTMAnomalyDetector(input_size=input_size)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001) # Use gradient descent for weight optimization
 
# Training loop
for epoch in range(10):
    model.train()
    for batch_X, _ in train_loader:
        output = model(batch_X)
        loss = criterion(output, batch_X)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    print(f"Epoch {epoch+1} Loss: {loss.item():.4f}")
    
# Compute anomaly score
with torch.no_grad():
    model.eval()
    outputs = model(X_val)
    reconstruction_errors = torch.mean((outputs - X_val) ** 2, dim=(1, 2))

# Convert to numpy
anomaly_scores = reconstruction_errors.cpu().numpy()

# Create a new dataframe with account_id and anomaly_score
anomaly_df = pd.DataFrame({'account_id': val_store_id})
anomaly_df['anomaly_score'] = anomaly_scores

# Save locally in training container
output_csv_path = '/opt/ml/model/anomaly_scores.csv'
anomaly_df.to_csv(output_csv_path, index=False)

# Upload anomaly_scores.csv to S3
s3_client = boto3.client('s3')
bucket_name = 'noumi-datasets'
s3_key = 'lstm_results/anomaly_scores.csv'

s3_client.upload_file(output_csv_path, bucket_name, s3_key)
print(f"Uploaded anomaly scores CSV to s3://{bucket_name}/{s3_key}")

# Save model
model_dir = "/opt/ml/model"
os.makedirs(model_dir, exist_ok=True)
torch.save(model.state_dict(), os.path.join(model_dir, "lstm_model.pth"))

"""
Next steps:
- Evaluate the model by plotting visualizations of the reconstruction errors
"""