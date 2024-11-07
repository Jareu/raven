from flask import Flask, request, Response, jsonify, make_response
from flask_cors import CORS
import requests
import os
import logging
from logging.handlers import RotatingFileHandler

class RavenServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.setup_cors()
        self.setup_logging()
        self.setup_api_keys()
        self.setup_routes()

    def setup_cors(self):
        """Configure CORS settings for the application."""
        CORS(self.app, resources={
            r"/*": {
                "origins": "*",
                "methods": ["GET", "POST", "OPTIONS"],
                "allow_headers": ["Content-Type"]
            }
        })

    def setup_logging(self):
        """Configure application logging."""
        if not self.app.debug:
            file_handler = RotatingFileHandler('raven.log', maxBytes=10240, backupCount=5)
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
            )
            file_handler.setLevel(logging.INFO)
            self.app.logger.addHandler(file_handler)
            self.app.logger.setLevel(logging.INFO)
            self.app.logger.info('Raven server startup')

    def setup_api_keys(self):
        """Configure API keys from environment variables."""
        self.openai_key = os.getenv('OPENAI_API_KEY', 'your-default-key')
        self.elevenlabs_key = os.getenv('ELEVENLABS_API_KEY', 'your-default-key')

    def generate_response_text(self, question):
        """Generate text response using OpenAI API via HTTP."""
        try:
            headers = {
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": question}
                ],
                "temperature": 1,
                "max_tokens": 100
            }
            response = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            self.app.logger.error(f"Error generating response: {str(e)}")
            raise

    def generate_audio_stream(self, text):
        """Generate audio stream using ElevenLabs API via HTTP."""
        try:
            headers = {
                "xi-api-key": self.elevenlabs_key,
                "Content-Type": "application/json"
            }
            payload = {
                "text": text,
                "model_id": "eleven_turbo_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.25
                }
            }
            response = requests.post(
                "https://api.elevenlabs.io/v1/text-to-speech/aYnsKRtbVPhAk1n2Gz0r/stream",
                headers=headers,
                json=payload,
                stream=True
            )
            response.raise_for_status()
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    yield chunk
        except Exception as e:
            self.app.logger.error(f"Error generating audio: {str(e)}")
            raise

    def setup_routes(self):
        """Configure application routes."""
        @self.app.before_request
        def handle_preflight():
            if request.method == "OPTIONS":
                response = make_response()
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
                response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                return response

        @self.app.route('/get_fortune', methods=['POST'])
        def get_fortune():
            data = request.json
            question = data.get("question")
            if not question:
                return jsonify({"error": "Question not provided"}), 400
            try:
                response_text = self.generate_response_text(question)
                return jsonify({"text": response_text})
            except Exception as e:
                self.app.logger.error(f"Error in get_fortune: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

        @self.app.route('/get_fortune_audio', methods=['POST'])
        def get_fortune_audio():
            data = request.json
            text = data.get("text")
            if not text:
                return jsonify({"error": "Text not provided"}), 400
            try:
                return Response(self.generate_audio_stream(text), mimetype='audio/mpeg')
            except Exception as e:
                self.app.logger.error(f"Error in get_fortune_audio: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

    def run(self, debug=False):
        """Run the Flask application."""
        self.app.run(debug=debug)

if __name__ == '__main__':
    server = RavenServer()
    server.run(debug=True)
