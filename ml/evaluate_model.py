"""
Model Evaluation and Diagnostic Reporting Module for MediGuide AI.
Evaluates the trained ML pipelines against synthetic benchmark test sets,
generating confusion matrices and per-class precision/recall/F1 diagnostics.
"""

import sys
from pathlib import Path
import pandas as pd
import joblib
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.config import DATA_DIR, ML_MODEL_PATH


def evaluate_models():
    """Load trained models and evaluate on synthetic benchmark."""
    if not Path(ML_MODEL_PATH).exists():
        print(f"Error: Model file {ML_MODEL_PATH} not found. Run train_model.py first.")
        return None

    artifacts = joblib.load(ML_MODEL_PATH)
    triage_model = artifacts["triage_pipeline"]
    specialty_model = artifacts["specialty_pipeline"]

    csv_path = DATA_DIR / "synthetic_demo_data.csv"
    df = pd.read_csv(csv_path)

    X = df["symptoms_text"].astype(str)
    y_triage = df["triage_level"].astype(str)
    y_specialty = df["specialty_category"].astype(str)

    # Predict
    pred_triage = triage_model.predict(X)
    pred_specialty = specialty_model.predict(X)

    # Metrics
    triage_acc = accuracy_score(y_triage, pred_triage)
    triage_f1 = f1_score(y_triage, pred_triage, average="macro")
    triage_cm = confusion_matrix(y_triage, pred_triage, labels=artifacts["triage_classes"])

    print("========================================================")
    print("MEDIGUIDE AI — CARE NAVIGATION ML BENCHMARK REPORT")
    print("========================================================")
    print(f"Total Benchmark Samples: {len(df)}")
    print(f"Overall Triage Urgency Accuracy: {triage_acc * 100:.2f}%")
    print(f"Triage Macro F1-Score: {triage_f1:.4f}")
    print("\nTriage Urgency Classification Report:")
    print(classification_report(y_triage, pred_triage, target_names=artifacts["triage_classes"], zero_division=0))

    print("\nTriage Confusion Matrix:")
    print("Classes:", artifacts["triage_classes"])
    print(triage_cm)

    print("\n--------------------------------------------------------")
    print("CLINICAL SAFETY CAVEAT:")
    print("Pure statistical text models must NEVER be used alone for triage")
    print("in real clinical environments due to risk of false negatives.")
    print("MediGuide AI pairs this model with a deterministic Safety Engine.")
    print("========================================================")

    return {
        "triage_accuracy": triage_acc,
        "triage_f1": triage_f1,
        "triage_classes": artifacts["triage_classes"],
        "confusion_matrix": triage_cm.tolist()
    }


if __name__ == "__main__":
    evaluate_models()
