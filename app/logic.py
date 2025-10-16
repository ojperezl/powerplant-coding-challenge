
# app/logic.py

from typing import Dict, List, Tuple
from .models import Payload, PowerPlant, FuelPrices

# --- Funciones auxiliares ---

def build_merit_order(powerplants: List[PowerPlant], fuels: FuelPrices) -> List[PowerPlant]:
    """Calcula el coste de generación por central y devuelve la lista ordenada (merit order)."""
    for plant in powerplants:
        if plant.type == "windturbine":
            plant.marginal_cost = 0.0
        elif plant.type == "gasfired":
            coste_co2 = 0.3 * fuels.co2_euro_per_ton
            plant.marginal_cost = (fuels.gas_euro_per_mwh / plant.efficiency) + coste_co2
        elif plant.type == "turbojet":
            plant.marginal_cost = fuels.kerosene_euro_per_mwh / plant.efficiency
        else:
            plant.marginal_cost = float("inf")
    return sorted(powerplants, key=lambda p: (p.marginal_cost if p.marginal_cost is not None else float("inf")))

def despachar_renovables(payload: Payload) -> Tuple[Dict[str, float], float]:
    """Calcula la producción de las eólicas y la demanda restante."""
    plan_produccion = {}
    energia_eolica_total = 0.0
    demanda_restante = float(payload.load)

    for planta in payload.powerplants:
        if planta.type == "windturbine":
            produccion = planta.pmax * (payload.fuels.wind_percentage / 100.0)
            produccion_redondeada = round(produccion, 1)
            plan_produccion[planta.name] = produccion_redondeada
            energia_eolica_total += produccion_redondeada
        else:
            plan_produccion[planta.name] = 0.0
    
    demanda_restante -= energia_eolica_total
    return plan_produccion, demanda_restante

def despachar_termicas(plantas_termicas: List[PowerPlant], demanda_restante: float, plan_actual: Dict[str, float]) -> Dict[str, float]:
    """Asigna la producción a las centrales térmicas según el orden de mérito."""
    for planta in plantas_termicas:
        if demanda_restante <= 0:
            break

        potencia_disponible = planta.pmax
        potencia_a_asignar = min(demanda_restante, potencia_disponible)

        if 0 < potencia_a_asignar < planta.pmin:
            continue

        potencia_asignada = round(potencia_a_asignar, 1)
        plan_actual[planta.name] = potencia_asignada
        demanda_restante -= potencia_asignada
    
    return plan_actual

def ajustar_carga_final(plan: Dict[str, float], plantas_ordenadas: List[PowerPlant], carga_total: float) -> Dict[str, float]:
    """Ajusta la producción para que la suma total sea exactamente igual a la carga."""
    produccion_actual = sum(plan.values())
    diferencia = round(carga_total - produccion_actual, 1)

    if diferencia == 0:
        return plan

    for planta in reversed(plantas_ordenadas):
        if planta.type != "windturbine" and plan.get(planta.name, 0) > 0:
            produccion_ajustada = plan[planta.name] + diferencia
            
            # Asegurarse de que el ajuste no viole pmin si la planta sigue encendida
            if (planta.pmin <= produccion_ajustada <= planta.pmax) or (produccion_ajustada == 0):
                plan[planta.name] = round(produccion_ajustada, 1)
                # Verificamos si el ajuste fue exitoso
                if round(sum(plan.values()), 1) == carga_total:
                    return plan
    
    return plan

# --- Función Principal Orquestadora ---

def calcular_plan_produccion(payload: Payload) -> List[Dict[str, any]]:
    """Orquesta el proceso completo para generar el plan de producción."""
    merit_order = build_merit_order(payload.powerplants, payload.fuels)
    
    plan_produccion, demanda_restante = despachar_renovables(payload)
    
    plantas_termicas_ordenadas = [p for p in merit_order if p.type in ["gasfired", "turbojet"]]
    plan_produccion = despachar_termicas(plantas_termicas_ordenadas, demanda_restante, plan_produccion)
    
    plan_final = ajustar_carga_final(plan_produccion, merit_order, float(payload.load))

    # Comprobación final
    suma_total = sum(plan_final.values())
    if abs(suma_total - payload.load) > 0.1: # Tolerancia por redondeo
         # En un caso real, aquí se lanzaría una excepción o se intentaría un ajuste más sofisticado
        print(f"ADVERTENCIA: No se pudo satisfacer la carga exactamente. Carga: {payload.load}, Producido: {suma_total}")

    respuesta = [{"name": planta.name, "p": plan_final.get(planta.name, 0.0)} for planta in payload.powerplants]
        
    return respuesta
