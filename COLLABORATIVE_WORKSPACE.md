# Collaborative Documentation Workspace

AccuDoc now includes a powerful collaborative documentation workspace that allows multiple users to edit, comment, and suggest changes to documentation simultaneously.

## Overview

The collaborative workspace feature provides:

- **Multi-user real-time editing**: Multiple users can edit the same document simultaneously
- **CRDT-based conflict resolution**: Conflict-free replicated data types ensure consistency
- **Membership system**: Role-based access control for teams and projects
- **Session management**: Track and manage collaborative editing sessions
- **Comments and suggestions**: Discuss changes and propose improvements
- **Audit trail**: Complete logging of all collaborative activities

## Architecture

### Core Components

1. **Membership System** (`accudoc/membership.py`)
   - User authentication and authorization
   - Team management
   - Role-based access control
   - API token generation

2. **CRDT Engine** (`accudoc/crdt.py`)
   - Conflict-free replicated data types
   - Operational transformation
   - Automatic conflict resolution
   - Document versioning

3. **Collaboration Manager** (`accudoc/collaboration.py`)
   - Session lifecycle management
   - Participant tracking
   - Operation synchronization
   - Comments and suggestions

4. **Project Database Integration** (`accudoc/project_database.py`)
   - Session metadata storage
   - Cross-project session tracking
   - Historical session data

5. **Audit Trail** (`accudoc/audit.py`)
   - Complete activity logging
   - Security review capabilities
   - Compliance tracking

## Features

### 1. Membership & Access Control

#### User Roles

- **Owner**: Full control including user management and deletion
- **Admin**: Manage users and sessions
- **Editor**: Read, write, and comment
- **Viewer**: Read and comment only

#### Permissions

- `READ`: View documentation
- `WRITE`: Edit documentation
- `COMMENT`: Add comments
- `MANAGE_USERS`: Add/remove users
- `MANAGE_SESSIONS`: Create/close sessions
- `DELETE`: Delete content

#### Example Usage

```python
from accudoc.membership import MembershipManager, Role, Permission

# Create membership manager
manager = MembershipManager()

# Create users
owner = manager.create_user('alice', 'alice@example.com', 'password', Role.OWNER)
editor = manager.create_user('bob', 'bob@example.com', 'password', Role.EDITOR)

# Create team
team = manager.create_team('Documentation Team', owner.user_id)
manager.add_team_member(team.team_id, editor.user_id, Role.EDITOR)

# Grant project access
manager.grant_project_access('project1', owner.user_id, user_id=editor.user_id, role=Role.EDITOR)

# Check permissions
can_write = manager.check_permission(editor.user_id, 'project1', Permission.WRITE)
```

### 2. CRDT-Based Editing

The system uses Conflict-free Replicated Data Types (CRDTs) to ensure that concurrent edits from multiple users can be merged automatically without conflicts.

#### Supported Operations

- **INSERT**: Add text at a position
- **DELETE**: Remove text from a position
- **REPLACE**: Replace text at a position

#### Example Usage

```python
from accudoc.crdt import CRDTDocument, OperationType

# Create document
doc = CRDTDocument('doc1', '# Documentation\n\nContent here')

# User 1 inserts text
op1 = doc.create_operation('user1', OperationType.INSERT, 16, '\n\n## Overview')
doc.apply_operation(op1)

# User 2 edits concurrently
op2 = doc.create_operation('user2', OperationType.REPLACE, 2, 'Project', 13)
doc.apply_operation(op2)

# Merge changes from another document
other_doc = CRDTDocument('doc1', '# Documentation\n\nContent here')
conflicts = doc.merge(other_doc)
```

### 3. Collaborative Sessions

Sessions manage real-time collaboration with participant tracking, operation history, and comments.

#### Session Lifecycle

1. **Create**: Start a new collaborative session
2. **Join**: Users join the session
3. **Edit**: Apply operations to the document
4. **Comment**: Add comments and discussions
5. **Suggest**: Propose changes for review
6. **Close**: End the session

#### Example Usage

