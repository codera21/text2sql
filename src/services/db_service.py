import duckdb as db


class DbService:
    def __init__(self):
        #  dataset source path
        base_file_path = "/Users/atulnepal/Documents/a21/text2sql"

        self.airlines = f"{base_file_path}/flight_delay_dataset/airlines.csv"

        self.airports = f"{base_file_path}/flight_delay_dataset/airports.csv"

        self.flights = f"{base_file_path}/flight_delay_dataset/flights.csv"
