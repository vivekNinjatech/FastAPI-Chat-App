from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json
import datetime

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>WhatsApp-like Chat with Reply and Menu</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
        <style>
            :root {
                --body-bg-light: #f0f2f5;
                --chat-container-bg-light: #ffffff;
                --message-list-bg-light: #ECE5DD;
                --my-message-bg-light: #DCF8C6;
                --other-message-bg-light: #FFFFFF;
                --status-message-color-light: #888;
                --text-color-light: #333;
                --input-bg-light: #f0f2f5;
                --input-border-light: #ccc;
                --header-bg-light: #075E54;
                --header-text-light: white;
                --menu-text-light: black;
                --menu-bg-light: white;
                --chat-background: var(--message-list-bg-light); /* Default chat theme */
            }

            /* Dark Mode Variables */
            body.dark-mode {
                --body-bg-light: #121212;
                --chat-container-bg-light: #1c1c1c;
                --message-list-bg-light: #262626; /* Darker WhatsApp chat background */
                --my-message-bg-light: #075E54; /* Darker green */
                --other-message-bg-light: #36454F; /* Darker grey/blue */
                --status-message-color-light: #bbb;
                --text-color-light: #eee;
                --input-bg-light: #333333;
                --input-border-light: #555;
                --header-bg-light: #075E54; /* Keep header green for dark mode */
                --header-text-light: white;
                --menu-text-light: white;
                --menu-bg-light: #2c2c2c;
            }

            body {
                font-family: Arial, sans-serif;
                background-color: var(--body-bg-light);
                margin: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                color: var(--text-color-light); /* Apply default text color */
            }
            .chat-container {
                width: 100%;
                max-width: 600px;
                background-color: var(--chat-container-bg-light);
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                overflow: hidden;
                display: flex;
                flex-direction: column;
                height: 80vh; /* Adjust height as needed */
            }
            .chat-header {
                background-color: var(--header-bg-light);
                color: var(--header-text-light);
                padding: 15px;
                text-align: center;
                font-size: 1.2em;
                font-weight: bold;
                position: relative; /* For dropdown positioning */
            }
            .message-list {
                flex-grow: 1;
                overflow-y: auto;
                padding: 15px;
                background-color: var(--chat-background); /* Use dynamic theme variable */
            }
            .message-item {
                display: flex;
                margin-bottom: 10px;
                cursor: pointer; /* Indicate messages are clickable */
            }
            .my-message .message-bubble {
                background-color: var(--my-message-bg-light); /* My message color */
                align-self: flex-end;
                margin-left: auto; /* Push to the right */
            }
            .other-message .message-bubble {
                background-color: var(--other-message-bg-light); /* Other message color */
                align-self: flex-start;
                margin-right: auto; /* Push to the left */
            }
            .status-message {
                text-align: center;
                font-style: italic;
                color: var(--status-message-color-light);
                font-size: 0.9em;
                margin: 10px 0;
            }
            .message-bubble {
                max-width: 75%;
                padding: 8px 12px;
                border-radius: 8px;
                box-shadow: 0 1px 0.5px rgba(0, 0, 0, 0.13);
                position: relative;
                color: var(--text-color-light); /* Ensure message text color adapts */
            }
            .message-sender {
                font-weight: bold;
                margin-bottom: 3px;
                font-size: 0.9em;
                color: #34B7F1; /* A WhatsApp-like sender color */
            }
            .my-message .message-sender {
                color: #25D366; /* Another WhatsApp-like sender color for self */
            }
            .message-text {
                font-size: 1em;
                word-wrap: break-word;
            }
            .message-time {
                font-size: 0.7em;
                color: #888;
                text-align: right;
                margin-top: 5px;
            }
            /* Reply Feature Styling */
            .message-bubble.selected-for-reply {
                outline: 2px solid #007bff; /* Highlight selected message */
            }
            .reply-preview {
                display: flex;
                align-items: center;
                background-color: var(--input-bg-light); /* Use input area background for preview */
                padding: 8px 12px;
                border-radius: 8px 8px 0 0;
                margin-bottom: -10px; /* Overlap with input slightly */
                border-bottom: 1px solid var(--input-border-light);
                font-size: 0.9em;
                color: var(--text-color-light);
            }
            .reply-preview-text {
                flex-grow: 1;
                margin-left: 10px;
                overflow: hidden;
                white-space: nowrap;
                text-overflow: ellipsis;
            }
            .reply-preview-close {
                cursor: pointer;
                font-weight: bold;
                font-size: 1.2em;
                margin-left: 10px;
                color: var(--status-message-color-light);
            }
            .reply-quote {
                border-left: 4px solid #34B7F1; /* WhatsApp-like blue bar */
                padding-left: 8px;
                margin-bottom: 5px;
                background-color: rgba(0,0,0,0.05); /* Slightly darker background for quote */
                border-radius: 3px;
                font-size: 0.85em;
                color: var(--text-color-light);
                max-height: 50px; /* Limit height of quoted text */
                overflow: hidden; /* Hide overflow */
                text-overflow: ellipsis; /* Add ellipsis */
                white-space: nowrap; /* Prevent wrapping */
            }
            .reply-quote .quote-sender {
                font-weight: bold;
                color: #34B7F1;
            }
            .reply-quote .quote-text {
                font-style: italic;
            }

            .chat-input-area {
                padding: 15px;
                border-top: 1px solid #ddd;
                background-color: var(--input-bg-light); /* Input area background */
            }
            .chat-input-area form {
                display: flex;
            }
            .chat-input-area input[type="text"] {
                flex-grow: 1;
                border-radius: 20px;
                border: 1px solid var(--input-border-light);
                padding: 10px 15px;
                margin-right: 10px;
                background-color: var(--chat-container-bg-light); /* Input field background */
                color: var(--text-color-light);
            }
            .chat-input-area button {
                border-radius: 20px;
                padding: 10px 20px;
                background-color: #25D366; /* WhatsApp green */
                border: none;
                color: white;
                font-weight: bold;
            }
            .chat-input-area button:hover {
                background-color: #1DA851;
            }

            /* Menu Styling */
            .menu-button {
                position: absolute;
                right: 15px;
                top: 50%;
                transform: translateY(-50%);
                background: none;
                border: none;
                color: white;
                font-size: 1.5em;
                cursor: pointer;
            }
            .dropdown-menu {
                background-color: var(--menu-bg-light);
                border: 1px solid var(--input-border-light);
            }
            .dropdown-item {
                color: var(--menu-text-light);
            }
            .dropdown-item:hover {
                background-color: rgba(0, 0, 0, 0.1);
            }
            .theme-swatches {
                display: flex;
                padding: 5px 15px;
                gap: 5px;
            }
            .color-swatch {
                width: 25px;
                height: 25px;
                border-radius: 50%;
                border: 1px solid #ccc;
                cursor: pointer;
                box-shadow: 0 0 3px rgba(0,0,0,0.2);
            }
            .color-swatch:hover {
                border-color: #007bff;
            }
        </style>
    </head>
    <body>
        <div class="chat-container" id="chatContainer">
            <div class="chat-header">
                FastAPI WhatsApp-ish Chat
                <div class="dropdown">
                    <button class="menu-button" type="button" id="dropdownMenuButton" data-bs-toggle="dropdown" aria-expanded="false">
                        <i class="bi bi-three-dots-vertical"></i>
                    </button>
                    <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="dropdownMenuButton">
                        <li><a class="dropdown-item" href="#" onclick="toggleDarkMode(event)">Dark Mode</a></li>
                        <li><a class="dropdown-item" href="#" onclick="clearChat(event)">Clear Chat</a></li>
                        <li><a class="dropdown-item" href="#" onclick="blockUser(event)">Block User (Demo)</a></li>
                        <li>
                            <a class="dropdown-item dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                                Change Chat Theme
                            </a>
                            <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarDropdown">
                                <li><div class="theme-swatches">
                                    <div class="color-swatch" style="background-color: #ECE5DD;" onclick="changeChatTheme('#ECE5DD', event)"></div>
                                    <div class="color-swatch" style="background-color: #DDE2E7;" onclick="changeChatTheme('#DDE2E7', event)"></div>
                                    <div class="color-swatch" style="background-color: #E6E7E9;" onclick="changeChatTheme('#E6E7E9', event)"></div>
                                    <div class="color-swatch" style="background-color: #F8F9FA;" onclick="changeChatTheme('#F8F9FA', event)"></div>
                                    <div class="color-swatch" style="background-color: #CCEEFF;" onclick="changeChatTheme('#CCEEFF', event)"></div>
                                </div></li>
                            </ul>
                        </li>
                    </ul>
                </div>
            </div>
            <div class="message-list" id="messages">
                </div>
            <div id="replyPreview" class="reply-preview" style="display:none;">
                <div class="reply-preview-content">
                    <span class="reply-preview-sender fw-bold"></span>
                    <div class="reply-preview-text"></div>
                </div>
                <span class="reply-preview-close" onclick="cancelReply()">X</span>
            </div>
            <div class="chat-input-area">
                <form action="" onsubmit="sendMessage(event)">
                    <input type="text" id="messageText" autocomplete="off" placeholder="Type a message..."/>
                    <button type="submit">Send</button>
                </form>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous"></script>

        <script>
            var client_id = Date.now(); // Unique ID for this client instance
            var username = ""; // User's chosen name
            var selectedMessage = null; // Stores { id, sender, text } of message being replied to
            const messagesList = document.getElementById('messages'); // Get messages list once

            // Prompt for username on load
            window.onload = function() {
                let name = prompt("Please enter your name:");
                if (name) {
                    username = name.trim();
                } else {
                    username = "Guest-" + client_id; // Default if no name entered
                }
                document.title = "Chat as " + username; // Update page title
                initializeWebSocket();
                loadThemePreference(); // Load dark mode preference
                loadChatTheme();       // Load chat background theme
            };

            var ws;

            function initializeWebSocket() {
                ws = new WebSocket(`ws://localhost:8000/ws/${client_id}?username=${encodeURIComponent(username)}`);

                ws.onmessage = function(event) {
                    var msgData = JSON.parse(event.data); // Parse the JSON message

                    if (msgData.type === 'status') {
                        // Display status messages (join/leave)
                        var statusDiv = document.createElement('div');
                        statusDiv.className = 'status-message';
                        statusDiv.textContent = msgData.message;
                        messagesList.appendChild(statusDiv);
                    } else if (msgData.type === 'chat') {
                        // Display chat messages
                        var messageId = 'msg-' + msgData.timestamp + '-' + msgData.sender.replace(/\s/g, ''); // Simple unique ID for now
                        
                        var messageItem = document.createElement('div');
                        messageItem.className = 'message-item';
                        messageItem.setAttribute('data-message-id', messageId); // Add data attribute for ID
                        messageItem.setAttribute('data-sender', msgData.sender); // Add data attribute for sender
                        messageItem.setAttribute('data-message-text', msgData.message); // Add data attribute for message text
                        messageItem.onclick = function() {
                            selectMessageForReply(messageId, msgData.sender, msgData.message);
                        };

                        var messageBubble = document.createElement('div');
                        messageBubble.className = 'message-bubble';
                        messageBubble.id = messageId; // Set ID for direct access

                        // If it's a reply, add the quoted message block
                        if (msgData.replied_to_message) {
                            var replyQuote = document.createElement('div');
                            replyQuote.className = 'reply-quote';
                            
                            var quoteSender = document.createElement('div');
                            quoteSender.className = 'quote-sender';
                            quoteSender.textContent = msgData.replied_to_sender;

                            var quoteText = document.createElement('div');
                            quoteText.className = 'quote-text';
                            quoteText.textContent = msgData.replied_to_message;

                            replyQuote.appendChild(quoteSender);
                            replyQuote.appendChild(quoteText);
                            messageBubble.appendChild(replyQuote);
                        }

                        var senderName = document.createElement('div');
                        senderName.className = 'message-sender';
                        senderName.textContent = msgData.sender;

                        var messageText = document.createElement('div');
                        messageText.className = 'message-text';
                        messageText.textContent = msgData.message;

                        var messageTime = document.createElement('div');
                        messageTime.className = 'message-time';
                        messageTime.textContent = formatTimestamp(msgData.timestamp);

                        // Add specific class for my messages vs. others' messages
                        if (msgData.sender === username) {
                            messageItem.classList.add('my-message');
                        } else {
                            messageItem.classList.add('other-message');
                        }
                        
                        messageBubble.appendChild(senderName);
                        messageBubble.appendChild(messageText);
                        messageBubble.appendChild(messageTime);
                        messageItem.appendChild(messageBubble);
                        messagesList.appendChild(messageItem);
                    }

                    scrollToBottom();
                };

                ws.onclose = function(event) {
                    console.log('WebSocket closed:', event);
                    var statusDiv = document.createElement('div');
                    statusDiv.className = 'status-message';
                    statusDiv.textContent = "Disconnected from chat. Please refresh to rejoin.";
                    messagesList.appendChild(statusDiv);
                    scrollToBottom();
                };

                ws.onerror = function(error) {
                    console.error('WebSocket error:', error);
                };
            }

            function sendMessage(event) {
                var input = document.getElementById("messageText");
                if (input.value.trim() !== "") {
                    // Prepare message data
                    let messageData = {
                        message: input.value,
                        type: 'chat' // Default type
                    };

                    // If a message is selected for reply, add its details
                    if (selectedMessage) {
                        messageData.replied_to_id = selectedMessage.id;
                        messageData.replied_to_sender = selectedMessage.sender;
                        messageData.replied_to_message = selectedMessage.text;
                    }
                    
                    ws.send(JSON.stringify(messageData)); // Send as JSON string
                    input.value = '';
                    cancelReply(); // Clear reply selection after sending
                }
                event.preventDefault();
            }

            function formatTimestamp(timestamp) {
                const date = new Date(timestamp);
                const hours = date.getHours().toString().padStart(2, '0');
                const minutes = date.getMinutes().toString().padStart(2, '0');
                return `${hours}:${minutes}`;
            }

            function scrollToBottom() {
                messagesList.scrollTop = messagesList.scrollHeight;
            }

            function selectMessageForReply(messageId, sender, messageText) {
                // Remove highlight from previously selected message
                if (selectedMessage) {
                    const prevSelectedBubble = document.getElementById(selectedMessage.id);
                    if (prevSelectedBubble) {
                        prevSelectedBubble.classList.remove('selected-for-reply');
                    }
                }

                // Highlight the newly selected message
                const newSelectedBubble = document.getElementById(messageId);
                if (newSelectedBubble) {
                    newSelectedBubble.classList.add('selected-for-reply');
                }

                selectedMessage = {
                    id: messageId,
                    sender: sender,
                    text: messageText
                };

                // Update and show the reply preview
                document.querySelector('#replyPreview .reply-preview-sender').textContent = sender;
                document.querySelector('#replyPreview .reply-preview-text').textContent = messageText;
                document.getElementById('replyPreview').style.display = 'flex';
                document.getElementById('messageText').focus(); // Focus on input field
            }

            function cancelReply() {
                if (selectedMessage) {
                    const prevSelectedBubble = document.getElementById(selectedMessage.id);
                    if (prevSelectedBubble) {
                        prevSelectedBubble.classList.remove('selected-for-reply');
                    }
                }
                selectedMessage = null;
                document.getElementById('replyPreview').style.display = 'none';
                document.querySelector('#replyPreview .reply-preview-sender').textContent = '';
                document.querySelector('#replyPreview .reply-preview-text').textContent = '';
            }

            // --- Menu Functions ---

            function toggleDarkMode(event) {
                event.preventDefault(); // Prevent default link behavior
                document.body.classList.toggle('dark-mode');
                // Store preference in localStorage
                if (document.body.classList.contains('dark-mode')) {
                    localStorage.setItem('chat-dark-mode', 'enabled');
                } else {
                    localStorage.removeItem('chat-dark-mode');
                }
            }

            function loadThemePreference() {
                if (localStorage.getItem('chat-dark-mode') === 'enabled') {
                    document.body.classList.add('dark-mode');
                }
            }

            function clearChat(event) {
                event.preventDefault(); // Prevent default link behavior
                if (confirm("Are you sure you want to clear the entire chat? This action cannot be undone.")) {
                    messagesList.innerHTML = ''; // Remove all child elements
                    cancelReply(); // Clear any active reply selection
                    // Add a status message
                    var statusDiv = document.createElement('div');
                    statusDiv.className = 'status-message';
                    statusDiv.textContent = "Chat history cleared.";
                    messagesList.appendChild(statusDiv);
                    scrollToBottom();
                }
            }

            function blockUser(event) {
                event.preventDefault(); // Prevent default link behavior
                // This is a client-side demo. In a real app, this would involve:
                // 1. Identifying the user to block (e.g., from a selected message's sender, or a user list).
                // 2. Sending an API request to the backend: ws.send(JSON.stringify({type: 'block', targetUser: 'SomeUser'}));
                // 3. Backend database stores the block, and modifies broadcast logic.
                alert("This is a demo for 'Block User'. In a real application, this would send a request to the server to prevent messages from a specific user.");
                // You might prompt the user to select who to block or block the last sender.
                // For simplicity, we'll just show an alert.
            }

            function changeChatTheme(color, event) {
                event.preventDefault(); // Prevent default link behavior
                // Set the CSS custom property for the chat background
                document.documentElement.style.setProperty('--chat-background', color);
                localStorage.setItem('chat-background-theme', color); // Save preference
                // Close the dropdown menu after selection
                var dropdown = new bootstrap.Dropdown(document.getElementById('dropdownMenuButton'));
                dropdown.hide();
            }

            function loadChatTheme() {
                const savedTheme = localStorage.getItem('chat-background-theme');
                if (savedTheme) {
                    document.documentElement.style.setProperty('--chat-background', savedTheme);
                } else {
                    // Default to WhatsApp-like theme if none saved
                    document.documentElement.style.setProperty('--chat-background', '#ECE5DD');
                }
            }
        </script>
    </body>
