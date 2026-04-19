import os
import pickle

import numpy as np

try:
	from sklearn.ensemble import GradientBoostingRegressor  # type: ignore
	from sklearn.metrics import mean_absolute_error, r2_score  # type: ignore
	from sklearn.model_selection import train_test_split  # type: ignore
	from sklearn.preprocessing import LabelEncoder, StandardScaler  # type: ignore
	SKLEARN_AVAILABLE = True
except Exception:
	GradientBoostingRegressor = None
	mean_absolute_error = None
	r2_score = None
	train_test_split = None
	LabelEncoder = None
	StandardScaler = None
	SKLEARN_AVAILABLE = False


DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), "saved"))
if os.environ.get("DATA_DIR"):
	MODEL_DIR = os.path.join(DATA_DIR, "ml_models")
else:
	MODEL_DIR = os.path.join(os.path.dirname(__file__), "saved")
os.makedirs(MODEL_DIR, exist_ok=True)

YIELD_MODEL_PATH = os.path.join(MODEL_DIR, "yield_model.pkl")
YIELD_SCALER_PATH = os.path.join(MODEL_DIR, "yield_scaler.pkl")
YIELD_ENCODER_PATH = os.path.join(MODEL_DIR, "yield_encoder.pkl")

YIELD_FEATURES = ["area_hectares", "fertilizer_kg", "pesticide_kg", "annual_rainfall_mm", "crop_encoded"]

CROP_BASE_YIELDS = {
	"rice": 4500, "wheat": 3200, "maize": 5500, "chickpea": 1200,
	"kidneybeans": 1500, "pigeonpeas": 1300, "mothbeans": 800,
	"mungbean": 900, "blackgram": 850, "lentil": 950,
	"pomegranate": 12000, "banana": 25000, "mango": 8000,
	"grapes": 15000, "watermelon": 22000, "muskmelon": 18000,
	"apple": 10000, "orange": 11000, "papaya": 30000,
	"coconut": 9000, "cotton": 1800, "jute": 2200, "coffee": 1500,
}


def _generate_yield_data():
	rng = np.random.default_rng(42)
	crops = list(CROP_BASE_YIELDS.keys())
	if SKLEARN_AVAILABLE:
		encoder = LabelEncoder()
		encoder.fit(crops)
	else:
		class _Encoder:
			classes_ = np.array(crops)

			def transform(self, values):
				return np.array([crops.index(value) for value in values], dtype=int)

		encoder = _Encoder()

	rows, targets = [], []

	for crop in crops:
		base = CROP_BASE_YIELDS[crop]
		for _ in range(150):
			area = rng.uniform(0.5, 50)
			fertilizer = rng.uniform(50, 500)
			pesticide = rng.uniform(0, 50)
			rainfall = rng.uniform(40, 300)
			crop_enc = encoder.transform([crop])[0]

			fert_effect = min(1.4, 0.8 + (fertilizer / 500) * 0.6)
			rain_effect = 1.0 - abs(rainfall - 150) / 500
			pest_effect = 1.0 + (pesticide / 100) * 0.2
			noise = rng.normal(1.0, 0.08)

			yield_val = base * fert_effect * rain_effect * pest_effect * noise
			yield_val = max(100, yield_val)

			rows.append([area, fertilizer, pesticide, rainfall, crop_enc])
			targets.append(yield_val)

	return np.array(rows, dtype=float), np.array(targets, dtype=float), encoder


def train_yield_model():
	if not SKLEARN_AVAILABLE:
		print("scikit-learn is unavailable; skipping yield model training and using heuristic fallback.")
		return {"r2": 0.0, "mae": 0.0}
	print("Training yield prediction model...")
	X, y, encoder = _generate_yield_data()

	X_train, X_test, y_train, y_test = train_test_split(
		X, y, test_size=0.2, random_state=42
	)

	scaler = StandardScaler()
	X_train_scaled = scaler.fit_transform(X_train)
	X_test_scaled = scaler.transform(X_test)

	model = GradientBoostingRegressor(
		n_estimators=100,
		learning_rate=0.1,
		max_depth=5,
		random_state=42,
	)
	model.fit(X_train_scaled, y_train)

	preds = model.predict(X_test_scaled)
	r2 = r2_score(y_test, preds)
	mae = mean_absolute_error(y_test, preds)
	print(f"Yield model  R²: {r2:.3f}  MAE: {mae:.0f} kg/ha")

	with open(YIELD_MODEL_PATH, "wb") as file_handle:
		pickle.dump(model, file_handle)
	with open(YIELD_SCALER_PATH, "wb") as file_handle:
		pickle.dump(scaler, file_handle)
	with open(YIELD_ENCODER_PATH, "wb") as file_handle:
		pickle.dump(encoder, file_handle)

	print("Yield model saved.")
	return {"r2": r2, "mae": mae}


def load_yield_model():
	if not SKLEARN_AVAILABLE or not os.path.exists(YIELD_MODEL_PATH):
		raise FileNotFoundError("Yield model not found. Run train_models.py first.")
	with open(YIELD_MODEL_PATH, "rb") as file_handle:
		model = pickle.load(file_handle)
	with open(YIELD_SCALER_PATH, "rb") as file_handle:
		scaler = pickle.load(file_handle)
	with open(YIELD_ENCODER_PATH, "rb") as file_handle:
		encoder = pickle.load(file_handle)
	return model, scaler, encoder


def predict_yield(features: dict) -> dict:
	crop_name = features["crop_name"].lower()
	known_crops = list(CROP_BASE_YIELDS.keys())
	if crop_name not in known_crops:
		closest = known_crops[0]
		note = f"Crop '{crop_name}' not in training set; using '{closest}' as proxy."
	else:
		closest = crop_name
		note = None

	if SKLEARN_AVAILABLE and os.path.exists(YIELD_MODEL_PATH):
		model, scaler, encoder = load_yield_model()
		crop_enc = encoder.transform([closest])[0]
		X = np.array([[features["area_hectares"], features["fertilizer_kg"], features["pesticide_kg"], features["annual_rainfall_mm"], crop_enc]], dtype=float)
		X_scaled = scaler.transform(X)
		predicted_yield = float(model.predict(X_scaled)[0])
	else:
		base = CROP_BASE_YIELDS[closest]
		fert_effect = min(1.4, 0.8 + (features["fertilizer_kg"] / 500) * 0.6)
		rain_effect = 1.0 - abs(features["annual_rainfall_mm"] - 150) / 500
		pest_effect = 1.0 + (features["pesticide_kg"] / 100) * 0.2
		predicted_yield = float(max(100, base * fert_effect * rain_effect * pest_effect))

	total_production = predicted_yield * features["area_hectares"]

	result = {
		"predicted_yield_kg_per_ha": round(predicted_yield, 1),
		"total_production_kg": round(total_production, 1),
		"crop": closest,
		"area_hectares": features["area_hectares"],
	}
	if note:
		result["note"] = note
	return result