"""
Demo script for collaborative documentation workspace features.

Demonstrates membership, CRDT operations, and collaborative sessions.
"""

import tempfile
from pathlib import Path

from accudoc.membership import MembershipManager, Role, Permission
from accudoc.crdt import CRDTDocument, OperationType
from accudoc.collaboration import CollaborationManager


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def demo_membership():
    """Demonstrate membership and access control."""
    print_section("Membership & Access Control Demo")
    
    # Create temporary database
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / 'demo_membership.db'
    manager = MembershipManager(db_path)
    
    # Create users
    print("\n1. Creating users...")
    owner = manager.create_user('alice', 'alice@example.com', 'pass123', Role.OWNER)
    editor = manager.create_user('bob', 'bob@example.com', 'pass456', Role.EDITOR)
    viewer = manager.create_user('charlie', 'charlie@example.com', 'pass789', Role.VIEWER)
    
    print(f"✓ Created user: {owner.username} (role: {owner.role.value})")
    print(f"✓ Created user: {editor.username} (role: {editor.role.value})")
    print(f"✓ Created user: {viewer.username} (role: {viewer.role.value})")
    
    # Authenticate
    print("\n2. Authenticating users...")
    auth_user = manager.authenticate_user('alice', 'pass123')
    if auth_user:
        print(f"✓ Successfully authenticated: {auth_user.username}")
    
    # Create team
    print("\n3. Creating team...")
    team = manager.create_team('Documentation Team', owner.user_id, 'Team for doc collaboration')
    print(f"✓ Created team: {team.name}")
    
    # Add team members
    print("\n4. Adding team members...")
    manager.add_team_member(team.team_id, editor.user_id, Role.EDITOR)
    manager.add_team_member(team.team_id, viewer.user_id, Role.VIEWER)
    print(f"✓ Added {editor.username} as EDITOR")
    print(f"✓ Added {viewer.username} as VIEWER")
    
    # Grant project access
    print("\n5. Granting project access...")
    manager.grant_project_access('project1', owner.user_id, user_id=editor.user_id, role=Role.EDITOR)
    print(f"✓ Granted EDITOR access to {editor.username} for project1")
    
    # Check permissions
    print("\n6. Checking permissions...")
    can_write = manager.check_permission(editor.user_id, 'project1', Permission.WRITE)
    can_manage = manager.check_permission(editor.user_id, 'project1', Permission.MANAGE_USERS)
    
    print(f"✓ {editor.username} can WRITE: {can_write}")
    print(f"✓ {editor.username} can MANAGE_USERS: {can_manage}")
    
    # Create API token
    print("\n7. Creating API token...")
    token = manager.create_api_token(editor.user_id, 'API Access', expires_in_days=30)
    print(f"✓ Created API token: {token[:20]}...")
    
    verified = manager.verify_api_token(token)
    print(f"✓ Token verified for user: {verified}")
    
    manager.close()
    print("\n✓ Membership demo complete!")


def demo_crdt():
    """Demonstrate CRDT operations."""
    print_section("CRDT Operations Demo")
    
    # Create document
    print("\n1. Creating CRDT document...")
    doc = CRDTDocument('doc1', '# AccuDoc\n\nDocumentation tool')
    print(f"✓ Initial content: '{doc.content}'")
    
    # Insert operation
    print("\n2. Applying INSERT operation...")
    op1 = doc.create_operation('user1', OperationType.INSERT, 10, '\n\n## Features')
    doc.apply_operation(op1)
    print(f"✓ After insert: '{doc.content}'")
    
    # Delete operation
    print("\n3. Applying DELETE operation...")
    op2 = doc.create_operation('user2', OperationType.DELETE, 10, length=2)
    doc.apply_operation(op2)
    print(f"✓ After delete: '{doc.content}'")
    
    # Replace operation
    print("\n4. Applying REPLACE operation...")
    op3 = doc.create_operation('user3', OperationType.REPLACE, 2, 'Project', 7)
    doc.apply_operation(op3)
    print(f"✓ After replace: '{doc.content}'")
    
    # Merge documents
    print("\n5. Merging concurrent edits...")
    doc2 = CRDTDocument('doc1', '# AccuDoc\n\nDocumentation tool')
    op4 = doc2.create_operation('user4', OperationType.INSERT, 28, ' for repositories')
    doc2.apply_operation(op4)
    
    print(f"✓ Doc1 content: '{doc.content}'")
    print(f"✓ Doc2 content: '{doc2.content}'")
    
    conflicts = doc.merge(doc2)
    print(f"✓ Merged documents (conflicts: {len(conflicts)})")
    print(f"✓ Final content: '{doc.content}'")
    
    # Document state
    print("\n6. Document state...")
    state = doc.get_state()
    print(f"✓ Document ID: {state['doc_id']}")
    print(f"✓ Version: {state['version']}")
    print(f"✓ Operations: {state['operation_count']}")
    
    print("\n✓ CRDT demo complete!")