```python
from accudoc.collaboration import CollaborationManager, OperationType

# Create manager
manager = CollaborationManager()

# Create session
session = manager.create_session(
    project_id='project1',
    document_path='/docs/README.md',
    created_by='alice',
    initial_content='# Project Documentation'
)

# Join session
manager.join_session(session.session_id, 'bob', 'Bob Smith')
manager.join_session(session.session_id, 'charlie', 'Charlie Jones')

# Apply edit
operation = manager.apply_operation(
    session.session_id, 'bob', OperationType.INSERT,
    position=23, content='\n\n## Overview'
)

# Add comment
comment_id = manager.add_comment(
    session.session_id, 'charlie', 'Charlie Jones',
    'Great addition!', position=25
)

# Add suggestion
suggestion_id = manager.add_suggestion(
    session.session_id, 'bob', 'Bob Smith',
    position=0, suggested_text='# AccuDoc Project Documentation',
    original_text='# Project Documentation',
    reason='More specific title'
)

# Review suggestion
manager.review_suggestion(suggestion_id, 'alice', accepted=True)

# Close session
manager.close_session(session.session_id)
```

### 4. Comments & Suggestions

#### Comments

Users can add comments at specific positions in the document to discuss changes or ask questions.

```python
# Add comment
comment_id = manager.add_comment(
    session_id=session.session_id,
    user_id='user1',
    username='Alice',
    content='Should we expand this section?',
    position=100
)

# Get comments
comments = manager.get_session_comments(session.session_id)
```

#### Suggestions

Users can propose changes that must be reviewed and accepted/rejected.

```python
# Add suggestion
suggestion_id = manager.add_suggestion(
    session_id=session.session_id,
    user_id='user2',
    username='Bob',
    position=50,
    original_text='old text',
    suggested_text='improved text',
    reason='Better clarity'
)

# Review suggestion (accept)
manager.review_suggestion(suggestion_id, 'user1', accepted=True)

# Get pending suggestions
suggestions = manager.get_session_suggestions(session.session_id, status='pending')
```

### 5. Audit Trail

All collaborative activities are logged to the audit trail for transparency and traceability.

#### Logged Events

- User authentication
- Session creation/closure
- User joins/leaves
- Edit operations
- Comments added
- Suggestions created/reviewed

#### Example Audit Log

```
2025-11-15 13:44:10 - INFO - create_collaborative_session: success
  session_id: NN5caCByHcM96n_epnz_vA
  project_id: project1
  created_by: alice

2025-11-15 13:44:10 - INFO - join_collaborative_session: success
  session_id: NN5caCByHcM96n_epnz_vA
  user_id: bob

2025-11-15 13:44:10 - INFO - apply_collaborative_edit: success
  session_id: NN5caCByHcM96n_epnz_vA
  user_id: bob
  op_type: insert
  position: 23
```

### 6. Database Integration

Collaborative session metadata is stored in the project database for historical tracking and analysis.

```python
from accudoc.project_database import ProjectDatabase

# Create database
db = ProjectDatabase()

# Add session metadata
db.add_collaborative_session(
    session_id='session1',
    project_id='project1',
    document_path='/docs/README.md',
    created_by='alice'
)

# Update statistics
db.update_collaborative_session_stats(
    session_id='session1',
    participant_count=3,
    operation_count=15,
    comment_count=5,
    suggestion_count=2
)

# Get project sessions
sessions = db.get_project_collaborative_sessions('project1', status='active')

# Close session
db.close_collaborative_session('session1')
```

## Security Considerations

### Authentication

- Passwords are hashed using SHA-256 before storage
- API tokens are hashed and can have expiration dates
- User sessions are tracked with last activity timestamps

### Authorization

- Role-based access control (RBAC) for all operations
- Granular permissions for fine-grained access control
- Team-based access for group collaboration

### Audit Trail

- All operations are logged with user, timestamp, and details
- Immutable audit log for compliance
- Failed authentication attempts are tracked

## API Integration

The collaborative features can be integrated into REST APIs or other applications.

### Example REST API Endpoint

