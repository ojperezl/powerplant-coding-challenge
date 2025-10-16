# app/models.py

from pydantic import BaseModel, Field
from typing import List, Optional  # <--- Asegúrate de que 'Optional' está importado

# Modelo para los precios de los combustibles
class FuelPrices(BaseModel):
    gas_euro_per_mwh: float = Field(alias='gas(euro/MWh)')
    kerosene_euro_per_mwh: float = Field(alias='kerosine(euro/MWh)')
    co2_euro_per_ton: int = Field(alias='co2(euro/ton)')
    wind_percentage: int = Field(alias='wind(%)')

# Modelo para cada central eléctrica
class PowerPlant(BaseModel):
    name: str
    type: str
    efficiency: float
    pmin: int
    pmax: int
    # Esta es la línea corregida, usando 'Optional[float]'
    marginal_cost: Optional[float] = None

# Modelo principal que representa todo el payload de entrada
class Payload(BaseModel):
    load: int
    fuels: FuelPrices
    powerplants: List[PowerPlant]

