import os
import pickle

import numpy as np

try:
	from sklearn.ensemble import RandomForestClassifier  # type: ignore
	from sklearn.metrics import accuracy_score  # type: ignore
	from sklearn.model_selection import train_test_split  # type: ignore
	from sklearn.preprocessing import StandardScaler  # type: ignore
	SKLEARN_AVAILABLE = True
except Exception:
	RandomForestClassifier = None
	accuracy_score = None
	train_test_split = None
	StandardScaler = None
	SKLEARN_AVAILABLE = False


DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), "saved"))
if os.environ.get("DATA_DIR"):
	MODEL_DIR = os.path.join(DATA_DIR, "ml_models")
else:
	MODEL_DIR = os.path.join(os.path.dirname(__file__), "saved")
os.makedirs(MODEL_DIR, exist_ok=True)

CROP_MODEL_PATH = os.path.join(MODEL_DIR, "crop_model.pkl")
CROP_SCALER_PATH = os.path.join(MODEL_DIR, "crop_scaler.pkl")

CROP_FEATURES = ["nitrogen", "phosphorus", "potassium", "temperature", "humidity", "ph", "rainfall"]

CROP_PROFILES = {
	"rice": ([80, 40, 40, 25, 82, 6.5, 200], 120),
	"wheat": ([40, 40, 40, 15, 65, 6.5, 80], 100),
	"maize": ([60, 50, 50, 22, 65, 6.0, 100], 100),
	"chickpea": ([40, 70, 80, 18, 20, 7.2, 80], 100),
	"kidneybeans": ([20, 70, 20, 20, 22, 5.7, 110], 100),
	"pigeonpeas": ([20, 70, 20, 27, 50, 5.8, 150], 100),
	"mothbeans": ([21, 48, 20, 28, 50, 6.9, 50], 100),
	"mungbean": ([20, 48, 20, 28, 85, 6.7, 50], 100),
	"blackgram": ([40, 67, 19, 30, 65, 7.0, 70], 100),
	"lentil": ([19, 70, 20, 18, 64, 6.8, 45], 100),
	"pomegranate": ([18, 18, 40, 22, 90, 6.0, 110], 100),
	"banana": ([100, 75, 50, 27, 80, 6.0, 105], 100),
	"mango": ([20, 20, 30, 31, 50, 5.7, 95], 100),
	"grapes": ([23, 130, 200, 24, 81, 6.0, 70], 100),
	"watermelon": ([99, 17, 50, 25, 85, 6.5, 50], 100),
	"muskmelon": ([100, 17, 50, 28, 92, 6.5, 25], 100),
	"apple": ([21, 135, 200, 21, 92, 5.9, 115], 100),
	"orange": ([20, 10, 10, 22, 92, 7.0, 110], 100),
	"papaya": ([50, 59, 50, 33, 92, 6.7, 145], 100),
	"coconut": ([22, 16, 30, 27, 95, 5.9, 175], 100),
	"cotton": ([118, 46, 20, 24, 80, 6.4, 80], 100),
	"jute": ([78, 46, 44, 25, 80, 6.5, 175], 100),
	"coffee": ([101, 28, 30, 25, 58, 6.7, 160], 100),
}


def _generate_training_data():
	samples_per_crop = 100
	X, y = [], []
	rng = np.random.default_rng(42)

	for crop, (profile, _) in CROP_PROFILES.items():
		noise_scale = [10, 8, 8, 2, 5, 0.3, 20]
		for _ in range(samples_per_crop):
			noisy = [max(0, profile[index] + rng.normal(0, noise_scale[index])) for index in range(len(profile))]
			X.append(noisy)
			y.append(crop)

	return np.array(X, dtype=float), np.array(y)


