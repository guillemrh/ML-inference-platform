"""
Training script for Chemical Reactor Anomaly Detection model.

This script generates synthetic data simulating a chemical reactor process
and trains a binary classifier to predict anomalies (off-spec product or safety events).

Usage:
    python train_reactor_model.py

Output:
    reactor_model_v1.pkl - Trained scikit-learn model
"""

import numpy as np
from pathlib import Path
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import StandardScaler


# Feature ranges for chemical reactor process
FEATURE_RANGES = {
    "temperature": (60, 120),        # °C
    "pressure": (1, 10),             # bar
    "flow_rate": (5, 50),            # L/min
    "reactant_concentration": (0.5, 2.0),  # mol/L
    "ph_level": (4, 10),             # pH
    "stirrer_speed": (100, 500),     # RPM
}

FEATURE_NAMES = list(FEATURE_RANGES.keys())


def generate_synthetic_data(n_samples: int = 5000, random_seed: int = 42) -> tuple:
    """
    Generate synthetic chemical reactor data with realistic anomaly patterns.

    Anomalies are more likely when:
    - Temperature > 105°C (overheating risk)
    - Pressure > 8 bar (overpressure risk)
    - pH < 5 or pH > 9 (chemical imbalance)
    - Low stirrer speed with high concentration (poor mixing)

    Args:
        n_samples: Number of samples to generate
        random_seed: Random seed for reproducibility

    Returns:
        Tuple of (features array, labels array)
    """
    np.random.seed(random_seed)

    # Generate random features within ranges
    features = np.zeros((n_samples, len(FEATURE_NAMES)))

    for i, (name, (low, high)) in enumerate(FEATURE_RANGES.items()):
        features[:, i] = np.random.uniform(low, high, n_samples)

    # Extract individual features for readability
    temperature = features[:, 0]
    pressure = features[:, 1]
    flow_rate = features[:, 2]
    concentration = features[:, 3]
    ph_level = features[:, 4]
    stirrer_speed = features[:, 5]

    # Calculate anomaly probability based on process conditions
    # Base probability is low (5%)
    anomaly_prob = np.full(n_samples, 0.05)

    # High temperature increases risk
    anomaly_prob += 0.3 * (temperature > 105).astype(float)
    anomaly_prob += 0.15 * ((temperature > 95) & (temperature <= 105)).astype(float)

    # High pressure increases risk
    anomaly_prob += 0.25 * (pressure > 8).astype(float)
    anomaly_prob += 0.1 * ((pressure > 6) & (pressure <= 8)).astype(float)

    # pH outside normal range (6-8) increases risk
    anomaly_prob += 0.2 * ((ph_level < 5) | (ph_level > 9)).astype(float)
    anomaly_prob += 0.1 * (((ph_level >= 5) & (ph_level < 6)) | ((ph_level > 8) & (ph_level <= 9))).astype(float)

    # Poor mixing: low stirrer speed with high concentration
    poor_mixing = (stirrer_speed < 200) & (concentration > 1.5)
    anomaly_prob += 0.2 * poor_mixing.astype(float)

    # Interaction: high temp AND high pressure is very dangerous
    anomaly_prob += 0.3 * ((temperature > 100) & (pressure > 7)).astype(float)

    # Cap probability at 0.95
    anomaly_prob = np.clip(anomaly_prob, 0, 0.95)

    # Generate labels based on probability
    labels = (np.random.random(n_samples) < anomaly_prob).astype(int)

    return features, labels


def train_model(X: np.ndarray, y: np.ndarray) -> tuple:
    """
    Train a logistic regression model with standardization.

    Args:
        X: Feature matrix
        y: Labels

    Returns:
        Tuple of (trained model, scaler, metrics dict)
    """
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Standardize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train model
    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X_train_scaled, y_train)

    # Evaluate
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)

    print("\n=== Model Evaluation ===")
    print(f"Accuracy: {accuracy:.3f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Normal", "Anomaly"]))

    metrics = {
        "accuracy": accuracy,
        "test_size": len(y_test),
        "train_size": len(y_train),
        "anomaly_rate_train": y_train.mean(),
        "anomaly_rate_test": y_test.mean(),
    }

    return model, scaler, metrics


def save_model(model, scaler, output_path: Path, version: str = "v1") -> None:
    """
    Save model and scaler together for inference.

    Args:
        model: Trained model
        scaler: Fitted scaler
        output_path: Directory to save model
        version: Version string for filename
    """
    model_data = {
        "model": model,
        "scaler": scaler,
        "feature_names": FEATURE_NAMES,
        "version": version,
    }

    filename = output_path / f"reactor_model_{version}.pkl"
    joblib.dump(model_data, filename)
    print(f"\nModel saved to: {filename}")


def main():
    print("=== Chemical Reactor Anomaly Detection Model ===")
    print(f"Features: {FEATURE_NAMES}")

    # Generate data
    print("\nGenerating synthetic data...")
    X, y = generate_synthetic_data(n_samples=5000)
    print(f"Generated {len(y)} samples")
    print(f"Anomaly rate: {y.mean():.1%}")

    # Train model
    print("\nTraining model...")
    model, scaler, metrics = train_model(X, y)

    # Save model
    output_path = Path(__file__).parent
    save_model(model, scaler, output_path, version="v1")

    print("\n=== Done ===")


if __name__ == "__main__":
    main()
