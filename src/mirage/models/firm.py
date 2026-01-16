"""Core firm and period models."""

from pydantic import BaseModel, Field


class Period(BaseModel):
    """Represents a simulation period."""

    number: int = Field(..., description="Period number (can be negative for history)")
    
    @property
    def is_historical(self) -> bool:
        return self.number < 0
    
    @property
    def is_current(self) -> bool:
        return self.number == 0
    
    @property
    def is_future(self) -> bool:
        return self.number > 0


class Firm(BaseModel):
    """Represents a firm in the simulation."""

    id: int = Field(..., ge=1, le=6, description="Firm ID (1-6)")
    name: str = Field(default="", description="Firm name")
    
    @property
    def display_name(self) -> str:
        return self.name if self.name else f"Firm {self.id}"
