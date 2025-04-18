import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# Improved Sample Training Data
X_train = np.array([
    [500, 1],   # Fraud (Short doc, Fake ID detected)
    [1200, 0],  # Legitimate
    [1500, 1],  # Fraud (Long doc, Fake ID detected)
    [800, 0],   # Legitimate
    [1100, 1],  # Fraud
    [700, 1],   # Fraud
    [300, 0],   # Legitimate
    [1000, 1],  # Fraud
    [600, 0],   # Legitimate
    [200, 0],   # Legitimate
])

y_train = [1, 0, 1, 0, 1, 1, 0, 1, 0, 0]  # Labels: 1 = Fraud, 0 = Legitimate

# Train Model
model = RandomForestClassifier(n_estimators=50, random_state=42)  # Increased trees for accuracy
model.fit(X_train, y_train)

# Save the trained model
joblib.dump(model, "fraud_detection_model.pkl")
print("✅ New fraud detection model saved as fraud_detection_model.pkl")
