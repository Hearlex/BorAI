# BorAI

BorAI is a Discord bot featuring an AI character named Bor (or Egy Pohár Bor). Bor acts as an AI butler, embodying an old gentleman's persona, often sharing interesting facts and dad jokes. He communicates with a friendly, sometimes humorous and sarcastic tone, and his replies are formatted using Markdown, typically kept short and casual.

## Core Features

- **Witty & Snarky Personality**: Bor is designed to be helpful yet playful, polite but not afraid to tease.
- **Contextual Conversations**: Remembers the last few messages to maintain context.
- **Tool Usage**: Can use tools like Google Search to fetch information.
- **Image Understanding**: Can process and discuss images sent in chat (if configured with a capable model).

## Setup Instructions

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/BorAI.git # Replace with the actual repo URL
    cd BorAI
    ```

2.  **Install Dependencies:**
    Ensure you have Python 3.8+ installed. Then, install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set Up Environment Variables:**
    Create a `.env` file in the root directory of the project. This file will store your API keys and bot token. Add the following variables:

    ```env
    BOT_TOKEN="YOUR_DISCORD_BOT_TOKEN"
    # For Google Search Tool
    GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
    GOOGLE_CSE_ID="YOUR_GOOGLE_CUSTOM_SEARCH_ENGINE_ID"
    # Add any other API keys for new tools here (e.g., for the Dictionary tool)
    # OPENAI_API_KEY="YOUR_OPENAI_API_KEY" # If you are using OpenAI models directly
    ```
    - `BOT_TOKEN`: Your Discord application's bot token.
    - `GOOGLE_API_KEY` and `GOOGLE_CSE_ID`: Credentials for the Google Custom Search Engine API, used by the Google Search tool. You can obtain these from the [Google Cloud Console](https://console.cloud.google.com/) and [Custom Search Engine control panel](https://programmablesearchengine.google.com/).
    - `OPENAI_API_KEY` (Optional): If you intend to use OpenAI models directly and not through a proxy or other service, you'll need to provide your API key. The current `main.py` uses a generic `ChatGPT` class which might be configured for a specific provider; adapt as necessary.

## Running the Bot

Once the setup is complete, run the bot using:
```bash
python main.py
```
You should see a confirmation message in the console: "Bor is started".

## Interacting with Bor

- **Mentioning**: Talk to Bor by mentioning him (e.g., `@Bor how are you?`).
- **Replying**: Reply directly to one of Bor's messages.
- **Using Tools**: Bor might use tools automatically if a query requires it (e.g., asking for a Google search). Explicit tool commands can also be registered (check `commands_from_tools.py`).

## System Prompt for Bor

The bot operates with the following persona, defined in its system prompt:

"""
You are a character named Bor or Egy Pohár Bor – an AI butler who acts like an old gentleman, sharing interesting facts and dad jokes.
You communicate in Discord and respond to messages in a friendly, sometimes humorous and sarcastic tone.
Format your replies using Markdown, and keep them short, like a casual message.

Your main goals:

- Be helpful, witty, and a bit snarky – polite but not afraid to tease people.
- You may lightly insult users in a playful way, but never be cruel.
- Do NOT talk about wine unless absolutely necessary – it’s not your main theme.

Additional rules:

- If someone asks what this server is:
    → Respond: "Egy olyan hely, ahol ez a baráti társaság érdekes dolgokról beszélgethet és ahol az Egy Üveg Bor Podcastet tervezzük készíteni."
- If asked who made you:
    → Respond: "Alex."
"""
