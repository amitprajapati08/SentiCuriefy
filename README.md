# SentiCuriefy - AI Powered Sentiment Analysis Platform

## Overview
SentiCuriefy is an end-to-end AI/ML-based web application designed to analyze user sentiments from textual data such as product reviews, feedback, and user inputs.

The system helps businesses and individuals understand customer opinions, detect emotions, and make data-driven decisions.

---

## Problem Statement
In today’s digital ecosystem, organizations receive large volumes of unstructured text data such as reviews, comments, and feedback.

Manual analysis of this data is:
- Time-consuming  
- Subjective  
- Inefficient  

SentiCuriefy addresses this challenge by providing automated sentiment and emotion analysis using Machine Learning and Natural Language Processing.

---

## Solution
The application processes user input text and:
- Classifies sentiment as Positive, Negative, or Neutral  
- Detects emotional tone from text  
- Generates visual insights such as sentiment distribution and word clouds  
- Stores and displays user analysis history  

---

## Key Features

### Sentiment Analysis
- Real-time sentiment prediction using NLP techniques  
- Dynamic handling of user input  

### Emotion Detection
- Identifies emotional context beyond basic sentiment classification  

### Dashboard and Analytics
- Sentiment distribution visualization  
- Word cloud generation  
- Historical tracking of user activity  

### User Authentication
- Secure login and signup functionality  
- Personalized dashboard  

### Product Review Analysis
- Analyze large sets of customer reviews  
- Identify trends and overall sentiment  

---

## System Architecture

User Input → Text Preprocessing → NLP Processing → ML Model → Prediction → Visualization → Dashboard

---

## Tech Stack

### Backend
- Python  
- Flask  

### Machine Learning / NLP
- Text preprocessing (tokenization, stopword removal)  
- Sentiment classification models  
- Emotion detection logic  

### Frontend
- HTML  
- CSS  
- Jinja Templates  

### Database
- SQLite (or configurable database)

---

## Project Structure

SentiCuriefy/  
│── routes/        API routes and controllers  
│── services/      NLP and ML logic  
│── models/        Database models  
│── templates/     Frontend pages  
│── static/        CSS, images, visualizations  
│── utils/         Helper functions  
│── Data/          Dataset  
│── Notebook/      Model experimentation  
│── app.py         Main application entry point  

---

## How to Run Locally

git clone https://github.com/amitprajapati08/SentiCuriefy.git  
cd SentiCuriefy  

python -m venv env  
env\Scripts\activate  

pip install -r requirements.txt  

python app.py  

---

## Example Use Cases
- Product review analysis  
- Customer feedback evaluation  
- Social media sentiment tracking  
- Business intelligence and decision support  

---

## Future Enhancements
- Cloud deployment (Render, AWS, etc.)  
- Integration of transformer-based models (BERT, etc.)  
- Real-time API integration  
- Multilingual sentiment analysis  
- Advanced analytics dashboard  

---

## Author
Amit Prajapat  
AI/ML Developer 

---

## Conclusion
SentiCuriefy converts unstructured textual data into meaningful insights, enabling smarter and data-driven decision-making using AI and NLP.
