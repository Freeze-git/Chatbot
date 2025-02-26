from flask import Flask, render_template, request, jsonify # type: ignore
import google.generativeai as genai # type: ignore
import json
import os

app = Flask(__name__)

# Enable CORS
from flask_cors import CORS # type: ignore
CORS(app)

# Configure Google Gemini AI API
genai.configure(api_key="Your-API-here")

# File to store patient data
DATA_FILE = "patient_data.json"

# Ensure the file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit_form', methods=['POST'])
def submit_form():
    try:
        # Ensure JSON data is received
        if not request.is_json:
            print("❌ Error: Request is not JSON")
            return jsonify({"error": "Content-Type must be application/json"}), 400

        data = request.get_json()  # Get JSON data from frontend
        print("✅ Received Data:", data)  # Debugging

        # Ensure essential fields exist
        if not all(key in data for key in ["name", "age", "gender", "symptoms"]):
            print("❌ Error: Missing fields in request")
            return jsonify({"error": "Missing required fields"}), 400

        # Save data to file
        with open(DATA_FILE, "a") as file:
            json.dump(data, file)
            file.write("\n")

        print("✅ Patient data saved successfully!")
        return jsonify({"redirect": "/recommendations"})

    except Exception as e:
        print(f"❌ Server Error: {str(e)}")  # Print error to console
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/recommendations', methods=['GET'])
def recommendations():
    return render_template('recommendations.html')

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    data = request.json
    symptoms = data.get("symptoms", "")

    # AI Prompt
    prompt = f"""
    The patient has the following symptoms: {symptoms}.
    Provide a detailed analysis, possible diseases, preventive measures, and recommended medications.
    """

    try:
       model = genai.GenerativeModel("gemini-1.5-pro")  # ✅ Correct model name
       response = model.generate_content(prompt)

       if response:
            return jsonify({"recommendation": response.text})
       else:
            return jsonify({"recommendation": "Unable to generate a response."})
    except Exception as e:
        return jsonify({"recommendation": f"Error: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
