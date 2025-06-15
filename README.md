# MoneyMap

MoneyMap is a web-based financial management and analysis tool built with Flask, Bootstrap, and MongoDB. It allows users to sign up, log in, upload their financial transaction files (CSV or Excel), and perform analysis and predictions on their data using an AI-powered Gemini API integration.

> **Hackathon Project:** This project was developed as part of a **MakeSkilled** hackathon.

## Features

- **User Authentication:** Secure sign-up, login, and logout functionality.
- **File Upload:** Upload financial files using a modern, interactive file upload interface.
- **Toast Notifications:** Displays Bootstrap toast notifications (centered on the screen) for both successful file uploads and errors.
- **Financial Analysis & Predictions:** Once a file is successfully uploaded, the Analyze and Predictions buttons are enabled to allow further data processing.
- **Responsive Design:** Includes an off-canvas mobile navigation menu and responsive layouts.

## Technologies Used

- **Backend:** Python 3 and Flask
- **Database:** MongoDB with GridFS for file storage
- **Frontend:** Bootstrap 5, JavaScript, and custom CSS
- **API Integration:** Google Gemini API (for generating financial insights)
- **Data Processing:** Pandas

## Installation

### Prerequisites

- Python 3.7 or higher
- MongoDB instance (local or hosted, e.g., MongoDB Atlas)
- [Virtualenv](https://virtualenv.pypa.io/en/latest/) (recommended)

# Usage
- **Sign Up / Log In**:
   Create an account or log in using the home page.

- **Dashboard**:
After logging in, navigate to the dashboard where you can upload your financial transaction file.

- The file upload area supports CSV and Excel (.xlsx) files.
- After clicking the Upload button, a centered Bootstrap toast will appear showing a success or error message.
- If the file is uploaded successfully, the Analyze and Predictions buttons are enabled for further actions.
# Analysis & Predictions:
Click on the Analyze or Predictions buttons to view detailed insights and predictive analysis of your financial data.

# Customization
- **Styling**: Modify the styles in static/css/styles.css or directly in your HTML templates.
- **JavaScript**: Additional interactivity can be added or modified in static/js/main.js.
- **Backend Logic**: Modify app.py to customize routes, file processing, or integrate additional APIs.
# Troubleshooting
- **File Upload Issues**:
Ensure that you are uploading a supported file format (CSV or Excel). Appropriate error messages will be flashed if the file is missing or the format is unsupported.

- **Database Connection**:
Double-check your MONGO_URI in the environment variables if you encounter connection issues.

- **API Issues**:
Verify that your Gemini API key is valid and that your API quota has not been exceeded.

# Acknowledgements
Team **Crafty Coders** for their contributions during the hackathon.

# outputs
- home page
  ![Home Page](output/1.png)
- signup Form
  ![signup Form](output/2.png)
- login From
  ![login Form](output/3.png)
- dashboard
  ![dashboard](output/4.png)
- upload
  ![upload](output/5.png)
  **upload successful**
  ![upload](output/6.png)
- analyze
  ![analyze](output/7.png)
- ai chart
  ![chart](output/8.png)
- log out
  ![log out](output/9.png)
- mongoDB
  ![mongoDB](output/10.png)
  **user uploaded dataset**
  ![mongoDB](output/11.png)
