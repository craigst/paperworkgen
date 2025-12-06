"""
Pydantic schemas for API request and response validation.
"""

from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, Field, root_validator, validator


class CarModel(BaseModel):
    """Model for individual car data in loadsheet."""
    reg: str = Field(..., description="Vehicle registration number")
    make_model: str = Field(..., description="Car make and model")
    offloaded: str = Field(default="N", description="Whether car is offloaded (Y/N)")
    docs: str = Field(default="N", description="Whether car has documents (Y/N)")
    spare_keys: str = Field(default="Y", description="Whether car has spare keys (Y/N)")
    car_notes: str = Field(default="", description="Additional notes for the car")

    @validator('offloaded', 'docs', 'spare_keys')
    def validate_yn_fields(cls, v):
        """Validate Y/N fields."""
        if v.upper() not in ['Y', 'N']:
            raise ValueError("Must be 'Y' or 'N'")
        return v.upper()


class LoadsheetRequest(BaseModel):
    """Request model for generating a loadsheet."""
    load_date: str = Field(..., description="Load date in YYYY-MM-DD format")
    load_number: str = Field(..., description="Load number identifier")
    collection_point: str = Field(..., description="Collection location name")
    delivery_point: str = Field(..., description="Delivery location name")
    fleet_reg: str = Field(..., description="Fleet registration number")
    load_notes: str = Field(default="", description="General notes for the load")
    sig1: str = Field(default="random", description="Signature 1 path or 'random'")
    sig2: str = Field(default="random", description="Signature 2 path or 'random'")
    cars: List[CarModel] = Field(..., description="List of cars on the load")

    @validator('load_date')
    def validate_date(cls, v):
        """Validate date format."""
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v


class LoadModel(BaseModel):
    """Model for individual load data in timesheet."""
    customer: str = Field(..., description="Customer name")
    car_count: Union[int, str] = Field(..., description="Number of cars")
    collection: str = Field(..., description="Collection location")
    delivery: str = Field(..., description="Delivery location")
    note: str = Field(default="", description="Additional note for the load")


class DayModel(BaseModel):
    """Model for individual day data in timesheet."""
    day: str = Field(..., description="Day of the week")
    start_time: Optional[str] = Field(None, description="Start time (HH:MM or SICK/HOLIDAY)")
    finish_time: Optional[str] = Field(None, description="Finish time (HH:MM or SICK/HOLIDAY)")
    total_hours: Optional[str] = Field(None, description="Total hours worked")
    loads: List[Union[LoadModel, dict]] = Field(default_factory=list, description="Loads for the day")

    @validator('day')
    def validate_day(cls, v):
        """Validate day of week."""
        valid_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        if v.lower() not in valid_days:
            raise ValueError("Day must be a valid weekday name")
        return v.title()


class TimesheetRequest(BaseModel):
    """Request model for generating a timesheet."""
    week_ending: Optional[str] = Field(
        None, description="Week ending date in YYYY-MM-DD format (Sunday preferred)"
    )
    week_end_date: Optional[str] = Field(
        None, description="Alias for week ending date (same format)", alias="week_end_date"
    )
    driver: str = Field(..., description="Driver name")
    fleet_reg: List[str] = Field(..., description="Fleet registration number(s)")
    start_mileage: str = Field(default="", description="Starting mileage")
    end_mileage: str = Field(default="", description="Ending mileage")
    weekly_total_hours: Optional[str] = Field(
        None, description="Optional weekly total hours (overrides auto-sum)"
    )
    sig1: str = Field(default="random", description="Signature 1 path or 'random'")
    sig2: str = Field(default="random", description="Signature 2 path or 'random'")
    days: List[DayModel] = Field(..., description="Daily time and load data")

    @root_validator(pre=True)
    def ensure_week_alias(cls, values):
        """Accept either week_ending or week_end_date."""
        if not values.get("week_ending") and values.get("week_end_date"):
            values["week_ending"] = values["week_end_date"]
        return values

    @root_validator
    def require_week_ending(cls, values):
        if not values.get("week_ending"):
            raise ValueError("week_ending (or week_end_date) is required for timesheets")
        return values

    @validator('week_ending')
    def validate_date(cls, v):
        """Validate date format."""
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v

    @validator('fleet_reg', pre=True)
    def normalize_fleet_reg(cls, v):
        if isinstance(v, str):
            return [v]
        if isinstance(v, list):
            return v
        raise ValueError("fleet_reg must be a string or list of strings")

    @validator('fleet_reg')
    def uppercase_fleet_reg(cls, v):
        return [item.upper() for item in v if str(item).strip()]


class GenerateResponse(BaseModel):
    """Response model for paperwork generation."""
    excel_path: str = Field(..., description="Path to generated Excel file")
    pdf_path: Optional[str] = Field(None, description="Path to generated PDF file")
    message: str = Field(..., description="Generation status message")
    week_folder: str = Field(..., description="Week folder name where files were saved")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Current timestamp")
    version: str = Field(..., description="API version")


class SignatureListResponse(BaseModel):
    """Response model for signature list."""
    sig1_images: List[str] = Field(..., description="Available signature 1 images")
    sig2_images: List[str] = Field(..., description="Available signature 2 images")
