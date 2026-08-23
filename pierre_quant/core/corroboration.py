"""
Pierre Quant Multi-Node Corroboration Boundary Engine (Agent 05)
================================================================
Validates price feeds across primary and secondary oracle streams with 0.5% tolerance threshold.
"""

def verify_price_corroboration(primary_price: float, secondary_price: float) -> bool:
    """Validates that primary and secondary oracle streams agree within a 0.5% tolerance threshold."""
    if primary_price <= 0.0 or secondary_price <= 0.0:
        return False
    delta = abs(primary_price - secondary_price) / primary_price
    return delta <= 0.005  # Maximum 0.5% discrepancy allowed
