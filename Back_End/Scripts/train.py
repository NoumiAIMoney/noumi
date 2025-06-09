# This file acts as an entry point to start training the LSTM model
import sagemaker
from sagemaker.pytorch import PyTorch

role = "arn:aws:iam::686255967431:role/service-role/AmazonSageMaker-ExecutionRole-20250528T183410"
bucket = 'noumi-datasets'
region = 'us-east-1'

estimator = PyTorch(
    entry_point='lstm_train.py',
    role=role,
    framework_version='1.13',
    py_version='py39',
    instance_count=1,
    instance_type='ml.m5.large',
    hyperparameters={
        'epochs': 20,
        'batch_size': 32,
        'lr': 0.001,
        'window_size': 10
    },
    output_path=f's3://{bucket}/models/lstm/'
)

estimator.fit({
    'train': f's3://{bucket}/lstm_train.csv',
    'val': f's3://{bucket}/lstm_val.csv'
})