from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.ml_service import predict_yield_service, recommend_crop


router = APIRouter()


class CropRequest(BaseModel):
	nitrogen: float = Field(..., ge=0, le=200, description="kg/ha")
	phosphorus: float = Field(..., ge=0, le=200, description="kg/ha")
	potassium: float = Field(..., ge=0, le=200, description="kg/ha")
	temperature: float = Field(..., ge=-10, le=50, description="°C")
	humidity: float = Field(..., ge=0, le=100, description="%")
	ph: float = Field(..., ge=0, le=14, description="soil pH")
	rainfall: float = Field(..., ge=0, le=500, description="mm/month")

	model_config = {
		"json_schema_extra": {
			"example": {
				"nitrogen": 80,
				"phosphorus": 40,
				"potassium": 40,
				"temperature": 25,
				"humidity": 82,
				"ph": 6.5,
				"rainfall": 200,
			}
		}
	}


@router.post("/predict/crop")
def crop_recommendation(request: CropRequest):
	try:
		result = recommend_crop(request.model_dump())
		return result
	except FileNotFoundError:
		raise HTTPException(status_code=503, detail="ML model not ready. Run: python -m app.ml.train_models")
	except Exception as error:
		raise HTTPException(status_code=500, detail=str(error)) from error


class YieldRequest(BaseModel):
	crop_name: str = Field(..., description="Crop name, e.g. 'rice'")
	area_hectares: float = Field(..., ge=0.1, le=10000, description="Farm area in hectares")
	fertilizer_kg: float = Field(..., ge=0, le=1000, description="Fertilizer used (kg/ha)")
	pesticide_kg: float = Field(..., ge=0, le=100, description="Pesticide used (kg/ha)")
	annual_rainfall_mm: float = Field(..., ge=0, le=5000, description="Annual rainfall in mm")

	model_config = {
		"json_schema_extra": {
			"example": {
				"crop_name": "rice",
				"area_hectares": 5.0,
				"fertilizer_kg": 200,
				"pesticide_kg": 10,
				"annual_rainfall_mm": 1800,
			}
		}
	}


@router.post("/predict/yield")
def yield_prediction(request: YieldRequest):
	try:
		result = predict_yield_service(request.model_dump())
		return result
	except FileNotFoundError:
		raise HTTPException(status_code=503, detail="ML model not ready. Run: python -m app.ml.train_models")
	except Exception as error:
		raise HTTPException(status_code=500, detail=str(error)) from error


@router.get("/predict/crops/list")
def list_supported_crops():
	from app.ml.yield_model import CROP_BASE_YIELDS

	return {"crops": sorted(CROP_BASE_YIELDS.keys())}