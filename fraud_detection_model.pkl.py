import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# Create sample training data (you should use real-world data)
X_train = np.array([
    [1000, 1],  # Fraud (Long document, fake ID detected)
    [1200, 0],  # Legitimate
    [1500, 1],  # Fraud
    [800, 0],   # Legitimate
    [1100, 1],  # Fraud
])
y_train = [1, 0, 1, 0, 1]  # 1 = Fraud, 0 = Legitimate

# Train Model
model = RandomForestClassifier(n_estimators=10, random_state=42)
model.fit(X_train, y_train)

# Save the trained model
joblib.dump(model, "fraud_detection_model.pkl")
print("✅ Fraud detection model saved as fraud_detection_model.pkl")
