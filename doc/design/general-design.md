# System General Design

The purpose of this tool is to provide users with an intelligent assistant platform that supports both built-in and custom AI models for conversational tasks. It enables users to interact with AI, upload files, and maintain persistent conversation history. The system is designed to enhance productivity by leveraging advanced AI capabilities, personal data referencing, and seamless user experience across devices.

## Key Features

- Multi-users
- Built-in models and allow custom models, charge on usage
- Persistent conversation history
- Extract information from history data (includes conversation and uploaded files) to vector database
- Support thinking mode, tool calling, MCP

## General UI Design

- Single page application
- Support light/dark theme
- Support multi-languages
- Two columns layout
  - Left sidebar
    - Conversation list, are splited into groups: Today, Yesterday, This week, This month, and the months before this
    - User status bar at the bottom
    - Sidebar can be collapsed
  - Chat area
    - Subject of the conversation on the top
      - Theme switch on the right side
    - Chatting message area in the midlle
      - Bubble style message box
      - Assistant message on the left side, and user message on the right side
      - Assistant message and user message distinguished by colors
    - User input area at the bottom, it has three layers
      - File uploader toolbar on the top
      - Textarea in the middle, auto adjust heights based on the input
      - A toolbar on the bottom
        - A set of tools about models, such as model selector, model status info, and setting button, etc.
        - Send button on the right
    - A collapsible preview panel can be displayed with the chatting message area and input area side by side
      - The preview panel supports multi-tabs
