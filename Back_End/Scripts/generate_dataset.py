import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(100)
random.seed(100)

# Initialize Faker
fake = Faker()

# Constants
NUM_TRANSACTIONS = 5000
NUM_ACCOUNTS = 100
ANOMALY_RATE = 0.02
START_DATE = datetime(2024, 6, 1)
END_DATE = datetime(2025, 6, 30)
INITIAL_BALANCE = 10000

# Define merchants, categories, and MCCs
MERCHANTS = [fake.company() for _ in range(50)] + ['Amazon', 'Walmart', 'Target', 'Starbucks', 'Uber', 'Netflix']
ANOMALY_MERCHANTS = ['Unknown Vendor', 'Offshore Ltd', 'Suspicious Payee']
CATEGORIES = ['Retail', 'Food and Drink', 'Bills', 'Transportation', 'Entertainment', 'Transfer', 'Income']
ANOMALY_CATEGORIES = ['Fraud', 'Miscellaneous']
MCC_MAPPING = {
    'Retail': 5651, 'Food and Drink': 5812, 'Bills': 4900, 'Transportation': 4121,
    'Entertainment': 7832, 'Transfer': 4829, 'Income': 6012, 'Fraud': 9999, 'Miscellaneous': 7399
}

def generate_date():
    """Generate random date between start and end date."""
    time_delta = END_DATE - START_DATE
    random_days = random.randint(0, time_delta.days)
    return START_DATE + timedelta(days=random_days)

def generate_accounts_data():
    """Generate synthetic accounts data."""
    accounts = []
    for i in range(NUM_ACCOUNTS):
        account_id = f'ACC{i+1:03d}'
        monthly_income = round(random.uniform(3000, 15000), 2)
        suggested_savings_amount = round(monthly_income * 0.2, 2)
        # Simulate multiple balance snapshots per account
        for _ in range(50):  # ~50 snapshots per account to reach ~5,000 rows
            current = round(random.uniform(5000, 20000), 2)  # Vary balance
            available = current if random.random() < 0.8 else None  # 20% chance of null
            accounts.append({
                'account_id': account_id,
                'available': available,
                'current': current,
                'monthly_income': monthly_income,
                'suggested_savings': suggested_savings,
                'date': generate_date()  # For merging with transactions
            })
    return pd.DataFrame(accounts)

def compute_rolling_features(df_account):
    """Compute 30-day rolling features for a single account."""
    df_account = df_account.sort_values('date')
    df_account['days_since_txn'] = (pd.to_datetime('2025-06-30') - df_account['date']).dt.days
    df_account['is_income'] = (df_account['amount'] > 0).astype(int)

    # Initialize rolling features
    df_account['total_spent_30d'] = 0.0
    df_account['total_income_30d'] = 0.0
    df_account['txn_count_30d'] = 0
    df_account['avg_txn_amt_30d'] = 0.0
    df_account['std_txn_amt_30d'] = 0.0

    for idx in df_account.index:
        current_date = df_account.loc[idx, 'date']
        window = df_account[(df_account['date'] < current_date) & 
                           (df_account['date'] >= current_date - timedelta(days=30))]
        
        df_account.loc[idx, 'total_spent_30d'] = window[window['amount'] < 0]['amount'].sum()
        df_account.loc[idx, 'total_income_30d'] = window[window['amount'] > 0]['amount'].sum()
        df_account.loc[idx, 'txn_count_30d'] = len(window)
        df_account.loc[idx, 'avg_txn_amt_30d'] = window['amount'].mean() if len(window) > 0 else 0
        df_account.loc[idx, 'std_txn_amt_30d'] = window['amount'].std() if len(window) > 1 else 0

    df_account['net_cash_flow_30d'] = df_account['total_income_30d'] + df_account['total_spent_30d']
    return df_account

