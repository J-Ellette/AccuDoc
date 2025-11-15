"""
Tests for collaborative documentation workspace features.

Tests membership system, CRDT operations, and collaborative sessions.
"""

import unittest
import tempfile
import os
from pathlib import Path

from accudoc.membership import MembershipManager, Role, Permission
from accudoc.crdt import CRDTDocument, OperationType, ConflictResolver
from accudoc.collaboration import CollaborationManager, SessionStatus


class TestMembershipSystem(unittest.TestCase):
    """Test membership and access control."""
    
    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test_membership.db'
        self.manager = MembershipManager(self.db_path)
    
    def tearDown(self):
        """Clean up test database."""
        self.manager.close()
        if self.db_path.exists():
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)
    
    def test_create_user(self):
        """Test creating a new user."""
        user = self.manager.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=Role.EDITOR
        )
        
        self.assertIsNotNone(user.user_id)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, Role.EDITOR)
    
    def test_authenticate_user(self):
        """Test user authentication."""
        # Create user
        self.manager.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Authenticate with correct password
        user = self.manager.authenticate_user('testuser', 'testpass123')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')
        
        # Authenticate with wrong password
        user = self.manager.authenticate_user('testuser', 'wrongpass')
        self.assertIsNone(user)
    
    def test_create_team(self):
        """Test creating a team."""
        # Create owner user
        owner = self.manager.create_user(
            username='owner',
            email='owner@example.com',
            password='pass123'
        )
        
        # Create team
        team = self.manager.create_team(
            name='Test Team',
            owner_id=owner.user_id,
            description='A test team'
        )
        
        self.assertIsNotNone(team.team_id)
        self.assertEqual(team.name, 'Test Team')
        self.assertEqual(team.owner_id, owner.user_id)
    
    def test_grant_project_access(self):
        """Test granting project access."""
        # Create user
        user = self.manager.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123'
        )
        
        # Grant access
        self.manager.grant_project_access(
            project_id='project1',
            granted_by=user.user_id,
            user_id=user.user_id,
            role=Role.EDITOR
        )
        
        # Check permission
        has_permission = self.manager.check_permission(
            user.user_id, 'project1', Permission.WRITE
        )
        self.assertTrue(has_permission)
    
    def test_check_permissions(self):
        """Test permission checking."""
        # Create user
        user = self.manager.create_user(
            username='viewer',
            email='viewer@example.com',
            password='pass123'
        )
        
        # Grant viewer access
        self.manager.grant_project_access(
            project_id='project1',
            granted_by=user.user_id,
            user_id=user.user_id,
            role=Role.VIEWER
        )
        
        # Viewer should have read permission
        self.assertTrue(self.manager.check_permission(
            user.user_id, 'project1', Permission.READ
        ))
        
        # Viewer should NOT have write permission
        self.assertFalse(self.manager.check_permission(
            user.user_id, 'project1', Permission.WRITE
        ))
    
    def test_api_token(self):
        """Test API token creation and verification."""
        # Create user
        user = self.manager.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123'
        )
        
        # Create API token
        token = self.manager.create_api_token(
            user_id=user.user_id,
            name='Test Token',
            expires_in_days=30
        )
        
        self.assertIsNotNone(token)
        
        # Verify token
        verified_user_id = self.manager.verify_api_token(token)
        self.assertEqual(verified_user_id, user.user_id)
        
        # Verify invalid token
        verified_user_id = self.manager.verify_api_token('invalid_token')
        self.assertIsNone(verified_user_id)


class TestCRDT(unittest.TestCase):
    """Test CRDT operations."""
    
    def test_insert_operation(self):
        """Test insert operation."""
        doc = CRDTDocument('doc1', 'Hello World')
        
        op = doc.create_operation(
            user_id='user1',
            op_type=OperationType.INSERT,
            position=5,
            content=' Beautiful'
        )
        
        result = doc.apply_operation(op)
        self.assertTrue(result)
        self.assertEqual(doc.content, 'Hello Beautiful World')
    
    def test_delete_operation(self):
        """Test delete operation."""
        doc = CRDTDocument('doc1', 'Hello World')
        
        op = doc.create_operation(
            user_id='user1',
            op_type=OperationType.DELETE,
            position=5,
            length=6
        )
        
        result = doc.apply_operation(op)
        self.assertTrue(result)
        self.assertEqual(doc.content, 'Hello')
    
    def test_replace_operation(self):
        """Test replace operation."""
        doc = CRDTDocument('doc1', 'Hello World')
        
        op = doc.create_operation(
            user_id='user1',
            op_type=OperationType.REPLACE,
            position=6,
            content='Everyone',
            length=5
        )
        
        result = doc.apply_operation(op)
        self.assertTrue(result)
        self.assertEqual(doc.content, 'Hello Everyone')
    
    def test_merge_documents(self):
        """Test merging CRDT documents."""
        doc1 = CRDTDocument('doc1', 'Hello World')
        doc2 = CRDTDocument('doc1', 'Hello World')
        
        # Apply operation to doc1
        op1 = doc1.create_operation(
            user_id='user1',
            op_type=OperationType.INSERT,
            position=5,
            content=' Beautiful'
        )
        doc1.apply_operation(op1)
        
        # Apply operation to doc2
        op2 = doc2.create_operation(
            user_id='user2',
            op_type=OperationType.INSERT,
            position=11,
            content='!'
        )
        doc2.apply_operation(op2)
        
        # Merge doc2 into doc1
        conflicts = doc1.merge(doc2)
        
        # Should have minimal conflicts with deterministic ordering
        self.assertIsInstance(conflicts, list)
    
    def test_conflict_detection(self):
        """Test conflict detection."""
        doc1 = CRDTDocument('doc1', 'Hello World')
        doc2 = CRDTDocument('doc1', 'Hello World')
        
        # Concurrent edits at same position
        op1 = doc1.create_operation('user1', OperationType.REPLACE, 0, 'Hi', 5)
        doc1.apply_operation(op1)
        
        op2 = doc2.create_operation('user2', OperationType.REPLACE, 0, 'Hey', 5)
        doc2.apply_operation(op2)
        
        conflicts = ConflictResolver.detect_conflicts(doc1, doc2)
        self.assertGreater(len(conflicts), 0)
    
    def test_document_serialization(self):
        """Test document to/from dictionary."""
        doc = CRDTDocument('doc1', 'Hello World')
        
        op = doc.create_operation('user1', OperationType.INSERT, 5, ' Beautiful')
        doc.apply_operation(op)
        
        # Convert to dict
        doc_dict = doc.to_dict()
        
        # Recreate from dict
        doc2 = CRDTDocument.from_dict(doc_dict)
        
        self.assertEqual(doc.content, doc2.content)
        self.assertEqual(doc.version, doc2.version)


