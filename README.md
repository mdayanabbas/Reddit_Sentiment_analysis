# Reddit Sentiment Analysis

![Reddit Sentiment Analysis](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Overview

The **Reddit Sentiment Analysis** application analyzes comments from Reddit posts to determine the sentiment expressed by users. Leveraging Natural Language Processing (NLP) techniques, this project provides insights into community opinions across various topics, enhancing understanding of public sentiment.

## Features

- **Sentiment Classification**: Classifies Reddit comments into positive, negative, or neutral sentiments.
- **Data Visualization**: Displays sentiment trends and distributions using interactive graphs.
- **User-Friendly Interface**: Designed for intuitive user interactions and ease of use.

## Technologies Used

- **Python**: Programming language for the backend.
- **Flask**: Web framework for building the web application.
- **Scikit-learn**: Library for machine learning and model building.
- **NLTK**: Toolkit for natural language processing.
- **Pandas**: Data manipulation and analysis library.
- **Matplotlib/Seaborn**: Libraries for data visualization.
- **Docker**: Containerization technology for streamlined deployment.

## Installation

Follow the steps below to set up the project locally:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/mdayanabbas/Reddit_Sentiment_analysis.git
   cd Reddit_Sentiment_analysis
Create a virtual environment (recommended):

bash
Copy code
python -m venv venv
source venv/bin/activate  # Use `venv\Scripts\activate` on Windows
Install the required packages:

bash
Copy code
pip install -r requirements.txt
Set up environment variables: Ensure you have the following environment variables set in your .env file or system:

CLIENT_ID: Your Reddit API client ID.
CLIENT_SECRET: Your Reddit API client secret.
USER_AGENT: Your Reddit API user agent.
Run the application:

bash
Copy code
python app.py
## Usage
Open your web browser and navigate to http://localhost:5000.
Enter the Reddit post URL or subreddit you wish to analyze.
View the resulting sentiment analysis and visualizations.
## Deployment
The application is deployed on Render. You can access it [here](https://reddit-sentiment-analysis-pyip.onrender.com/).

## Contributing
Contributions are welcome! If you'd like to contribute to this project, please follow these steps:

Fork the repository.
Create a new branch for your feature or bug fix.
Make your changes and commit them.
Push your branch to your forked repository.
Submit a pull request for review.
License
This project is licensed under the MIT License. See the LICENSE file for more details.
