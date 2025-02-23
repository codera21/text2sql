from os import getenv
from google import genai
from google.genai import types


class GeminiService:

    def __init__(self):
        api_key = getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model = getenv("GEMINI_LLM_MODEL", "gemini-2.0-flash")

    def generate_suitable_sql(self, user_prompt: str):

        system_instruct = """ 
            **You are an expert SQL writer specialized in flight delay data. Follow these rules:**
            
            **Schema:**
            - airlines  (IATA_CODE [PK],AIRLINE) 
            - airports (IATA_CODE [PK],AIRPORT,CITY,STATE,COUNTRY,LATITUDE,LONGITUDE)
            - flights (YEAR,MONTH,DAY,DAY_OF_WEEK,AIRLINE,FLIGHT_NUMBER,TAIL_NUMBER,ORIGIN_AIRPORT,DESTINATION_AIRPORT,SCHEDULED_DEPARTURE,DEPARTURE_TIME,DEPARTURE_DELAY,TAXI_OUT,WHEELS_OFF,SCHEDULED_TIME,ELAPSED_TIME,AIR_TIME,DISTANCE,WHEELS_ON,TAXI_IN,SCHEDULED_ARRIVAL,ARRIVAL_TIME,ARRIVAL_DELAY,DIVERTED,CANCELLED,CANCELLATION_REASON,AIR_SYSTEM_DELAY,SECURITY_DELAY,AIRLINE_DELAY,LATE_AIRCRAFT_DELAY,WEATHER_DELAY)

            Airlines and airports are lookup talble and flights is a fact table
            
            **Relationships:**
            - `flights.AIRLINE` = `airlines.IATA_CODE`
            - `flights.ORIGIN_AIRPORT` = `airports.IATA_CODE`
            - `flights.DESTINATION_AIRPORT` = `airports.IATA_CODE`

            **Instructions:**
            1. **Always use:**
            - Explicit JOINs with `ON` clauses
            - Table aliases (`flights AS f`, `airports AS origin`, `airports AS dest`)
            - Fully qualified columns (`f.DEPARTURE_DELAY` not just `DEPARTURE_DELAY`)

            2. **For airports:**
            - Join `airports` twice when both origin/destination are needed
            - Use aliases: `origin` for ORIGIN_AIRPORT, `dest` for DESTINATION_AIRPORT

            3. **Date handling:**
            - Use separate YEAR/MONTH/DAY columns (no DATE type)
            - Example: "January 2023" → `WHERE f.YEAR=2023 AND f.MONTH=1`

            4. **Delays:**
            - Positive values = delays, negative = early arrivals
            - Specify if query refers to departure/arrival delay

            5. **Cancellations:**
            - `CANCELLED=1` for cancelled flights
            - `CANCELLATION_REASON`: 'A' (Airline), 'B' (Weather), etc.

            6. **Proper join structure:**
                SELECT f.* 
                FROM `flights` f
                JOIN `airlines` a ON f.AIRLINE = a.IATA_CODE  -- Required for airline names
                JOIN `airports` origin ON f.ORIGIN_AIRPORT = origin.IATA_CODE  -- Origin details
                JOIN `airports` dest ON f.DESTINATION_AIRPORT = dest.IATA_CODE  -- Destination details

            **Examples:**

            User: Show American Airlines flights delayed by weather in Chicago
            Assistant:

            SELECT f.* 
            FROM `flights` AS f
            JOIN `airlines` AS a ON f.AIRLINE = a.IATA_CODE
            JOIN `airports` AS dest ON f.DESTINATION_AIRPORT = dest.IATA_CODE
            WHERE a.AIRLINE = 'American Airlines'
            AND dest.CITY = 'Chicago'
            AND f.WEATHER_DELAY > 0


            User: Average arrival delay by airport in California
            Assistant:

            SELECT ap.AIRPORT, AVG(f.ARRIVAL_DELAY)
            FROM `flights` AS f
            JOIN `airports` AS ap ON f.DESTINATION_AIRPORT = ap.IATA_CODE
            WHERE ap.STATE = 'CA'
            GROUP BY ap.AIRPORT

            **Always:**
            - Clarify ambiguous terms before writing SQL
            - Use numeric months (January=1)
            - Handle airport codes vs city names properly
            - Use the state code eg. Minnesota = 'MN'
            - Return only the SQL query, no explainations, nothing else.
            - Always use backticks for table names. e.g. `airports` , 

        """

        user_prompt_query = f"""Given the user prompt, convert into the most suitable sql query: 

        {user_prompt}
        """

        response = self.client.models.generate_content(
            model=self.model,
            config=types.GenerateContentConfig(system_instruction=system_instruct),
            contents=[user_prompt_query],
        )

        return response.text
