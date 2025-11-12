#!/usr/bin/env python3
"""
AI Tekstanalyse Tool

Simpel GUI til at analysere og rette tekstfiler med AI.
"""

from src.gui import create_gui
from config import Config


def main():
    """
    Hovedfunktion der starter applikationen.
    """
    print("AI Tekstanalyse Tool")
    print("=" * 50)

    # Valider konfiguration
    try:
        Config.validate()
    except ValueError as e:
        print(f"Konfigurationsfejl: {e}")
        print("\nOpret en .env fil med dine API nøgler:")
        print("CLAUDE_API_KEY=your_api_key_here")
        print("# eller")
        print("OPENAI_API_KEY=your_api_key_here")
        return

    # Vis konfiguration
    print(f"Provider: {Config.LLM_PROVIDER}")
    print(f"Model: {Config.get_model()}")
    print(f"Server: http://{Config.GRADIO_SERVER_NAME}:{Config.GRADIO_SERVER_PORT}")
    print("=" * 50)

    # Opret og start GUI
    interface = create_gui(
        provider_type=Config.LLM_PROVIDER,
        api_key=Config.get_api_key(),
        model=Config.get_model()
    )

    # Start server
    interface.launch(
        share=Config.GRADIO_SHARE,
        server_name=Config.GRADIO_SERVER_NAME,
        server_port=Config.GRADIO_SERVER_PORT
    )


if __name__ == "__main__":
    main()
