import duckdb as db
from models import ConversationHistoryItem, GroupedConversationItem, ProjectItem


class DbService:
    def __init__(self):
        self.create_tables()

    def connect(self):
        return db.connect("new.db")

    def create_tables(self):
        # Create a sample table
        conn = self.connect()

        # project
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS project (
                project_id TEXT PRIMARY KEY,
                username TEXT,
                project_name TEXT,
                created_at BIGINT
            )
        """
        )

        # conversation_group
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conversation_group (
                conversation_group_id TEXT PRIMARY KEY,
                username TEXT,
                project_id TEXT,
                conversation_group_name TEXT,
                created_at BIGINT
            )
        """
        )

        # legacy databases may miss project_id column; add when absent
        try:
            conn.execute(
                """
                ALTER TABLE conversation_group ADD COLUMN project_id TEXT
            """
            )
        except Exception:
            pass

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

        self._backfill_projects()

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
            INSERT INTO conversation_group (
                conversation_group_id,
                username,
                project_id,
                conversation_group_name,
                created_at
            ) VALUES (?, ?, ?, ?, ?)
        """,
            (
                conversation_group.conversation_group_id,
                conversation_group.username,
                conversation_group.project_id,
                conversation_group.conversation_group_name,
                conversation_group.created_at,
            ),
        )

        conn.close()
        return conversation_group

    def get_conversation_group(self, username: str, project_id: str):
        conn = self.connect()

        rows = conn.execute(
            
            """
                select  conversation_group_id, username, project_id, conversation_group_name, created_at
                from conversation_group 
                where username = ? and project_id = ?
                order by created_at desc
            """,
            (username, project_id),
        ).fetchall()

        conn.close()
        return [
            {
                "conversation_group_id": row[0],
                "username": row[1],
                "project_id": row[2],
                "conversation_group_name": row[3],
                "created_at": row[4],
            }            for row in rows
        ]

    def get_conversation_history(self, conversation_group_id: str):

        conn = self.connect()

        rows = conn.execute(
            """
                select  id, username, user_prompt, response, created_at 
                from conversation_history 
                where conversation_group_id = ?
                order by created_at asc
            """,
            (conversation_group_id,),
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

        prepared_query = self._prepare_query(query)

        df = db.sql(prepared_query)

        return df

    def _prepare_query(self, query):
        # remove unnecessary whitespace
        query = query.strip()
        # remove ```sql tick if any
        query = query.replace("```sql", "")
        query = query.replace("```", "")

        return query

    def get_conversation_group_detail(self, conversation_group_id: str):
        conn = self.connect()

        row = conn.execute(
            """
                select  cg.conversation_group_id,
                        cg.username,
                        cg.project_id,
                        cg.conversation_group_name,
                        cg.created_at,
                        p.project_name
                from conversation_group cg
                left join project p on p.project_id = cg.project_id
                where cg.conversation_group_id = ?
            """,
            (conversation_group_id,),
        ).fetchone()

        conn.close()
        if not row:
            raise ValueError("Conversation group not found")
        return {
            "conversation_group_id": row[0],
            "username": row[1],
            "project_id": row[2],
            "conversation_group_name": row[3],
            "created_at": row[4],
            "project_name": row[5],
        }

    def edit_conversation_group(
        self, conversation_group_id: str, new_conversation_group_name: str
    ):

        conn = self.connect()

        conn.execute(
            """
                update  conversation_group 
                set   conversation_group_name= ?
                where conversation_group_id = ?
            """,
            (new_conversation_group_name, conversation_group_id),
        )
        conn.close()

    def delete_conversation_group(self, username: str, project_id: str):

        conn = self.connect()
        group_rows = conn.execute(
            """
                select conversation_group_id
                from conversation_group
                where username = ? and project_id = ?
            """,
            (username, project_id),
        ).fetchall()

        for (group_id,) in group_rows:
            conn.execute(
                """
                    delete from conversation_history
                    where conversation_group_id = ?
                """,
                (group_id,),
            )

        conn.execute(
            """
                delete from  conversation_group 
                where username = ? and project_id = ?
            """,
            (username, project_id),
        )
        conn.close()

    def delete_conversation_by_id(self, conversation_group_id: str):

        conn = self.connect()

        conn.execute(
            """
                delete from  conversation_history 
                where conversation_group_id = ?
            """,
            (conversation_group_id,),
        )

        conn.execute(
            """
                delete from  conversation_group 
                where conversation_group_id = ?
            """,
            (conversation_group_id,),
        )
        conn.close()

    def add_new_project(self, project_item: ProjectItem, conn=None):
        owns_conn = False
        if conn is None:
            conn = self.connect()
            owns_conn = True

        conn.execute(
            """
            INSERT INTO project (project_id, username, project_name, created_at)
            VALUES (?, ?, ?, ?)
        """,
            (
                project_item.project_id,
                project_item.username,
                project_item.project_name,
                project_item.created_at,
            ),
        )

        if owns_conn:
            conn.close()

        return project_item

    def get_projects(self, username: str):
        conn = self.connect()

        rows = conn.execute(
            """
                select project_id, username, project_name, created_at
                from project
                where username = ?
                order by created_at desc
            """,
            (username,),
        ).fetchall()

        conn.close()
        return [
            {
                "project_id": row[0],
                "username": row[1],
                "project_name": row[2],
                "created_at": row[3],
            }
            for row in rows
        ]

    def get_project_detail(self, project_id: str):
        conn = self.connect()
        row = conn.execute(
            """
                select project_id, username, project_name, created_at
                from project
                where project_id = ?
            """,
            (project_id,),
        ).fetchone()
        conn.close()
        if not row:
            raise ValueError("Project not found")
        return {
            "project_id": row[0],
            "username": row[1],
            "project_name": row[2],
            "created_at": row[3],
        }

    def delete_project(self, project_id: str):
        conn = self.connect()

        group_rows = conn.execute(
            """
                select conversation_group_id
                from conversation_group
                where project_id = ?
            """,
            (project_id,),
        ).fetchall()

        for (group_id,) in group_rows:
            conn.execute(
                """
                    delete from conversation_history
                    where conversation_group_id = ?
                """,
                (group_id,),
            )

        conn.execute(
            """
                delete from conversation_group
                where project_id = ?
            """,
            (project_id,),
        )

        conn.execute(
            """
                delete from project
                where project_id = ?
            """,
            (project_id,),
        )
        conn.close()

    def update_project_name(self, project_id: str, project_name: str):
        conn = self.connect()
        conn.execute(
            """
                update project
                set project_name = ?
                where project_id = ?
            """,
            (project_name, project_id),
        )
        conn.close()

    def get_or_create_default_project(self, username: str) -> ProjectItem:
        conn = self.connect()
        row = conn.execute(
            """
                select project_id, username, project_name, created_at
                from project
                where username = ?
                order by created_at asc
                limit 1
            """,
            (username,),
        ).fetchone()

        if row:
            conn.close()
            return ProjectItem(
                project_id=row[0],
                username=row[1],
                project_name=row[2],
                created_at=row[3],
            )

        project_item = ProjectItem(username=username, project_name="Default Project")
        self.add_new_project(project_item, conn=conn)
        conn.close()
        return project_item

    def _backfill_projects(self):
        conn = self.connect()
        usernames = conn.execute(
            """
                select distinct username
                from conversation_group
                where project_id is null or project_id = ''
            """
        ).fetchall()
        conn.close()

        for (username,) in usernames:
            if not username:
                continue
            project = self.get_or_create_default_project(username)
            update_conn = self.connect()
            update_conn.execute(
                """
                    update conversation_group
                    set project_id = ?
                    where username = ? and (project_id is null or project_id = '')
                """,
                (project.project_id, username),
            )
            update_conn.close()
