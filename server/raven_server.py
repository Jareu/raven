from flask import Flask, request, Response, jsonify, make_response
from flask_cors import CORS
from openai import OpenAI
from elevenlabs.client import ElevenLabs
import requests
import os
import logging
from logging.handlers import RotatingFileHandler
import numpy as np
from scipy import signal  # For audio processing

class RavenServer:
    def __init__(self):
        self.app = Flask(__name__)

        self.setup_cors()
        self.setup_logging()
        self.setup_api_keys()
        self.setup_openai()
        self.setup_routes()
        self.setup_audio_effects()

    def setup_cors(self):
        """Configure CORS settings for the application"""
        CORS(self.app, resources={
            r"/*": {
                "origins": "*",
                "methods": ["GET", "POST", "OPTIONS"],
                "allow_headers": ["Content-Type"]
            }
        })
        
    def setup_logging(self):
        """Configure application logging"""
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
        """Configure API keys from environment variables"""
        self.openai_key = os.environ.get('OPENAI_API_KEY') or 'your-default-key'
        self.elevenlabs_key = os.environ.get('ELEVENLABS_API_KEY') or 'your-default-key'

    def setup_openai(self):
        """Initialize OpenAI client and prompt"""
        self.client = OpenAI(api_key=self.openai_key)

        self.prompt = (
            "Respond as Huginn, Odin's all-seeing raven, who speaks with the voice of "
            "ancient wisdom and mystery. Huginn is wise and poetic, often seeing "
            "deep into the soul of those who seek his guidance. Speak as though you see "
            "what the seeker cannot, hinting at their inner struggles and offering advice "
            "that resonates deeply. Provide a direct answer to the question, and then follow "
            "up with one or two short sentences, making use of Barnum statements. Keep the tone "
            "wise, solemn, and slightly ominous. Reference figures from Norse mythology." +
            "your complete answer will be a single paragraph, not be more than 3 sentences."
        )

        self.prompt1 = (
            "Respond as Huginn, Odin's all-seeing raven, who speaks with the voice of "
            "ancient wisdom and mystery. Huginn is wise, cryptic, and poetic, often seeing "
            "deep into the soul of those who seek his guidance. Huginn's words should be "
            "filled with Norse imagery, drawing from nature, mythology, and the shadows of fate. "
            "Your words should echo with Norse mythology and be shrouded in ambiguity, each "
            "sentence crafted to feel both specific and universal. Speak as though you see "
            "what the seeker cannot, hinting at their inner struggles and offering advice "
            "that resonates deeply. Answer the question directly, in a few words. Then follow up with one or two sentences. "
            " make use of Barnum statements and avoid specifics; instead, speak of ‘paths,’ ‘shadows,’ ‘winds of change,’ or "
            "the fires of dawn.’ Keep the tone wise, solemn, and slightly ominous. "
            "Reference ancient wisdom, then provide an answer. Responses should be short, "
            "no more than 1 or 2 sentences, with an air of solemnity and depth."
        )

    def generate_response_text(self, question):
        """Generate text response using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": f"{self.prompt}\nQuestion: {question}\nResponse:"}],
                temperature=1,
                max_tokens=100,
                top_p=1,
                frequency_penalty=0.5,
                presence_penalty=0.15,
                response_format={"type": "text"}
            )
            return response.choices[0].message.content
        except Exception as e:
            self.app.logger.error(f"Error generating response: {str(e)}")
            raise

    def setup_routes(self):
        """Configure application routes"""
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
            
            return Response(self.generate_audio_stream(text), mimetype='audio/mpeg')

    def setup_audio_effects(self):
        """Configure audio effects parameters"""
        # Reverb parameters
        self.reverb_delay = 0.1  # seconds
        self.decay = 0.5  # reverb decay factor
        
    def apply_reverb(self, audio_data):
        """Apply reverb effect to audio data"""
        # Convert audio data to numpy array if needed
        audio_array = np.frombuffer(audio_data, dtype=np.float32)
        
        # Create reverb impulse response
        sr = 44100  # Sample rate
        delay_samples = int(self.reverb_delay * sr)
        impulse = np.zeros(delay_samples)
        impulse[0] = 1
        impulse[delay_samples-1] = self.decay
        
        # Apply convolution for reverb effect
        reverb_audio = signal.convolve(audio_array, impulse, mode='full')
        
        return reverb_audio.tobytes()

    def generate_audio_stream(self, text):
        """Generate audio stream with effects"""
        response = requests.post(
            "https://api.elevenlabs.io/v1/text-to-speech/aYnsKRtbVPhAk1n2Gz0r/stream",
            headers={
                "xi-api-key": self.elevenlabs_key,
                "Content-Type": "application/json",
            },
            json={
                "text": f'<break time="1.5s" /> {text}',
                "model_id": "eleven_turbo_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.25
                }
            },
            stream=True
        )

        # Process audio chunks with effects
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                # Apply effects to the chunk
                #processed_chunk = self.apply_reverb(chunk)
                #yield processed_chunk
                yield chunk

    def run(self, debug=False):
        """Run the Flask application"""
        self.app.run(debug=debug)

if __name__ == '__main__':
    server = RavenServer()
    server.run(debug=True)
