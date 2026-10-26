"""
Machine Learning Model Training Pipeline for MediGuide AI.
Trains lightweight NLP classification pipelines for:
1. Care Navigation Urgency (Triage Level)
2. Medical Specialty Category

Uses TF-IDF feature extraction with Logistic Regression and stratified train-test splits.
Saves model artifacts via Joblib.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, f1_score

# Ensure root is in path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.config import DATA_DIR, ML_DIR, ML_MODEL_PATH


def train_models():
    """Train care navigation and specialty classification models."""
    csv_path = DATA_DIR / "synthetic_demo_data.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset not found at {csv_path}. Run generate_data.py first.")

    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} samples from {csv_path}")

    # Features and targets
    X = df["symptoms_text"].astype(str)
    y_triage = df["triage_level"].astype(str)
    y_specialty = df["specialty_category"].astype(str)

    print("\nTriage Level Class Distribution:")
    print(y_triage.value_counts())

    # Stratified Train/Test Split (80% train, 20% test)
    X_train_t, X_test_t, y_train_t, y_test_t = train_test_split(
        X, y_triage, test_size=0.20, random_state=42, stratify=y_triage
    )

    # Train Triage Pipeline
    print("\n--- Training Triage Urgency Model ---")
    triage_pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=1200,
            sublinear_tf=True,
            stop_words="english"
        )),
        ("clf", LogisticRegression(
            C=2.0,
            max_iter=1000,
            random_state=42
        ))
    ])

    triage_pipeline.fit(X_train_t, y_train_t)
    y_pred_t = triage_pipeline.predict(X_test_t)

    triage_acc = accuracy_score(y_test_t, y_pred_t)
    triage_f1 = f1_score(y_test_t, y_pred_t, average="macro")
    print(f"Triage Test Accuracy: {triage_acc * 100:.2f}% | Macro F1: {triage_f1:.4f}")
    print("\nTriage Classification Report:")
    print(classification_report(y_test_t, y_pred_t, zero_division=0))

    # Train Specialty Pipeline
    print("\n--- Training Medical Specialty Model ---")
    # For specialty, some classes have few samples so we train on the full text set with Stratified K-Fold or train/test split
    # If rare classes exist, split without stratify or min_samples check
    try:
        X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(
            X, y_specialty, test_size=0.20, random_state=42, stratify=y_specialty
        )
    except Exception:
        X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(
            X, y_specialty, test_size=0.20, random_state=42
        )

    specialty_pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=1500,
            sublinear_tf=True,
            stop_words="english"
        )),
        ("clf", LogisticRegression(
            C=2.0,
            max_iter=1000,
            random_state=42
        ))
    ])

    specialty_pipeline.fit(X_train_s, y_train_s)
    y_pred_s = specialty_pipeline.predict(X_test_s)
    spec_acc = accuracy_score(y_test_s, y_pred_s)
    print(f"Specialty Test Accuracy: {spec_acc * 100:.2f}%")

    # Save artifacts bundle
    artifacts = {
        "triage_pipeline": triage_pipeline,
        "specialty_pipeline": specialty_pipeline,
        "triage_classes": list(triage_pipeline.classes_),
        "specialty_classes": list(specialty_pipeline.classes_),
        "triage_accuracy": triage_acc,
        "triage_macro_f1": triage_f1,
        "specialty_accuracy": spec_acc
    }

    ML_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifacts, ML_MODEL_PATH)
    print(f"\nModel pipeline successfully saved to {ML_MODEL_PATH}")


if __name__ == "__main__":
    train_models()
