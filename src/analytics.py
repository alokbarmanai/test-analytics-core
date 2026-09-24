from pydantic import BaseModel, Field, ValidationError


class InvalidPayloadError(Exception):
    """Raised when the incoming analytics data structure is corrupted or invalid."""

    pass


# Define the data contract structure
class AnalyticsPayloadSchema(BaseModel):
    metric_name: str = Field(..., min_length=1)
    values: list[float | int]


def verify_and_process_payload(payload_dict: dict) -> dict:
    ## Use Pydantic to do the heavy lifting of parsing and validation
    try:
        payload = AnalyticsPayloadSchema(**payload_dict)
    except ValidationError as e:
        # Catch Pydantic's error and wrap it in your custom project error
        raise InvalidPayloadError(f"Schema validation failed: {e}") from e

    # 3. Processing logical boundaries
    if len(payload.values) == 0:
        return {"metric": payload.metric_name, "status": "EMPTY", "average": 0.0}

    avg = sum(payload.values) / len(payload.values)
    return {
        "metric": payload.metric_name,
        "status": "PROCESSED",
        "average": round(avg, 2),
    }
