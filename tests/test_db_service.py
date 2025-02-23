import unittest
from pathlib import Path
from src.services.db_service import DbService
from models import ConversationHistoryItem, GroupedConversationItem

class TestDbService(unittest.TestCase):
    def setUp(self):
        self.db_service = DbService()
        self.db_service.create_tables()

    def test_add_conversation_history(self):
        item = ConversationHistoryItem(
            id="1",
            user_prompt="Hello",
            response="Hi",
            username="user1",
            conversation_group_id="group1",
            created_at=1234567890
        )
        result = self.db_service.add_converation_history(item)
        self.assertEqual(result.id, item.id)

    def test_add_new_conversation_group(self):
        group = GroupedConversationItem(
            conversation_group_id="group1",
            username="user1",
            conversation_group_name="Test Group",
            created_at=1234567890
        )
        result = self.db_service.add_new_conversation_group(group)
        self.assertEqual(result.conversation_group_id, group.conversation_group_id)

    def test_get_conversation_group(self):
        username = "user1"
        groups = self.db_service.get_conversation_group(username)
        self.assertIsInstance(groups, list)

    def test_get_conversation_history(self):
        conversation_group_id = "group1"
        history = self.db_service.get_conversation_history(conversation_group_id)
        self.assertIsInstance(history, list)

    def test_execute_llm_sql(self):
        query = "SELECT * FROM airlines"
        result = self.db_service.execute_llm_sql(query)
        self.assertIsNotNone(result)

    def test_get_conversation_group_detail(self):
        conversation_group_id = "group1"
        detail = self.db_service.get_conversation_group_detail(conversation_group_id)
        self.assertIsInstance(detail, dict)

    def test_edit_conversation_group(self):
        conversation_group_id = "group1"
        new_name = "New Group Name"
        self.db_service.edit_conversation_group(conversation_group_id, new_name)
        detail = self.db_service.get_conversation_group_detail(conversation_group_id)
        self.assertEqual(detail["conversation_group_name"], new_name)

    def test_delete_conversation_group(self):
        username = "user1"
        self.db_service.delete_conversation_group(username)
        groups = self.db_service.get_conversation_group(username)
        self.assertEqual(len(groups), 0)

    def test_delete_conversation_by_id(self):
        conversation_group_id = "group1"
        self.db_service.delete_conversation_by_id(conversation_group_id)
        detail = self.db_service.get_conversation_group_detail(conversation_group_id)
        self.assertIsNone(detail)

if __name__ == '__main__':
    unittest.main()
