from pydantic import BaseModel


class WeatherConditions(BaseModel):
    temperature_celsius: int
    temperature_fahrenheit: int
    icon: str
    conditions: str
    city: str | None = None
