import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score

df = pd.read_csv('training.csv')
y = df.pop('cancelled_next_30d')
X = pd.get_dummies(df.drop(columns=['snapshot_at', 'customer_id']))
X = SimpleImputer().fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
model = RandomForestClassifier(random_state=42).fit(X_train, y_train)
print(roc_auc_score(y_test, model.predict_proba(X_test)[:, 1]))