def generate_transactions_data(accounts_df):
    """Generate synthetic transactions data."""
    data = []
    account_balances = {row['account_id']: INITIAL_BALANCE for _, row in accounts_df.iterrows()}
    num_anomalies = int(NUM_TRANSACTIONS * ANOMALY_RATE)
    anomaly_indices = random.sample(range(NUM_TRANSACTIONS), num_anomalies)

    for i in range(NUM_TRANSACTIONS):
        is_anomaly = i in anomaly_indices
        transaction_id = f'TXN{i+1:06d}'
        account_id = random.choice(accounts_df['account_id'].unique())
        date = generate_date()

        # Normal transaction
        if not is_anomaly:
            if random.random() < 0.2:  # 20% chance of income
                amount = np.random.normal(2500, 500)
                amount = max(500, min(5000, amount))  # Clip income
                category = 'Income'
                merchant = random.choice(['Employer', 'Freelance', 'Investment'])
            else:
                amount = -abs(np.random.normal(100, 50))  # Negative for spending
                amount = max(-1000, min(-1, amount))  # Clip spending
                category = random.choice(CATEGORIES[:-1])  # Exclude Income
                merchant = random.choice(MERCHANTS)
        # Anomalous transaction
        else:
            anomaly_type = random.choice(['high_amount', 'unusual'])
            if anomaly_type == 'high_amount':
                amount = random.choice([
                    random.uniform(2000, 10000),  # High positive
                    -random.uniform(1000, 5000)   # High negative
                ])
                category = random.choice(ANOMALY_CATEGORIES)
                merchant = random.choice(ANOMALY_MERCHANTS)
            else:  # Unusual merchant/category
                amount = -abs(np.random.normal(100, 50))
                category = random.choice(ANOMALY_CATEGORIES)
                merchant = random.choice(ANOMALY_MERCHANTS)

        # Update balance
        account_balances[account_id] += amount
        balance = account_balances[account_id]
        
        # Prevent unrealistic balances
        if balance < -5000:
            account_balances[account_id] -= amount
            continue

        # Assign MCC
        mcc = MCC_MAPPING.get(category, 7399)
        
        # Generate description
        description = f"{'Deposit from' if category == 'Income' else 'Purchase at' if category not in ANOMALY_CATEGORIES else 'Payment to'} {merchant}"

        # Append transaction
        data.append({
            'transaction_id': transaction_id,
            'account_id': account_id,
            'amount': round(amount, 2),
            'date': date,
            'merchant_name': merchant,
            'merchant_category': category,
            'mcc': mcc,
            'balance_at_txn_time': round(balance, 2),
            'is_anomaly': int(is_anomaly)
        })

    return pd.DataFrame(data)

def merge_and_enrich(accounts_df, transactions_df):
    """Merge accounts and transactions, compute features."""
    # Merge on account_id and closest date
    transactions_df['date'] = pd.to_datetime(transactions_df['date'])
    accounts_df['date'] = pd.to_datetime(accounts_df['date'])
    
    merged_df = transactions_df.copy()
    for idx, row in merged_df.iterrows():
        account_id = row['account_id']
        txn_date = row['date']
        # Find closest account snapshot before or on transaction date
        account_rows = accounts_df[accounts_df['account_id'] == account_id]
        account_rows = account_rows[account_rows['date'] <= txn_date]
        if not account_rows.empty:
            closest_row = account_rows.iloc[account_rows['date'].sub(txn_date).abs().argmin()]
            merged_df.loc[idx, 'monthly_income'] = closest_row['monthly_income']
            merged_df.loc[idx, 'suggested_savings'] = closest_row['suggested_savings']
            merged_df.loc[idx, 'available'] = closest_row['available']
        else:
            # Fallback: use account's first available data
            account_row = accounts_df[accounts_df['account_id'] == account_id].iloc[0]
            merged_df.loc[idx, 'monthly_income'] = account_row['monthly_income']
            merged_df.loc[idx, 'suggested_savings'] = account_row['suggested_savings']
            merged_df.loc[idx, 'available'] = account_row['available']

    # Compute rolling features per account
    df_list = []
    for account_id in merged_df['account_id'].unique():
        df_account = merged_df[merged_df['account_id'] == account_id].copy()
        df_account = compute_rolling_features(df_account)
        df_list.append(df_account)
    
    final_df = pd.concat(df_list).sort_values(['account_id', 'date']).reset_index(drop=True)
    
    # Compute savings delta
    final_df['savings_delta'] = final_df['balance_at_txn_time'] - final_df['suggested_savings']
    
    # Fill NaN in std_txn_amt_30d
    final_df['std_txn_amt_30d'] = final_df['std_txn_amt_30d'].fillna(0)
    
    return final_df

def main():
    """Generate and save synthetic dataset."""
    accounts_df = generate_accounts_data()
    transactions_df = generate_transactions_data(accounts_df)
    final_df = merge_and_enrich(accounts_df, transactions_df)
    
    # Save to CSV
    final_df.to_csv('../Database/merge_dataset.csv', index=False)
    print("Dataset generated and saved as 'merge_dataset.csv'")
    print(final_df.head())

if __name__ == "__main__":
    main()