class TestCollaboration(unittest.TestCase):
    """Test collaborative session management."""
    
    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test_collaboration.db'
        self.manager = CollaborationManager(self.db_path)
    
    def tearDown(self):
        """Clean up test database."""
        self.manager.close()
        if self.db_path.exists():
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)
    
    def test_create_session(self):
        """Test creating a collaborative session."""
        session = self.manager.create_session(
            project_id='project1',
            document_path='/docs/README.md',
            created_by='user1',
            initial_content='# Project Documentation'
        )
        
        self.assertIsNotNone(session.session_id)
        self.assertEqual(session.project_id, 'project1')
        self.assertEqual(session.status, SessionStatus.ACTIVE)
    
    def test_join_session(self):
        """Test joining a session."""
        # Create session
        session = self.manager.create_session(
            project_id='project1',
            document_path='/docs/README.md',
            created_by='user1'
        )
        
        # Join session
        result = self.manager.join_session(
            session.session_id, 'user2', 'Test User 2'
        )
        
        self.assertTrue(result)
        
        # Check participants
        participants = self.manager.get_session_participants(session.session_id)
        self.assertEqual(len(participants), 1)
        self.assertEqual(participants[0].user_id, 'user2')
    
    def test_apply_operation(self):
        """Test applying an edit operation."""
        # Create session
        session = self.manager.create_session(
            project_id='project1',
            document_path='/docs/README.md',
            created_by='user1',
            initial_content='# Documentation'
        )
        
        # Apply operation
        operation = self.manager.apply_operation(
            session_id=session.session_id,
            user_id='user1',
            op_type=OperationType.INSERT,
            position=2,
            content='Project '
        )
        
        self.assertIsNotNone(operation)
        
        # Check content
        content = self.manager.get_session_content(session.session_id)
        self.assertEqual(content, '# Project Documentation')
    
    def test_add_comment(self):
        """Test adding a comment."""
        # Create session
        session = self.manager.create_session(
            project_id='project1',
            document_path='/docs/README.md',
            created_by='user1'
        )
        
        # Add comment
        comment_id = self.manager.add_comment(
            session_id=session.session_id,
            user_id='user2',
            username='Test User',
            content='This needs clarification',
            position=10
        )
        
        self.assertIsNotNone(comment_id)
        
        # Get comments
        comments = self.manager.get_session_comments(session.session_id)
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0]['content'], 'This needs clarification')
    
    def test_add_suggestion(self):
        """Test adding a change suggestion."""
        # Create session
        session = self.manager.create_session(
            project_id='project1',
            document_path='/docs/README.md',
            created_by='user1'
        )
        
        # Add suggestion
        suggestion_id = self.manager.add_suggestion(
            session_id=session.session_id,
            user_id='user2',
            username='Test User',
            position=0,
            original_text='old text',
            suggested_text='new text',
            reason='Improve clarity'
        )
        
        self.assertIsNotNone(suggestion_id)
        
        # Get suggestions
        suggestions = self.manager.get_session_suggestions(session.session_id)
        self.assertEqual(len(suggestions), 1)
        self.assertEqual(suggestions[0]['suggested_text'], 'new text')
    
    def test_review_suggestion(self):
        """Test reviewing a suggestion."""
        # Create session
        session = self.manager.create_session(
            project_id='project1',
            document_path='/docs/README.md',
            created_by='user1',
            initial_content='old text here'
        )
        
        # Add suggestion
        suggestion_id = self.manager.add_suggestion(
            session_id=session.session_id,
            user_id='user2',
            username='Test User',
            position=0,
            original_text='old text',
            suggested_text='new text',
            reason='Improve clarity'
        )
        
        # Accept suggestion
        result = self.manager.review_suggestion(
            suggestion_id=suggestion_id,
            reviewed_by='user1',
            accepted=True
        )
        
        self.assertTrue(result)
        
        # Check that content was updated
        content = self.manager.get_session_content(session.session_id)
        self.assertIn('new text', content)
    
    def test_close_session(self):
        """Test closing a session."""
        # Create session
        session = self.manager.create_session(
            project_id='project1',
            document_path='/docs/README.md',
            created_by='user1'
        )
        
        # Close session
        result = self.manager.close_session(session.session_id)
        self.assertTrue(result)
        
        # Check status
        session = self.manager.get_session(session.session_id)
        self.assertEqual(session.status, SessionStatus.CLOSED)


def run_tests():
    """Run all tests."""
    print("=" * 60)
    print("Testing Collaborative Documentation Workspace")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMembershipSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestCRDT))
    suite.addTests(loader.loadTestsFromTestCase(TestCollaboration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    sys.exit(0 if run_tests() else 1)
