from pathlib import Path
import duckdb as db
from models import ConversationHistoryItem, GroupedConversationItem


class DbService:
    def __init__(self):
        #  dataset source path
        dataset_path = Path("./dataset").resolve()
        
        self.airlines = f"{dataset_path}/airlines.csv"
        self.airports = f"{dataset_path}/airports.csv"
        self.flights = f"{dataset_path}/flights.csv"

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
                conversation_group_id TEXT PRIMARY KEY,
                username TEXT,
                conversation_group_name TEXT,
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
                conversation_group_id TEXT,
                created_at BIGINT
            )
        """
        )

        conn.close()

    def add_converation_history(
        self, conversation_history_item: ConversationHistoryItem
    ):
        conn = self.connect()

        conn.execute(
            """
            INSERT INTO conversation_history (id , username ,  user_prompt, response , created_at , conversation_group_id) VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                conversation_history_item.id,
                conversation_history_item.username,
                conversation_history_item.user_prompt,
                conversation_history_item.response,
                conversation_history_item.created_at,
                conversation_history_item.conversation_group_id,
            ),
        )

        conn.close()
        return conversation_history_item

    def add_new_conversation_group(self, conversation_group: GroupedConversationItem):
        conn = self.connect()

        conn.execute(
            """
            INSERT INTO conversation_group (conversation_group_id , username ,  conversation_group_name,  created_at) VALUES (?, ?, ?, ?)
        """,
            (
                conversation_group.conversation_group_id,
                conversation_group.username,
                conversation_group.conversation_group_name,
                conversation_group.created_at,
            ),
        )

        return conversation_group

    def get_conversation_group(self, username: str):
        conn = self.connect()

        rows = conn.execute(
            f"""
                select  conversation_group_id, username, conversation_group_name, created_at
                from conversation_group 
                where username = '{username}'
                order by created_at desc
            """
        ).fetchall()

        conn.close()
        return [
            {
                "conversation_group_id": row[0],
                "username": row[1],
                "conversation_group_name": row[2],
                "created_at": row[3],
            }
            for row in rows
        ]

    def get_conversation_history(self, conversation_group_id: str):

        conn = self.connect()

        rows = conn.execute(
            f"""
                select  id, username, user_prompt, response, created_at 
                from conversation_history 
                where conversation_group_id = '{conversation_group_id}'
                order by created_at asc
            """
        ).fetchall()

        conn.close()
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

    def get_conversation_group_detail(self, conversation_group_id: str):
        conn = self.connect()

        row = conn.execute(
            f"""
                select  conversation_group_id, username, conversation_group_name, created_at
                from conversation_group 
                where conversation_group_id = '{conversation_group_id}'
                order by created_at desc
            """
        ).fetchone()

        conn.close()
        return {
            "conversation_group_id": row[0],
            "username": row[1],
            "conversation_group_name": row[2],
            "created_at": row[3],
        }

    def edit_conversation_group(
        self, conversation_group_id: str, new_conversation_group_name: str
    ):

        conn = self.connect()

        conn.execute(
            f"""
                update  conversation_group 
                set   conversation_group_name= '{new_conversation_group_name}'
                where conversation_group_id = '{conversation_group_id}'
            """
        )
        conn.close()

    def delete_conversation_group(self, username: str):

        conn = self.connect()

        conn.execute(
            f"""
                delete from  conversation_group 
                where username = '{username}'
            """
        )
        conn.close()

    def delete_conversation_by_id(self, conversation_group_id: str):

        conn = self.connect()

        conn.execute(
            f"""
                delete from  conversation_group 
                where conversation_group_id = '{conversation_group_id}'
            """
        )
        conn.close()
