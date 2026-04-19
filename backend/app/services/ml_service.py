from app.ml.crop_model import predict_crop
from app.ml.yield_model import predict_yield
from app.utils.db import get_db


def _log_prediction():
	"""Record a prediction event for dashboard stats."""
	conn = get_db()
	conn.execute("INSERT INTO app_stats (event_type) VALUES (?)", ("prediction",))
	conn.commit()
	conn.close()


def recommend_crop(features: dict) -> dict:
	result = predict_crop(features)
	_log_prediction()
	return result


def predict_yield_service(features: dict) -> dict:
	result = predict_yield(features)
	_log_prediction()
	return result