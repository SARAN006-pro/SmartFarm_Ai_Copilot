"""
Run this script once to initialize the database and train ML models.

Usage (from backend/ folder):
    python -m app.scripts.init_db
"""
from __future__ import annotations

import os
import sys


def ensure_dirs() -> None:
    """Create all runtime directories."""
    data_dir = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), ".."))
    for subdir in ("rag_store", "uploads", "saved", "ml_models"):
        path = os.path.join(data_dir, subdir)
        os.makedirs(path, exist_ok=True)
    print("[init] Directories ready.")


def init_database() -> None:
    """Initialize the SQLite database schema."""
    from app.utils.db import get_db

    conn = get_db()
    print("[init] Database tables created.")
    conn.close()


def train_models() -> dict:
    """Train ML models and return metrics."""
    from app.ml.crop_model import train_crop_model
    from app.ml.yield_model import train_yield_model

    crop_acc = train_crop_model()
    yield_metrics = train_yield_model()
    return {"crop_accuracy": crop_acc, "yield_r2": yield_metrics["r2"], "yield_mae": yield_metrics["mae"]}


def main() -> None:
    print("=" * 50)
    print("SmartFarm AI — Initializing...")
    print("=" * 50)

    ensure_dirs()
    init_database()

    print("\nTraining ML models (this may take a minute)...")
    try:
        metrics = train_models()
        print(f"\nCrop model accuracy : {metrics['crop_accuracy']:.2%}")
        print(f"Yield model R²      : {metrics['yield_r2']:.3f}")
        print(f"Yield model MAE     : {metrics['yield_mae']:.0f} kg/ha")
    except Exception as exc:
        print(f"\n[WARN] Model training failed: {exc}")
        print("Models will train on first prediction request.")

    print("\n" + "=" * 50)
    print("Initialization complete. Run: uvicorn app.main:app --reload")
    print("=" * 50)


if __name__ == "__main__":
    main()
