/**
 * Real-Time Collaboration Client for AccuDoc Electron GUI
 * 
 * Handles WebSocket connections, real-time document editing,
 * comments, reviews, and notifications.
 */

class CollaborationClient {
    constructor() {
        this.socket = null;
        this.clientId = null;
        this.currentUser = null;
        this.currentDocument = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        
        // Event listeners
        this.eventListeners = {
            'user_join': [],
            'user_leave': [],
            'document_edit': [],
            'cursor_move': [],
            'comment_add': [],
            'comment_update': [],
            'comment_delete': [],
            'review_request': [],
            'review_approve': [],
            'review_reject': [],
            'notification': []
        };
        
        // UI elements
        this.setupUI();
    }
    
    /**
     * Connect to collaboration server
     */
    async connect(serverUrl = 'ws://localhost:8765') {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            return;
        }
        
        try {
            this.socket = new WebSocket(serverUrl);
            
            this.socket.onopen = () => {
                console.log('Connected to collaboration server');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.updateConnectionStatus('connected');
            };
            
            this.socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (error) {
                    console.error('Error parsing message:', error);
                }
            };
            
            this.socket.onclose = () => {
                console.log('Disconnected from collaboration server');
                this.isConnected = false;
                this.updateConnectionStatus('disconnected');
                this.attemptReconnect(serverUrl);
            };
            
