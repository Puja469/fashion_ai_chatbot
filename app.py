from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
RASA_API_URL = os.getenv('RASA_API_URL', 'http://localhost:5006/webhooks/rest/webhook')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        if not request.json:
            return jsonify({
                'status': 'error',
                'message': 'Invalid JSON data received.'
            }), 400
            
        user_message = request.json.get('message')
        sender_id = request.json.get('sender', 'user')
        
        if not user_message or user_message.strip() == '':
            return jsonify({
                'status': 'error',
                'message': 'Please enter a message.'
            }), 400
        
        # Send message to Rasa
        payload = {
            'sender': sender_id,
            'message': user_message.strip()
        }
        
        response = requests.post(RASA_API_URL, json=payload, timeout=15)
        
        if response.status_code == 200:
            bot_responses = response.json()
            
            # Format responses
            formatted_responses = []
            for bot_response in bot_responses:
                formatted_response = {
                    'text': bot_response.get('text', ''),
                    'image': bot_response.get('image'),
                    'buttons': bot_response.get('buttons', []),
                    'timestamp': datetime.now().strftime('%H:%M')
                }
                formatted_responses.append(formatted_response)
            
            return jsonify({
                'status': 'success',
                'responses': formatted_responses
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Rasa server returned status {response.status_code}. Please make sure the Rasa server is running.'
            }), 500
            
    except requests.exceptions.ConnectionError:
        return jsonify({
            'status': 'error', 
            'message': 'Cannot connect to Rasa server. Please make sure the Rasa server is running on http://localhost:5006'
        }), 500
    except requests.exceptions.Timeout:
        return jsonify({
            'status': 'error',
            'message': 'Request timed out. Please try again.'
        }), 500
    except requests.exceptions.RequestException as e:
        return jsonify({
            'status': 'error', 
            'message': f'Network error: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Something went wrong: {str(e)}'
        }), 500

@app.route('/health')
def health():
    try:
        # Check if Rasa server is running
        response = requests.get('http://localhost:5006/status', timeout=5)
        rasa_status = 'connected' if response.status_code == 200 else 'error'
    except:
        rasa_status = 'disconnected'
    
    return jsonify({
        'status': 'healthy', 
        'service': 'Fashion Chatbot Web Interface',
        'rasa_status': rasa_status
    })

@app.route('/status')
def status():
    return jsonify({
        'status': 'running',
        'service': 'Fashion Chatbot Web Interface',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("🚀 Starting Fashion Chatbot Web Interface...")
    print("📱 Web interface will be available at: http://localhost:5050")
    print("🤖 Make sure Rasa server is running on: http://localhost:5006")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5050)