def demo_collaboration():
    """Demonstrate collaborative sessions."""
    print_section("Collaborative Sessions Demo")
    
    # Create temporary database
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / 'demo_collaboration.db'
    manager = CollaborationManager(db_path)
    
    # Create session
    print("\n1. Creating collaborative session...")
    session = manager.create_session(
        project_id='project1',
        document_path='/docs/README.md',
        created_by='alice',
        initial_content='# Project Documentation\n\nWelcome to our project.'
    )
    print(f"✓ Session ID: {session.session_id}")
    print(f"✓ Document: {session.document_path}")
    print(f"✓ Status: {session.status.value}")
    
    # Join session
    print("\n2. Users joining session...")
    manager.join_session(session.session_id, 'bob', 'Bob Smith')
    manager.join_session(session.session_id, 'charlie', 'Charlie Jones')
    
    participants = manager.get_session_participants(session.session_id)
    print(f"✓ Participants: {len(participants)}")
    for p in participants:
        print(f"  - {p.username} (joined: {p.joined_at[:19]})")
    
    # Apply edits
    print("\n3. Applying collaborative edits...")
    op1 = manager.apply_operation(
        session.session_id, 'bob', OperationType.INSERT,
        23, '\n\n## Overview\nThis is a collaborative documentation project.'
    )
    print(f"✓ Bob added overview section")
    
    op2 = manager.apply_operation(
        session.session_id, 'charlie', OperationType.INSERT,
        0, '<!--- Header --->\n'
    )
    print(f"✓ Charlie added header comment")
    
    content = manager.get_session_content(session.session_id)
    print(f"\n✓ Current document content:")
    print("-" * 60)
    print(content)
    print("-" * 60)
    
    # Add comments
    print("\n4. Adding comments...")
    comment_id = manager.add_comment(
        session.session_id, 'charlie', 'Charlie Jones',
        'Should we add more details here?', position=50
    )
    print(f"✓ Comment added: {comment_id[:16]}...")
    
    comments = manager.get_session_comments(session.session_id)
    print(f"✓ Total comments: {len(comments)}")
    for c in comments:
        print(f"  - {c['username']}: {c['content']}")
    
    # Add suggestions
    print("\n5. Adding change suggestions...")
    suggestion_id = manager.add_suggestion(
        session.session_id, 'bob', 'Bob Smith',
        position=23, original_text='Welcome to our project.',
        suggested_text='Welcome to the AccuDoc project!',
        reason='More specific project name'
    )
    print(f"✓ Suggestion added: {suggestion_id[:16]}...")
    
    suggestions = manager.get_session_suggestions(session.session_id, status='pending')
    print(f"✓ Pending suggestions: {len(suggestions)}")
    for s in suggestions:
        print(f"  - {s['username']}: '{s['suggested_text']}'")
    
    # Review suggestion
    print("\n6. Reviewing suggestion...")
    manager.review_suggestion(suggestion_id, 'alice', accepted=True)
    print(f"✓ Suggestion accepted and applied")
    
    final_content = manager.get_session_content(session.session_id)
    print(f"\n✓ Updated document content:")
    print("-" * 60)
    print(final_content)
    print("-" * 60)
    
    # Close session
    print("\n7. Closing session...")
    manager.close_session(session.session_id)
    
    session = manager.get_session(session.session_id)
    print(f"✓ Session status: {session.status.value}")
    
    manager.close()
    print("\n✓ Collaboration demo complete!")


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("AccuDoc Collaborative Documentation Workspace Demo")
    print("=" * 60)
    
    try:
        demo_membership()
        demo_crdt()
        demo_collaboration()
        
        print("\n" + "=" * 60)
        print("All Demos Completed Successfully!")
        print("=" * 60)
        print("\nKey Features Demonstrated:")
        print("✓ User authentication and authorization")
        print("✓ Team management and access control")
        print("✓ API token generation and verification")
        print("✓ CRDT-based conflict-free editing")
        print("✓ Real-time collaborative sessions")
        print("✓ Comments and suggestions")
        print("✓ Audit trail logging")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
