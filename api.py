from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pickle
import numpy as np
from typing import Optional, List
import uvicorn

app = FastAPI(
    title="Dubai Real Estate Price Prediction API",
    description="API for predicting Dubai residential property prices using Random Forest model",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and encoders at startup
print("Loading model and encoders...")
with open('model/random_forest_model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('model/label_encoder_area.pkl', 'rb') as f:
    le_area = pickle.load(f)

with open('model/label_encoder_subtype.pkl', 'rb') as f:
    le_subtype = pickle.load(f)

with open('model/label_encoder_regtype.pkl', 'rb') as f:
    le_regtype = pickle.load(f)

with open('model/metadata.pkl', 'rb') as f:
    metadata = pickle.load(f)

# Load validation rules
import json
try:
    with open('model/validation_rules.json', 'r') as f:
        validation_rules = json.load(f)
    print("Validation rules loaded successfully!")
except Exception as e:
    print(f"Warning: Could not load validation rules: {e}")
    validation_rules = None

print("Model and encoders loaded successfully!")


# Request/Response models
class PropertyInput(BaseModel):
    procedure_area: float = Field(..., description="Property size in square meters", example=100.0, gt=0, lt=1000)
    bedrooms: int = Field(..., description="Number of bedrooms (0 for Studio)", example=2, ge=0, le=10)
    has_parking: int = Field(..., description="Has parking (0 or 1)", example=1, ge=0, le=1)
    has_project: int = Field(..., description="Part of a named project (0 or 1)", example=1, ge=0, le=1)
    area_name_en: str = Field(..., description="Location area name", example="DUBAI MARINA")
    property_sub_type_en: str = Field(..., description="Property sub-type", example="Flat")
    reg_type_en: str = Field(..., description="Registration type", example="Off-Plan Properties")

    class Config:
        json_schema_extra = {
            "example": {
                "procedure_area": 100.0,
                "bedrooms": 2,
                "has_parking": 1,
                "has_project": 1,
                "area_name_en": "DUBAI MARINA",
                "property_sub_type_en": "Flat",
                "reg_type_en": "Off-Plan Properties"
            }
        }


class PredictionResponse(BaseModel):
    predicted_price: float = Field(..., description="Predicted price in AED (mid-point)")
    predicted_price_formatted: str = Field(..., description="Formatted price string")
    price_range: dict = Field(..., description="Price range (±10%): lower_bound and upper_bound")
    price_range_formatted: str = Field(..., description="Formatted price range string")
    price_per_sqm: float = Field(..., description="Price per square meter")
    confidence_level: str = Field(..., description="Confidence level of prediction")
    input_features: dict = Field(..., description="Input features used for prediction")
    validation_warnings: List[str] = Field(default=[], description="Input validation warnings")


class BatchPropertyInput(BaseModel):
    properties: List[PropertyInput]


class BatchPredictionResponse(BaseModel):
    predictions: List[PredictionResponse]
    total_properties: int


class ModelInfoResponse(BaseModel):
    model_config = {"protected_namespaces": ()}  # Allow model_* fields

    model_type: str
    training_samples: int
    r2_score: float
    mae: float
    available_areas: List[str]
    available_property_subtypes: List[str]
    available_registration_types: List[str]
    price_range: dict


# Helper function
def safe_encode(encoder, value, encoder_name):
    """Safely encode categorical values"""
    if value in encoder.classes_:
        return encoder.transform([value])[0]
    else:
        # Use most common class if unknown
        print(f"Warning: '{value}' not found in {encoder_name}, using default")
        return encoder.transform([encoder.classes_[0]])[0]


def validate_property_inputs(area_size, bedrooms, property_subtype):
    """Validate property inputs and return warnings"""
    warnings = []

    if validation_rules is None:
        return warnings

    # Check size for given bedrooms
    bedroom_key = 'Studio' if bedrooms == 0 else f'{bedrooms}_bedroom'
    if bedroom_key in validation_rules.get('size_ranges', {}):
        size_info = validation_rules['size_ranges'][bedroom_key]
        min_size = size_info['min_typical']
        max_size = size_info['max_typical']

        if area_size < min_size * 0.7:
            warnings.append(f"Size seems too small for {bedroom_key.replace('_', ' ')}. Typical range: {min_size:.0f}-{max_size:.0f} sqm")
        elif area_size > max_size * 1.5:
            warnings.append(f"Size seems too large for {bedroom_key.replace('_', ' ')}. Typical range: {min_size:.0f}-{max_size:.0f} sqm")

    # Check property subtype specifics
    if property_subtype in validation_rules.get('property_subtype_specifics', {}):
        subtype_info = validation_rules['property_subtype_specifics'][property_subtype]

        if bedrooms not in subtype_info.get('typical_bedrooms', []):
            typical = subtype_info['typical_bedrooms']
            if typical:
                warnings.append(f"{property_subtype} typically has {min(typical)}-{max(typical)} bedrooms")

        size_range = subtype_info.get('size_range', [0, 1000])
        if area_size < size_range[0] or area_size > size_range[1]:
            warnings.append(f"{property_subtype} typically ranges {size_range[0]}-{size_range[1]} sqm")

    return warnings


def get_confidence_level(area_size, bedrooms, area_name, subtype):
    """Estimate confidence level based on input characteristics"""
    confidence_score = 100

    # Check if inputs are common
    if area_name not in le_area.classes_[:50]:  # Not in top 50 areas
        confidence_score -= 15

    if subtype not in ['Flat', 'Villa', 'Hotel Apartment']:
        confidence_score -= 10

    # Check if size is within expected range
    if validation_rules:
        bedroom_key = 'Studio' if bedrooms == 0 else f'{bedrooms}_bedroom'
        if bedroom_key in validation_rules.get('size_ranges', {}):
            size_info = validation_rules['size_ranges'][bedroom_key]
            if area_size < size_info['min_typical'] * 0.7 or area_size > size_info['max_typical'] * 1.5:
                confidence_score -= 20

    if bedrooms > 5:
        confidence_score -= 10

    if confidence_score >= 85:
        return "High"
    elif confidence_score >= 70:
        return "Medium"
    else:
        return "Low"


# API Endpoints
@app.get("/")
def read_root():
    return {
        "message": "Dubai Real Estate Price Prediction API",
        "version": "1.0.1",
        "endpoints": {
            "/predict": "POST - Predict price for a single property",
            "/predict/batch": "POST - Predict prices for multiple properties",
            "/model/info": "GET - Get model information",
            "/validation/rules": "GET - Get validation rules and typical size ranges",
            "/areas": "GET - Get list of available areas",
            "/property-types": "GET - Get list of available property sub-types",
            "/registration-types": "GET - Get list of available registration types"
        }
    }


@app.post("/predict", response_model=PredictionResponse)
def predict_price(property_input: PropertyInput):
    """Predict price for a single property"""
    try:
        # Encode categorical features
        area_encoded = safe_encode(le_area, property_input.area_name_en, "area")
        subtype_encoded = safe_encode(le_subtype, property_input.property_sub_type_en, "subtype")
        regtype_encoded = safe_encode(le_regtype, property_input.reg_type_en, "registration type")

        # Create feature array
        features = np.array([[
            property_input.procedure_area,
            property_input.bedrooms,
            property_input.has_parking,
            property_input.has_project,
            area_encoded,
            subtype_encoded,
            regtype_encoded
        ]])

        # Validate inputs
        warnings = validate_property_inputs(
            property_input.procedure_area,
            property_input.bedrooms,
            property_input.property_sub_type_en
        )

        # Make prediction
        prediction = model.predict(features)[0]

        # Calculate price range (±10%)
        lower_bound = prediction * 0.90
        upper_bound = prediction * 1.10

        # Calculate derived metrics
        price_per_sqm = prediction / property_input.procedure_area

        # Get confidence level
        confidence = get_confidence_level(
            property_input.procedure_area,
            property_input.bedrooms,
            property_input.area_name_en,
            property_input.property_sub_type_en
        )

        # Helper function to format price
        def format_price_millions(price):
            if price >= 1_000_000:
                millions = price / 1_000_000
                return f"{millions:.2f}M" if millions < 10 else f"{millions:.1f}M"
            elif price >= 1_000:
                return f"{price/1_000:.0f}K"
            else:
                return f"{price:.0f}"

        return PredictionResponse(
            predicted_price=round(prediction, 2),
            predicted_price_formatted=f"{prediction:,.0f} AED",
            price_range={
                "lower_bound": round(lower_bound, 2),
                "upper_bound": round(upper_bound, 2)
            },
            price_range_formatted=f"{format_price_millions(lower_bound)} - {format_price_millions(upper_bound)} AED",
            price_per_sqm=round(price_per_sqm, 2),
            confidence_level=confidence,
            input_features=property_input.dict(),
            validation_warnings=warnings
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")


@app.post("/predict/batch", response_model=BatchPredictionResponse)
def predict_batch(batch_input: BatchPropertyInput):
    """Predict prices for multiple properties"""
    try:
        predictions = []
        for prop in batch_input.properties:
            pred = predict_price(prop)
            predictions.append(pred)

        return BatchPredictionResponse(
            predictions=predictions,
            total_properties=len(predictions)
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Batch prediction error: {str(e)}")


@app.get("/model/info", response_model=ModelInfoResponse)
def get_model_info():
    """Get model information and statistics"""
    return ModelInfoResponse(
        model_type=metadata['model_type'],
        training_samples=metadata['training_samples'],
        r2_score=round(metadata['r2_score'], 4),
        mae=round(metadata['mae'], 2),
        available_areas=sorted(metadata['categorical_mappings']['areas'])[:20],  # Top 20
        available_property_subtypes=sorted(metadata['categorical_mappings']['property_subtypes']),
        available_registration_types=sorted(metadata['categorical_mappings']['registration_types']),
        price_range={
            "lower_bound": round(metadata['price_bounds']['lower'], 2),
            "upper_bound": round(metadata['price_bounds']['upper'], 2)
        }
    )


@app.get("/areas")
def get_areas():
    """Get list of all available areas"""
    return {
        "total_areas": len(le_area.classes_),
        "areas": sorted(le_area.classes_.tolist())
    }

'''
@app.get("/property-types")
def get_property_types():
    """Get list of all available property sub-types"""
    return {
        "total_types": len(le_subtype.classes_),
        "property_sub_types": sorted(le_subtype.classes_.tolist())
    }


@app.get("/registration-types")
def get_registration_types():
    """Get list of all available registration types"""
    return {
        "total_types": len(le_regtype.classes_),
        "registration_types": sorted(le_regtype.classes_.tolist())
    }


@app.get("/validation/rules")
def get_validation_rules():
    """Get validation rules and typical size ranges"""
    if validation_rules is None:
        raise HTTPException(status_code=404, detail="Validation rules not available")

    return {
        "size_ranges_by_bedroom": validation_rules.get('size_ranges', {}),
        "property_type_rules": validation_rules.get('property_type_rules', {}),
        "property_subtype_specifics": validation_rules.get('property_subtype_specifics', {}),
        "description": "Validation rules based on analysis of 1.5M Dubai property transactions (2000-2025)"
    }
'''

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "encoders_loaded": all([le_area is not None, le_subtype is not None, le_regtype is not None]),
        "validation_rules_loaded": validation_rules is not None
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
