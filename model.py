# Dependencies
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle 

#Generate synthetic data
np.random.seed(42)
N = 2000
def generate_data(n_samples):
    data = []
    for _ in range(n_samples):
        is_attack = np.random.choice([0, 1], p=[0.55, 0.45])
        if is_attack == 0:
            # Normal user behavior
            login_attempts       = np.random.randint(1, 6)
            failed_attempts      = np.random.randint(0, min(login_attempts, 3))
            avg_time_between     = np.random.uniform(10, 300)   # seconds — relaxed pace
            ip_change_frequency  = np.random.uniform(0, 0.2)    # rarely changes IP
        else:
            # Brute-force attack behavior
            login_attempts       = np.random.randint(15, 51)
            failed_attempts      = np.random.randint(int(login_attempts * 0.7), login_attempts)
            avg_time_between     = np.random.uniform(0.1, 5)    # very fast attempts
            ip_change_frequency  = np.random.uniform(0.3, 1.0)  # frequently rotates IPs

        failed_ratio = failed_attempts / max(login_attempts, 1)
        data.append({
            "login_attempts":        login_attempts,
            "failed_attempts":       failed_attempts,
            "failed_ratio":          round(failed_ratio, 4),
            "avg_time_between":      round(avg_time_between, 2),
            "ip_change_frequency":   round(ip_change_frequency, 4),
            "label":                 is_attack
        })
    return pd.DataFrame(data)
df = generate_data(N)
print(df.head(10))

# Prepare data for modeling (SPLIT TRAIN / TEST)
X = df[["login_attempts", "failed_attempts", "failed_ratio",
        "avg_time_between", "ip_change_frequency"]]
y = df["label"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)