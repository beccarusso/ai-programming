# Campus Resource Assistant

An AI-powered assistant that helps students find information about campus resources.

## Features

- Natural language questions about campus services
- Accurate information sourced from verified data
- 24/7 availability through a web interface
- Conversation history within sessions

## Live App

**URL:** https://campus-resource-assistant.streamlit.app

## Local Development

1. Clone the repository
2. Create conda environment: `conda create -n ai-agents python=3.11`
3. Activate: `conda activate ai-agents`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file with: `GOOGLE_API_KEY=your-key-here`
6. Run: `streamlit run app.py`

## Project Structure

```
campus_agent/
├── agent.py                # ADK agent and tool definition
├── app.py                  # Streamlit web interface
├── campus_resources.json   # Verified campus data
├── requirements.txt        # Python dependencies
└── .streamlit/
    └── config.toml         # Streamlit configuration
```

## Data Verification

All campus resource information was verified against official college sources. See `campus_resources.json` for verification details including:

- Who verified the information (`verified_by`)
- When it was last checked (`last_verified`)

## Author

Rebecca Russo
CSC 2560 Introduction to AI Development
Fall 2026