</html>
"""

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}
        self.client_names: dict[int, str] = {} # To store client IDs and their chosen names
    
    async def connect(self, websocket: WebSocket, client_id: int, username: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.client_names[client_id] = username
        print(f"Client #{client_id} ({username}) connected.")

    def disconnect(self, websocket: WebSocket, client_id: int):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.client_names:
            del self.client_names[client_id]
        print(f"Client #{client_id} disconnected.")

    async def send_json_message(self, message: dict, websocket: WebSocket):
        await websocket.send_text(json.dumps(message))
    
    async def broadcast(self, message: dict):
        # Using list() to avoid issues if connections are removed during iteration
        for client_id, connection in list(self.active_connections.items()):
            try:
                await connection.send_text(json.dumps(message))
            except RuntimeError as e:
                print(f"Error sending to client {client_id}: {e}. Removing connection.")
                self.disconnect(connection, client_id)


manager = ConnectionManager()


@app.get("/", response_class=HTMLResponse)
async def get():
    return HTMLResponse(content=html)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int, username: str = "Anonymous"):
    username = username or f"Guest-{client_id}"

    await manager.connect(websocket, client_id, username)

    join_message = {
        "type": "status",
        "message": f"'{username}' has joined the chat.",
        "timestamp": datetime.datetime.now().isoformat()
    }
    await manager.broadcast(join_message)

    try: 
        while True:
            # Receive raw text, then parse as JSON
            raw_data = await websocket.receive_text()
            received_message_data = json.loads(raw_data)
            
            # Construct the message to broadcast
            chat_message = {
                "type": "chat",
                "sender": username,
                "message": received_message_data.get("message"), # Get the actual message text
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Add reply specific fields if they exist in the received data
            if "replied_to_id" in received_message_data:
                chat_message["replied_to_id"] = received_message_data["replied_to_id"]
                chat_message["replied_to_sender"] = received_message_data["replied_to_sender"]
                chat_message["replied_to_message"] = received_message_data["replied_to_message"]
            
            await manager.broadcast(chat_message)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, client_id)
        leave_message = {
            "type": "status",
            "message": f"'{username}' has left the chat.",
            "timestamp": datetime.datetime.now().isoformat()
        }
        await manager.broadcast(leave_message)