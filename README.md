# Weather AI SaaS - Homework #1

A cloud-based SaaS application for weather data retrieval and AI-powered suggestions.

## Functionality
 **Weather data**: integrated with Visual Crossing API for meteorological metrics.
 **AI recommendations**: uses Google Gemini 2.5 Flash to generate evening plans based on weather conditions.

## Project Structure
 *weather_app.py*: main Flask application for EC2 deployment.
 *rsa_api_test_v3.ipynb*: development and testing environment.

## Setup and Deployment
1. Install dependencies: *pip install requests flask*.
2. Configure **RSA_KEY** and **GEMINI_KEY** in the application code.
3. Deploy on EC2 and start the server using uWSGI.
4. Access the endpoint via POST request.