def train_crop_model():
	if not SKLEARN_AVAILABLE:
		print("scikit-learn is unavailable; skipping crop model training and using heuristic fallback.")
		return 0.0
	print("Training crop recommendation model...")
	X, y = _generate_training_data()

	X_train, X_test, y_train, y_test = train_test_split(
		X, y, test_size=0.2, random_state=42, stratify=y
	)

	scaler = StandardScaler()
	X_train_scaled = scaler.fit_transform(X_train)
	X_test_scaled = scaler.transform(X_test)

	model = RandomForestClassifier(
		n_estimators=100,
		max_depth=15,
		random_state=42,
		n_jobs=-1,
	)
	model.fit(X_train_scaled, y_train)

	accuracy = accuracy_score(y_test, model.predict(X_test_scaled))
	print(f"Crop model accuracy: {accuracy:.2%}")

	with open(CROP_MODEL_PATH, "wb") as file_handle:
		pickle.dump(model, file_handle)
	with open(CROP_SCALER_PATH, "wb") as file_handle:
		pickle.dump(scaler, file_handle)

	print("Crop model saved.")
	return accuracy


def load_crop_model():
	if not SKLEARN_AVAILABLE or not os.path.exists(CROP_MODEL_PATH):
		raise FileNotFoundError("Crop model not found. Run train_models.py first.")
	with open(CROP_MODEL_PATH, "rb") as file_handle:
		model = pickle.load(file_handle)
	with open(CROP_SCALER_PATH, "rb") as file_handle:
		scaler = pickle.load(file_handle)
	return model, scaler


def _generate_reason(crop: str, features: dict) -> str:
	n = features["nitrogen"]
	temp = features["temperature"]
	rain = features["rainfall"]
	ph = features["ph"]

	parts = []
	if n > 60:
		parts.append("high nitrogen availability")
	elif n < 25:
		parts.append("low nitrogen requirement")

	if temp > 28:
		parts.append("warm temperature")
	elif temp < 18:
		parts.append("cool temperature preference")

	if rain > 150:
		parts.append("high rainfall suitability")
	elif rain < 60:
		parts.append("drought tolerance")

	if 6.0 <= ph <= 7.0:
		parts.append("neutral soil pH")
	elif ph < 6.0:
		parts.append("acidic soil tolerance")
	else:
		parts.append("alkaline soil tolerance")

	base = f"{crop.capitalize()} is recommended based on "
	return base + (", ".join(parts) if parts else "the overall soil and climate profile") + "."


def predict_crop(features: dict) -> dict:
	if SKLEARN_AVAILABLE and os.path.exists(CROP_MODEL_PATH):
		model, scaler = load_crop_model()
		X = np.array([[features[name] for name in CROP_FEATURES]], dtype=float)
		X_scaled = scaler.transform(X)
		crop = model.predict(X_scaled)[0]
		proba = model.predict_proba(X_scaled)[0]
		classes = model.classes_
		top_idx = int(np.argmax(proba))
		confidence = float(proba[top_idx]) * 100
		top3_idx = np.argsort(proba)[::-1][:3]
		alternatives = [
			{"crop": classes[index], "confidence": round(float(proba[index]) * 100, 1)}
			for index in top3_idx
		]
	else:
		feature_vector = np.array([features[name] for name in CROP_FEATURES], dtype=float)
		best_crop = None
		best_distance = float("inf")
		candidate_distances = []
		for crop_name, (profile, _) in CROP_PROFILES.items():
			distance = float(np.linalg.norm(feature_vector - np.array(profile, dtype=float)))
			candidate_distances.append((crop_name, distance))
			if distance < best_distance:
				best_crop = crop_name
				best_distance = distance
		candidate_distances.sort(key=lambda item: item[1])
		crop = best_crop or "rice"
		confidence = max(30.0, 100.0 - best_distance)
		alternatives = [
			{"crop": crop_name, "confidence": round(max(5.0, 100.0 - distance), 1)}
			for crop_name, distance in candidate_distances[:3]
		]

	reason = _generate_reason(crop, features)
	return {
		"recommended_crop": crop,
		"confidence": round(confidence, 1),
		"reason": reason,
		"alternatives": alternatives,
	}