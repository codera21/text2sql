import duckdb as db
from models import ConversationHistoryItem, GroupedConversationItem


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

        # conversation_group
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conversation_group (
                conversation_grouped_id TEXT PRIMARY KEY,
                username TEXT,
                conversation_grouped_name TEXT,
                created_at BIGINT
            )
        """
        )

        # conversation_history
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

    def add_new_conversation_group(self, conversation_group: GroupedConversationItem):
        conn = self.connect()

        conn.execute(
            """
            INSERT INTO conversation_group (conversation_grouped_id , username ,  conversation_grouped_name,  created_at) VALUES (?, ?, ?, ?)
        """,
            (
                conversation_group.conversation_grouped_id,
                conversation_group.username,
                conversation_group.conversation_grouped_name,
                conversation_group.created_at,
            ),
        )

        return True

    def get_conversation_group(self, username: str):
        conn = self.connect()

        rows = conn.execute(
            f"""
                select  conversation_grouped_id, username, conversation_grouped_name, created_at
                from conversation_group 
                where username = '{username}'
                order by created_at desc
            """
        ).fetchall()

        return [
            {
                "conversation_grouped_id": row[0],
                "username": row[1],
                "conversation_grouped_name": row[2],
                "created_at": row[3],
            }
            for row in rows
        ]

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

    def execute_llm_sql(self, query: str):

        df = db.sql(f""" SELECT * from  '{self.airlines}' """)

        return df

    def clear_converation_history(self, username: str):

        conn = self.connect()
        conn.execute(f"DELETE conversation_history where username='{username}'")

    def get_conversation_group_detail(self, conversation_grouped_id: str):
        conn = self.connect()

        row = conn.execute(
            f"""
                select  conversation_grouped_id, username, conversation_grouped_name, created_at
                from conversation_group 
                where conversation_grouped_id = '{conversation_grouped_id}'
                order by created_at desc
            """
        ).fetchone()

        return {
            "conversation_grouped_id": row[0],
            "username": row[1],
            "conversation_grouped_name": row[2],
            "created_at": row[3],
        }
