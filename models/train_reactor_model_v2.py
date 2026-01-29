"""
Training script for Chemical Reactor Anomaly Detection model v2.

Uses RandomForestClassifier instead of LogisticRegression for a non-linear
decision boundary. Same data, same features, different model architecture.

Usage:
    python train_reactor_model_v2.py
"""

import numpy as np
from pathlib import Path
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import StandardScaler


# Feature ranges — identical to v1
FEATURE_RANGES = {
    "temperature": (60, 120),
    "pressure": (1, 10),
    "flow_rate": (5, 50),
    "reactant_concentration": (0.5, 2.0),
    "ph_level": (4, 10),
    "stirrer_speed": (100, 500),
}

FEATURE_NAMES = list(FEATURE_RANGES.keys())


def generate_synthetic_data(n_samples: int = 5000, random_seed: int = 42) -> tuple:
    """
    Generate synthetic chemical reactor data — identical to v1.

    Same data generation ensures differences come from the model, not the data.
    """
    np.random.seed(random_seed)

    features = np.zeros((n_samples, len(FEATURE_NAMES)))
    for i, (name, (low, high)) in enumerate(FEATURE_RANGES.items()):
        features[:, i] = np.random.uniform(low, high, n_samples)

    temperature = features[:, 0]
    pressure = features[:, 1]
    concentration = features[:, 3]
    ph_level = features[:, 4]
    stirrer_speed = features[:, 5]

    anomaly_prob = np.full(n_samples, 0.05)
    anomaly_prob += 0.3 * (temperature > 105).astype(float)
    anomaly_prob += 0.15 * ((temperature > 95) & (temperature <= 105)).astype(float)
    anomaly_prob += 0.25 * (pressure > 8).astype(float)
    anomaly_prob += 0.1 * ((pressure > 6) & (pressure <= 8)).astype(float)
    anomaly_prob += 0.2 * ((ph_level < 5) | (ph_level > 9)).astype(float)
    anomaly_prob += 0.1 * (((ph_level >= 5) & (ph_level < 6)) | ((ph_level > 8) & (ph_level <= 9))).astype(float)
    poor_mixing = (stirrer_speed < 200) & (concentration > 1.5)
    anomaly_prob += 0.2 * poor_mixing.astype(float)
    anomaly_prob += 0.3 * ((temperature > 100) & (pressure > 7)).astype(float)
    anomaly_prob = np.clip(anomaly_prob, 0, 0.95)
    labels = (np.random.random(n_samples) < anomaly_prob).astype(int)

    return features, labels


def train_model(X: np.ndarray, y: np.ndarray) -> tuple:
    """Train a RandomForest model with standardization."""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
    )
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)

    print("\n=== Model v2 Evaluation (RandomForest) ===")
    print(f"Accuracy: {accuracy:.3f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Normal", "Anomaly"]))

    return model, scaler


def main():
    print("=== Chemical Reactor Model v2 (RandomForest) ===")

    X, y = generate_synthetic_data(n_samples=5000)
    print(f"Generated {len(y)} samples, anomaly rate: {y.mean():.1%}")

    model, scaler = train_model(X, y)

    model_data = {
        "model": model,
        "scaler": scaler,
        "feature_names": FEATURE_NAMES,
        "version": "v2",
    }

    output_path = Path(__file__).parent / "reactor_model_v2.pkl"
    joblib.dump(model_data, output_path)
    print(f"\nModel saved to: {output_path}")


if __name__ == "__main__":
    main()
