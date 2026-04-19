"""
Run this once to train and save both ML models.

Usage (from backend/ folder):
    python -m app.ml.train_models
"""

from app.ml.crop_model import train_crop_model
from app.ml.yield_model import train_yield_model


if __name__ == "__main__":
	print("=" * 40)
	crop_acc = train_crop_model()
	print()
	yield_metrics = train_yield_model()
	print()
	print("=" * 40)
	print(f"Crop accuracy : {crop_acc:.2%}")
	print(f"Yield R²      : {yield_metrics['r2']:.3f}")
	print(f"Yield MAE     : {yield_metrics['mae']:.0f} kg/ha")
	print("Both models ready.")