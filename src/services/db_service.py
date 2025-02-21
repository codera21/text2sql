import duckdb as db
from models import ConversationHistoryItem


class DbService:
    def __init__(self):
        #  dataset source path
        base_file_path = "/Users/atulnepal/Documents/a21/text2sql"

        self.airlines = f"{base_file_path}/flight_delay_dataset/airlines.csv"
        self.airports = f"{base_file_path}/flight_delay_dataset/airports.csv"
        self.flights = f"{base_file_path}/flight_delay_dataset/flights.csv"

        self.create_tables()

    def connect(self):
        return db.connect("text2sql.db")

    def create_tables(self):
        # Create a sample table
        conn = self.connect()
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conversation_history (
                id TEXT PRIMARY KEY,
                user_prompt TEXT,
                response TEXT,
                username TEXT,
                created_at BIGINT
            )
        """
        )

    def add_converation_history(
        self, conversation_history_item: ConversationHistoryItem
    ):
        conn = self.connect()

        conn.execute(
            """
            INSERT INTO conversation_history (id , username ,  user_prompt, response , created_at) VALUES (?, ?, ?, ?, ?)
        """,
            (
                conversation_history_item.id,
                conversation_history_item.username,
                conversation_history_item.user_prompt,
                conversation_history_item.response,
                conversation_history_item.created_at,
            ),
        )

        return True

    def get_convesation_history(self, username: str):

        conn = self.connect()

        rows = conn.execute(
            f"""
                select  id, username, user_prompt, response, created_at 
                from conversation_history 
                where username = '{username}'
                order by created_at asc
            """
        ).fetchall()

        return [
            {
                "id": row[0],
                "username": row[1],
                "user_prompt": row[2],
                "response": row[3],
                "created_at": row[4],
            }
            for row in rows
        ]

    def execute_llm_query(self):
        pass
