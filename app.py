from flask import Flask, render_template, redirect, url_for, session, request,jsonify,flash
import google.generativeai as genai
import os
from pymongo import MongoClient
from gridfs import GridFS
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from bson.objectid import ObjectId
from io import BytesIO  # To handle file data in memory

# Secure MongoDB URI (Move credentials to env variables)
#MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://arjun123:Arjun_123@cluster0.5wy9x.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)

SECRET_KEY = os.getenv('SECRET_KEY', 'default_fallback')
db = client['sacet']
collection = db['cse']
payCollection = db['uploads']
fs = GridFS(db)  # GridFS for storing files

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')  # Needed for session management

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signupForm', methods=['POST'])
def signupForm():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    # Validate input fields
    if not username or not email or not password:
        return render_template('home.html', err="All fields are required!")
    # Check if the email already exists
    existing_user = collection.find_one({"email": email})
    if existing_user:
        return render_template('home.html', err="Account already exists")
    # Hash the password and insert into the database
    hashed_password = generate_password_hash(password)
    collection.insert_one({"username": username, "email": email, "password": hashed_password})
    # Redirect to home page with success message
    return render_template('home.html', msg="Account created successfully")

@app.route('/loginForm', methods=['POST'])
def loginForm():
    email = request.form.get('email')
    password = request.form.get('password')
    # Look up the user by email
    user = collection.find_one({"email": email})
    # Verify password
    if user and check_password_hash(user["password"], password):
        session["username"] = user["username"]
        return redirect(url_for('dashboard'))  # Redirect to dashboard on success
    # If login fails, show error message
    flash("Incorrect login. Please check your email and password.", "error")
    return redirect(url_for('home'))  # Redirect to home page with a message

@app.route('/dashboard')
def dashboard():
    if "username" in session:
        # If user is logged in, render the dashboard page
        return render_template('dashboard.html')
    return redirect(url_for('home'))  # Redirect to login if not logged in

@app.route('/analyze')
def analyze():
    if "username" in session:
        return render_template('analyze.html')
    return redirect(url_for('home'))

@app.route('/prediction')
def prediction():
    if "username" in session:
        return render_template('prediction.html')
    return redirect(url_for('home'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if "username" not in session:
        return redirect(url_for('home'))
    
    # Check if a file is part of the request
    if 'file' not in request.files:
        flash("No file uploaded", "error")
        return redirect(url_for('dashboard'))
    
    file = request.files['file']
    
    # If no file is selected, flash an error message
    if file.filename == '':
        flash("No file selected", "error")
        return redirect(url_for('dashboard'))
    
    # Save the file using GridFS and store file info in the collection
    if file:
        file_id = fs.put(file, filename=file.filename, username=session["username"])
        payCollection.insert_one({"username": session["username"], "file_id": file_id})
        flash(f"File uploaded successfully: {file.filename}", "success")
        return redirect(url_for('dashboard'))



# Configure Gemini API
#GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyBuJqWhnbgC5bM0F47ybC-lrBHjXDFL2Fo')  # Replace with your Gemini API key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.json
        user_question = data.get('question')

        if not user_question:
            return jsonify({'answer': 'Please provide a question.'}), 400

        # Fetch the user's file from MongoDB
        user_file = payCollection.find_one({"username": session["username"]})
        if not user_file:
            return jsonify({'answer': 'No file found for the user. Please upload a file.'}), 404

        file_id = user_file["file_id"]
        file = fs.get(file_id)

        # Read the file based on its format
        try:
            if file.filename.endswith('.xlsx'):
                transaction_data = pd.read_excel(BytesIO(file.read())).to_string()
            elif file.filename.endswith('.csv'):
                transaction_data = pd.read_csv(BytesIO(file.read())).to_string()
            else:
                return jsonify({'answer': 'Unsupported file format. Please upload a .xlsx or .csv file.'}), 400
        except Exception as e:
            print(f"Error reading file: {e}")
            return jsonify({'answer': 'Error reading transaction data. Please check the file format.'}), 500

        # Combine the transaction data with the user's question
        prompt = f"The following is transaction data:\n{transaction_data}\n\nQuestion: {user_question}\nAnswer:"

        # Get the response from Gemini API
        response = model.generate_content(prompt)

        # Return the response to the frontend
        return jsonify({'answer': response.text})
    except Exception as e:
        print(f"Error: {e}")  # Log the error for debugging
        return jsonify({'answer': 'Sorry, something went wrong. Please try again.'}), 500

# Process data for pie charts
def process_data(df):
    # Convert the 'Amount' column to string (if it's not already)
    df['Amount'] = df['Amount'].astype(str)
    
    # Clean the 'Amount' column by removing '₹' and commas, then convert to numeric
    df['Amount'] = df['Amount'].str.replace('₹', '', regex=True).str.replace(',', '').astype(float)

    # Calculate total credit and debit amounts
    credit_data = df[df['Type'] == 'CREDIT']['Amount'].sum()
    debit_data = df[df['Type'] == 'DEBIT']['Amount'].sum()
    return {
        'credit': credit_data,
        'debit': debit_data
    }

@app.route('/data')
def get_data():
    try:
        # Fetch the user's file from MongoDB
        user_file = payCollection.find_one({"username": session["username"]})
        if not user_file:
            return jsonify({'error': 'No file found for the user. Please upload a file.'}), 404

        file_id = user_file["file_id"]
        file = fs.get(file_id)

        # Load and process the transaction data
        if file.filename.endswith('.xlsx'):
            df = pd.read_excel(BytesIO(file.read()))
        elif file.filename.endswith('.csv'):
            df = pd.read_csv(BytesIO(file.read()))
        else:
            return jsonify({'error': 'Unsupported file format. Please upload a .xlsx or .csv file.'}), 400

        print("Loaded DataFrame Columns:", df.columns.tolist())  # Debug: Print column names
        print("Sample Data:\n", df.head())  # Debug: Print sample data

        # Process data for pie charts
        data = process_data(df)
        print("Processed Data:", data)  # Debug: Print processed data

        # Return the data in the required format
        return jsonify(data)
    except FileNotFoundError as e:
        print("FileNotFoundError:", e)  # Debug: Print file not found error
        return jsonify({'error': str(e)}), 404
    except ValueError as e:
        print("ValueError:", e)  # Debug: Print value error
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print("Error:", e)  # Debug: Print any other error
        return jsonify({'error': 'Error processing transaction data. Please check the file format.'}), 500

@app.route('/logout')
def logout():
    session.pop("username", None)  # Remove user from session
    session.clear()  # Clears all session data
    flash("logout successfully.", "error")
    return redirect(url_for('home'))  # Redirect to login page

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1982, debug=True)