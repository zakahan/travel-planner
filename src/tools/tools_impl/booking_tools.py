
def booking_flight(flight_number: str, date: str) -> str:
    """
    Book a flight with the given flight number and date.

    Args:
        flight_number (str): The flight number (e.g., "CA123").
        date (str): The flight date in the format "YYYY-MM-DD".

    Returns:
        str: A message indicating that the flight booking was successful.
    """
    return f"booking {flight_number} - {date} successful."


def booking_hotel(hotel_name: str, date: str) -> str:
    """
    Book a hotel room at the given hotel on the specified date.

    Args:
        hotel_name (str): The name of the hotel (e.g., "Hilton").
        date (str): The check-in date in the format "YYYY-MM-DD".

    Returns:
        str: A message indicating that the hotel booking was successful.
    """
    return f"booking {hotel_name} - {date} successful."


def booking_attraction(attractions: list[dict]) -> str:
    """
    Book attractions based on the provided list of attraction information.

    Args:
        attractions (list[dict]): A list of dictionaries containing attraction information.

    Returns:
        str: A message indicating that the attraction bookings were successful.
    """
    return "booking attractions successful."