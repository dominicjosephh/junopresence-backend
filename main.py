from flask import Flask, request, jsonify, send_from_directory
import openai
import whisper
import os
import uuid
import requests
import json  # Required for response_class workaround

app = Flask(__name__)  # ← This MUST come first

model = None
session_history = {}