            this.socket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus('error');
            };
            
        } catch (error) {
            console.error('Failed to connect to collaboration server:', error);
            this.updateConnectionStatus('error');
        }
    }
    
    /**
     * Attempt to reconnect to server
     */
    attemptReconnect(serverUrl) {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.log('Max reconnection attempts reached');
            return;
        }
        
        this.reconnectAttempts++;
        console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        
        setTimeout(() => {
            this.connect(serverUrl);
        }, this.reconnectDelay * this.reconnectAttempts);
    }
    
    /**
     * Disconnect from server
     */
    disconnect() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
        this.isConnected = false;
        this.currentDocument = null;
        this.updateConnectionStatus('disconnected');
    }
    
    /**
     * Join a document session
     */
    joinDocument(documentId, user) {
        if (!this.isConnected) {
            console.error('Not connected to collaboration server');
            return;
        }
        
        this.currentUser = user;
        this.currentDocument = documentId;
        
        this.sendMessage({
            type: 'user_join',
            document_id: documentId,
            user: user
        });
        
        this.updateDocumentStatus(`Joined document: ${documentId}`);
    }
    
    /**
     * Leave current document session
     */
    leaveDocument() {
        if (!this.currentDocument) {
            return;
        }
        
        this.sendMessage({
            type: 'user_leave',
            document_id: this.currentDocument
        });
        
        this.currentDocument = null;
        this.updateDocumentStatus('No active document');
    }
    
    /**
     * Send document edit
     */
    sendDocumentEdit(operation, position, content = '') {
        if (!this.currentDocument) {
            console.error('No active document');
            return;
        }
        
        this.sendMessage({
            type: 'document_edit',
            document_id: this.currentDocument,
            operation: operation,
            position: position,
            content: content
        });
    }
    
    /**
     * Send cursor position
     */
    sendCursorMove(position) {
        if (!this.currentDocument) {
            return;
        }
        
        this.sendMessage({
            type: 'cursor_move',
            document_id: this.currentDocument,
            position: position
        });
    }
    
    /**
     * Add comment
     */
    addComment(content, lineStart, lineEnd, parentId = null) {
        if (!this.currentDocument) {
            console.error('No active document');
            return;
        }
        
        this.sendMessage({
            type: 'comment_add',
            action: 'add',
            document_id: this.currentDocument,
            content: content,
            line_start: lineStart,
            line_end: lineEnd,
            parent_id: parentId
        });
    }
    
    /**
     * Request review
     */
    requestReview(reviewerId) {
        if (!this.currentDocument) {
            console.error('No active document');
            return;
        }
        
        this.sendMessage({
            type: 'review_request',
            action: 'request',
            document_id: this.currentDocument,
            reviewer_id: reviewerId
        });
    }
    
    /**
     * Send message to server
     */
    sendMessage(message) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(message));
        } else {
            console.error('WebSocket is not connected');
        }
    }
    
    /**
     * Handle incoming messages
     */
    handleMessage(data) {
        const { type } = data;
        
        switch (type) {
            case 'connection_established':
                this.clientId = data.client_id;
                console.log('Client ID received:', this.clientId);
                break;
                
            case 'user_join':
                this.handleUserJoin(data);
                break;
                
            case 'user_leave':
                this.handleUserLeave(data);
                break;
                
            case 'document_edit':
                this.handleDocumentEdit(data);
                break;
                
            case 'cursor_move':
                this.handleCursorMove(data);
                break;
                
            case 'comment_add':
                this.handleCommentAdd(data);
                break;
                
            case 'review_request':
                this.handleReviewRequest(data);
                break;
                
            default:
                console.log('Unknown message type:', type);
        }
        
        // Trigger event listeners
        this.triggerEventListeners(type, data);
    }
    
    /**
     * Handle user joining document
     */
    handleUserJoin(data) {
        const { user } = data;
        console.log(`User joined: ${user.name}`);
        
        // Update active users list
        this.updateActiveUsersList();
        
        // Show notification
        this.showNotification(`${user.name} joined the document`, 'info');
    }
    
    /**
     * Handle user leaving document
     */
    handleUserLeave(data) {
        const { user } = data;
        console.log(`User left: ${user.name}`);
        
        // Update active users list
        this.updateActiveUsersList();
        
        // Show notification
        this.showNotification(`${user.name} left the document`, 'info');
    }
    
    /**
     * Handle document edit
     */
    handleDocumentEdit(data) {
        const { user, operation, position, content } = data;
        console.log(`Document edit by ${user.name}: ${operation} at ${position}`);
        
        // Apply edit to document (implement based on your editor)
        this.applyDocumentEdit(operation, position, content);
        
        // Show change indicator
        this.showChangeIndicator(user, operation);
    }
    
    /**
     * Handle cursor movement
     */
    handleCursorMove(data) {
        const { client_id, position, user } = data;
        
        // Update cursor position in editor
        this.updateRemoteCursor(client_id, position, user);
    }
    
    /**
     * Handle comment addition
     */
    handleCommentAdd(data) {
        const { comment } = data;
        console.log('New comment added:', comment);
        
        // Add comment to UI
        this.addCommentToUI(comment);
        
        // Show notification
        this.showNotification(`New comment by ${comment.user.name}`, 'info');
    }
    
    /**
     * Handle review request
     */
    handleReviewRequest(data) {
        const { requester, reviewer_id } = data;
        
        if (this.currentUser && this.currentUser.id === reviewer_id) {
            this.showNotification(`Review requested by ${requester.name}`, 'warning');
            this.showReviewDialog(data);
        }
    }
    
    /**
     * Setup UI elements
     */
    setupUI() {
        // Add collaboration panel to existing GUI
        const collaborationHTML = `
            <div id="collaboration-panel" class="collaboration-panel hidden">
                <div class="collaboration-header">
                    <h3>Real-Time Collaboration</h3>
                    <div class="connection-status" id="connectionStatus">
                        <span class="status-indicator disconnected"></span>
                        <span class="status-text">Disconnected</span>
                    </div>
                </div>
                
                <div class="collaboration-content">
                    <div class="user-section">
                        <h4>Active Users</h4>
                        <div id="activeUsersList" class="users-list"></div>
                    </div>
                    
                    <div class="comments-section">
                        <h4>Comments</h4>
                        <div id="commentsList" class="comments-list"></div>
                        <div class="add-comment">
                            <textarea id="newCommentText" placeholder="Add a comment..."></textarea>
                            <button id="addCommentBtn" class="btn btn-primary">Add Comment</button>
                        </div>
                    </div>
                    
                    <div class="review-section">
                        <h4>Review</h4>
                        <div class="review-controls">
                            <select id="reviewerSelect">
                                <option value="">Select reviewer...</option>
                            </select>
                            <button id="requestReviewBtn" class="btn btn-secondary">Request Review</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add to main container (assuming it exists)
        const mainContainer = document.querySelector('.main-container') || document.body;
        const collaborationPanel = document.createElement('div');
        collaborationPanel.innerHTML = collaborationHTML;
        mainContainer.appendChild(collaborationPanel.firstElementChild);
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Add collaboration tab to navigation
        this.addCollaborationTab();
    }
    
    /**
     * Setup event listeners for UI elements
     */
    setupEventListeners() {
        const addCommentBtn = document.getElementById('addCommentBtn');
        const requestReviewBtn = document.getElementById('requestReviewBtn');
        
        if (addCommentBtn) {
            addCommentBtn.addEventListener('click', () => {
                const commentText = document.getElementById('newCommentText').value.trim();
                if (commentText) {
                    this.addComment(commentText, 1, 1); // Default to line 1
                    document.getElementById('newCommentText').value = '';
                }
            });
        }
        
        if (requestReviewBtn) {
            requestReviewBtn.addEventListener('click', () => {
                const reviewerId = document.getElementById('reviewerSelect').value;
                if (reviewerId) {
                    this.requestReview(reviewerId);
                }
            });
        }
    }
    
    /**
     * Add collaboration tab to navigation
     */
    addCollaborationTab() {
        const navigation = document.querySelector('.navigation');
        if (!navigation) return;
        
        const collaborationItem = document.createElement('div');
        collaborationItem.className = 'nav-item';
        collaborationItem.innerHTML = `
            <i class="fas fa-users"></i>
            <span>Collaboration</span>
        `;
        
        collaborationItem.addEventListener('click', () => {
            this.showCollaborationPanel();
        });
        
        navigation.appendChild(collaborationItem);
    }
    
    /**
     * Show collaboration panel
     */
    showCollaborationPanel() {
        // Hide other views
        document.querySelectorAll('.view').forEach(view => {
            view.classList.add('hidden');
        });
        
        // Show collaboration panel
        const collaborationPanel = document.getElementById('collaboration-panel');
        if (collaborationPanel) {
            collaborationPanel.classList.remove('hidden');
        }
    }
    
    /**
     * Update connection status UI
     */
    updateConnectionStatus(status) {
        const statusIndicator = document.querySelector('.status-indicator');
        const statusText = document.querySelector('.status-text');
        
        if (statusIndicator && statusText) {
            statusIndicator.className = `status-indicator ${status}`;
            statusText.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        }
    }
    
    /**
     * Update document status
     */
    updateDocumentStatus(status) {
        console.log('Document status:', status);
        // Update UI as needed
    }
    
    /**
     * Update active users list
     */
    updateActiveUsersList() {
        const usersList = document.getElementById('activeUsersList');
        if (!usersList) return;
        
        // This would be populated with actual user data from server
        usersList.innerHTML = '<div class="user-item">Loading users...</div>';
    }
    
    /**
     * Add comment to UI
     */
    addCommentToUI(comment) {
        const commentsList = document.getElementById('commentsList');
        if (!commentsList) return;
        
        const commentElement = document.createElement('div');
        commentElement.className = 'comment-item';
        commentElement.innerHTML = `
            <div class="comment-header">
                <span class="comment-author">${comment.user.name}</span>
                <span class="comment-time">${new Date(comment.created_at).toLocaleString()}</span>
            </div>
            <div class="comment-content">${comment.content}</div>
            <div class="comment-location">Lines ${comment.line_start}-${comment.line_end}</div>
        `;
        
        commentsList.appendChild(commentElement);
    }
    
    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        // Use existing notification system or create new one
        if (typeof showNotification === 'function') {
            showNotification(message, type);
        } else {
            console.log(`Notification [${type}]: ${message}`);
        }
    }
    
    /**
     * Apply document edit (placeholder - implement based on your editor)
     */
    applyDocumentEdit(operation, position, content) {
        console.log('Applying document edit:', { operation, position, content });
        // This would integrate with your document editor
    }
    
    /**
     * Update remote cursor position (placeholder)
     */
    updateRemoteCursor(clientId, position, user) {
        console.log('Remote cursor update:', { clientId, position, user });
        // This would show other users' cursor positions in the editor
    }
    
    /**
     * Show change indicator
     */
    showChangeIndicator(user, operation) {
        // Show visual indication of changes by other users
        this.showNotification(`${user.name} made a ${operation}`, 'info');
    }
    
    /**
     * Show review dialog
     */
    showReviewDialog(reviewData) {
        const dialog = document.createElement('div');
        dialog.className = 'review-dialog modal';
        dialog.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Review Request</h3>
                    <span class="close">&times;</span>
                </div>
                <div class="modal-body">
                    <p>You have been requested to review this document by ${reviewData.requester.name}.</p>
                    <div class="review-actions">
                        <button id="approveBtn" class="btn btn-success">Approve</button>
                        <button id="rejectBtn" class="btn btn-danger">Reject</button>
                        <button id="laterBtn" class="btn btn-secondary">Review Later</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(dialog);
        
        // Setup dialog event listeners
        dialog.querySelector('.close').addEventListener('click', () => {
            dialog.remove();
        });
        
        dialog.querySelector('#laterBtn').addEventListener('click', () => {
            dialog.remove();
        });
        
        // Show dialog
        dialog.style.display = 'block';
    }
    
    /**
     * Add event listener for collaboration events
     */
    addEventListener(eventType, callback) {
        if (this.eventListeners[eventType]) {
            this.eventListeners[eventType].push(callback);
        }
    }
    
    /**
     * Trigger event listeners
     */
    triggerEventListeners(eventType, data) {
        if (this.eventListeners[eventType]) {
            this.eventListeners[eventType].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error('Error in event listener:', error);
                }
            });
        }
    }
}

// Global collaboration client instance
let collaborationClient = null;

// Initialize collaboration when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    collaborationClient = new CollaborationClient();
    
    // Auto-connect if server is available
    setTimeout(() => {
        collaborationClient.connect();
    }, 1000);
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CollaborationClient;
}