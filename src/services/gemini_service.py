from os import getenv
from google import genai
from google.genai import types


class GeminiService:

    def __init__(self):
        api_key = getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model = getenv("GEMINI_LLM_MODEL", "gemini-2.0-flash")

    def generate_sql_query_content(self, user_prompt: str):

        system_instruct = """ You are a text-to-SQL translator. The domain is flight, and there is data for flight delays. Convert the user's query into SQL.
            Schema:
            - airlines (IATA_CODE,AIRLINE)
            - airpots (IATA_CODE,AIRPORT,CITY,STATE,COUNTRY,LATITUDE,LONGITUDE)
            - flights (YEAR,MONTH,DAY,DAY_OF_WEEK,AIRLINE,FLIGHT_NUMBER,TAIL_NUMBER,ORIGIN_AIRPORT,DESTINATION_AIRPORT,SCHEDULED_DEPARTURE,DEPARTURE_TIME,DEPARTURE_DELAY,TAXI_OUT,WHEELS_OFF,SCHEDULED_TIME,ELAPSED_TIME,AIR_TIME,DISTANCE,WHEELS_ON,TAXI_IN,SCHEDULED_ARRIVAL,ARRIVAL_TIME,ARRIVAL_DELAY,DIVERTED,CANCELLED,CANCELLATION_REASON,AIR_SYSTEM_DELAY,SECURITY_DELAY,AIRLINE_DELAY,LATE_AIRCRAFT_DELAY,WEATHER_DELAY)
            
            Rules:
            1. Use ONLY column names in the schema.
            2. Use JOINs for queries across tables.
            3. Return only SQL, no explanations.
            4. Always use backticks for table/column names (e.g., `IATA_CODE` , `AIRPORT`). 

            
        """

        response = self.client.models.generate_content(
            model=self.model,
            config=types.GenerateContentConfig(system_instruction=system_instruct),
            contents=[user_prompt],
        )

        return response.text
