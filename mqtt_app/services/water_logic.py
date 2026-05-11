def calculate(
    total_height: float,
    total_volume: float,
    distance: float,
    battery_voltage: float = 0,
):
    """
    Central water management calculation logic.
    This is the SINGLE source of truth for all derived values.
    """

    # Water level calculation
    water_height = max(total_height - distance, 0)

    # Percentage filled
    percentage = (water_height / total_height) * 100 if total_height else 0

    # Filled volume
    filled_water_in_volume = (percentage / 100) * total_volume

    return {
        "PERCENTAGE": round(percentage, 2),
        "FILLED_WATER_IN_VOLUME": round(filled_water_in_volume, 2),
        "BATTERY_VOLTAGE": round(battery_voltage, 2),
        "DISTANCE": round(distance, 2),
        "TOTAL_HEIGHT": total_height,
        "TOTAL_VOLUME": total_volume,
    }

    # return {
    #     "percentage": round(percentage, 2),
    #     "filled_water_in_volume": round(filled_water_in_volume, 2),
    #     "motor_status": motor_status,
    #     "motor_mode": motor_mode,
    #     "battery_voltage": round(battery_voltage, 2),
    #     "distance": round(distance, 2),
    #     "total_height": total_height,
    #     "total_volume": total_volume,
    # }