```python
from flask import Flask, request, jsonify
from accudoc.collaboration import CollaborationManager
from accudoc.membership import MembershipManager

app = Flask(__name__)
collab_manager = CollaborationManager()
membership_manager = MembershipManager()

@app.route('/api/collaborate/session', methods=['POST'])
def create_session():
    data = request.json
    token = request.headers.get('Authorization')
    
    # Verify token
    user_id = membership_manager.verify_api_token(token)
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Create session
    session = collab_manager.create_session(
        project_id=data['project_id'],
        document_path=data['document_path'],
        created_by=user_id,
        initial_content=data.get('content', '')
    )
    
    return jsonify({
        'session_id': session.session_id,
        'status': session.status.value
    })

@app.route('/api/collaborate/session/<session_id>/edit', methods=['POST'])
def apply_edit(session_id):
    data = request.json
    token = request.headers.get('Authorization')
    
    # Verify token
    user_id = membership_manager.verify_api_token(token)
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Apply operation
    operation = collab_manager.apply_operation(
        session_id=session_id,
        user_id=user_id,
        op_type=OperationType(data['op_type']),
        position=data['position'],
        content=data.get('content', ''),
        length=data.get('length', 0)
    )
    
    if operation:
        return jsonify({'success': True, 'op_id': operation.op_id})
    else:
        return jsonify({'error': 'Failed to apply operation'}), 400
```

## Testing

Comprehensive tests are provided in `test_collaboration.py`:

```bash
# Run tests
python test_collaboration.py

# Run specific test class
python -m unittest test_collaboration.TestMembershipSystem
python -m unittest test_collaboration.TestCRDT
python -m unittest test_collaboration.TestCollaboration
```

## Demo

A complete demo is available in `demo_collaboration.py`:

```bash
python demo_collaboration.py
```

The demo shows:
- User creation and authentication
- Team management
- Permission checking
- CRDT operations
- Collaborative session workflow
- Comments and suggestions

## Best Practices

### For Administrators

1. **Use teams**: Group users into teams for easier management
2. **Grant minimal permissions**: Follow principle of least privilege
3. **Review audit logs**: Regularly check for suspicious activity
4. **Set token expiration**: Use expiring API tokens for security

### For Developers

1. **Handle conflicts gracefully**: CRDT resolves most conflicts, but check for edge cases
2. **Validate operations**: Check user permissions before applying operations
3. **Track sessions**: Close sessions when done to free resources
4. **Use transactions**: Wrap database operations in transactions for consistency

### For Users

1. **Join sessions promptly**: Don't leave inactive sessions open
2. **Use comments**: Communicate changes to collaborators
3. **Review suggestions**: Respond to suggestions in a timely manner
4. **Save work frequently**: Operations are saved automatically, but close sessions when done

## Performance Considerations

### Scalability

- CRDT operations are O(n) where n is the number of concurrent operations
- Session data is indexed for fast lookups
- Database uses connection pooling for better performance

### Memory Usage

- Active sessions are kept in memory for fast access
- Inactive sessions are loaded from database on demand
- Old session data can be archived or pruned

### Network Optimization

- Operations can be batched for network efficiency
- Delta synchronization reduces bandwidth
- WebSocket support for real-time updates (future enhancement)

## Future Enhancements

### Planned Features

1. **Real-time WebSocket support**: Live updates without polling
2. **Conflict visualization**: Show conflicts in UI with resolution options
3. **Version control integration**: Sync with Git branches
4. **Offline mode**: Work offline and sync when connected
5. **Rich text editing**: Support for formatted text beyond markdown
6. **File attachments**: Attach files to comments and suggestions
7. **Presence indicators**: Show who's currently editing
8. **Cursor tracking**: See where other users are editing

### Integration Opportunities

- REST API endpoints for all collaborative features
- WebSocket server for real-time updates
- GUI integration in AccuDoc's Tkinter interface
- CLI commands for session management
- Export collaborative session history

## Troubleshooting

### Common Issues

**Q: Edits are not appearing**
A: Check that the session is active and the user has write permissions

**Q: Conflicts are occurring**
A: CRDT should resolve most conflicts automatically. Check audit logs for details

**Q: Authentication failing**
A: Verify password and check that user is active

**Q: Session not found**
A: Session may have been closed. Check session status in database

### Debug Mode

Enable debug logging for troubleshooting:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('accudoc.collaboration')
logger.setLevel(logging.DEBUG)
```

## License

The collaborative documentation workspace is part of AccuDoc and is licensed under the GNU General Public License v3.0.

---

*For more information, see the main AccuDoc README.md*
