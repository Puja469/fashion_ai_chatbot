#!/usr/bin/env python3
"""
Fashion Chatbot Startup Script
This script starts both the Rasa server and the web interface.
"""

import subprocess
import time
import sys
import os
import signal
import requests
from threading import Thread

class ChatbotStarter:
    def __init__(self):
        self.rasa_process = None
        self.web_process = None
        self.running = True
        
    def start_rasa_server(self):
        """Start the Rasa server"""
        print("🤖 Starting Rasa server...")
        try:
            # Start Rasa server with actions
            self.rasa_process = subprocess.Popen([
                'rasa', 'run', '--enable-api', '--cors', '*', '--port', '5005'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait a bit for Rasa to start
            time.sleep(5)
            
            # Check if Rasa is running
            try:
                response = requests.get('http://localhost:5005/status', timeout=5)
                if response.status_code == 200:
                    print("✅ Rasa server is running on http://localhost:5005")
                    return True
                else:
                    print("❌ Rasa server failed to start properly")
                    return False
            except:
                print("❌ Rasa server failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Error starting Rasa server: {e}")
            return False
    
    def start_web_interface(self):
        """Start the web interface"""
        print("🌐 Starting web interface...")
        try:
            # Start Flask web interface
            self.web_process = subprocess.Popen([
                sys.executable, 'app.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait a bit for web interface to start
            time.sleep(3)
            
            # Check if web interface is running
            try:
                response = requests.get('http://localhost:5050/status', timeout=5)
                if response.status_code == 200:
                    print("✅ Web interface is running on http://localhost:5050")
                    return True
                else:
                    print("❌ Web interface failed to start properly")
                    return False
            except:
                print("❌ Web interface failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Error starting web interface: {e}")
            return False
    
    def start_actions_server(self):
        """Start the Rasa actions server in a separate thread"""
        def run_actions():
            print("⚡ Starting Rasa actions server...")
            try:
                subprocess.run(['rasa', 'run', 'actions'], check=True)
            except subprocess.CalledProcessError as e:
                print(f"❌ Actions server error: {e}")
            except KeyboardInterrupt:
                print("🛑 Actions server stopped")
        
        actions_thread = Thread(target=run_actions, daemon=True)
        actions_thread.start()
        time.sleep(2)  # Give actions server time to start
    
    def wait_for_services(self):
        """Wait for both services to be ready"""
        print("⏳ Waiting for services to be ready...")
        
        # Wait for Rasa
        for i in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get('http://localhost:5005/status', timeout=2)
                if response.status_code == 200:
                    break
            except:
                pass
            time.sleep(1)
        
        # Wait for web interface
        for i in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get('http://localhost:5050/status', timeout=2)
                if response.status_code == 200:
                    break
            except:
                pass
            time.sleep(1)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n🛑 Shutting down services...")
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Clean up processes"""
        if self.rasa_process:
            print("🛑 Stopping Rasa server...")
            self.rasa_process.terminate()
            self.rasa_process.wait()
        
        if self.web_process:
            print("🛑 Stopping web interface...")
            self.web_process.terminate()
            self.web_process.wait()
    
    def run(self):
        """Main run method"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("🚀 Fashion Chatbot Startup")
        print("=" * 50)
        
        # Start actions server first
        self.start_actions_server()
        
        # Start Rasa server
        if not self.start_rasa_server():
            print("❌ Failed to start Rasa server. Exiting.")
            return
        
        # Start web interface
        if not self.start_web_interface():
            print("❌ Failed to start web interface. Exiting.")
            return
        
        # Wait for services to be ready
        self.wait_for_services()
        
        print("\n🎉 Fashion Chatbot is ready!")
        print("=" * 50)
        print("📱 Web Interface: http://localhost:5050")
        print("🤖 Rasa Server: http://localhost:5005")
        print("⚡ Actions Server: http://localhost:5055")
        print("=" * 50)
        print("💡 Try asking: 'I need fashion advice' or 'What should I wear?'")
        print("🛑 Press Ctrl+C to stop all services")
        print("=" * 50)
        
        # Keep running
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Received interrupt signal")
        finally:
            self.cleanup()

if __name__ == "__main__":
    starter = ChatbotStarter()
    starter.run() 