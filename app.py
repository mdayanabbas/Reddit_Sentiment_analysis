# main.py
import praw
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import json
import os
from datetime import datetime, timedelta
import numpy as np
from wordcloud import WordCloud
import base64
from io import BytesIO
import nltk
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# Initialize Reddit API client
reddit = praw.Reddit(client_id="_oxIeTUuyDiPRWzq-qeVZQ",         # your client id
    client_secret="bcJjNvJ-2Bt0E82IeqdoLWnlx5U_KQ",      # your client secret
    user_agent="Abbas")        # your user agent


async def collect_reddit_data(subreddit_name: str, limit: int = 2000) -> List[dict]:
    subreddit = reddit.subreddit(subreddit_name)
    posts = []
    
    # Collect from different time periods to get more posts
    time_filters = ['day', 'week', 'month', 'year']
    
    for time_filter in time_filters:
        for post in subreddit.top(time_filter=time_filter, limit=limit//len(time_filters)):
            posts.append({
                'title': post.title,
                'text': post.selftext,
                'score': post.score,
                'created_utc': datetime.fromtimestamp(post.created_utc),
                'num_comments': post.num_comments
            })
    
    return posts

def analyze_sentiment(text: str) -> Dict:
    blob = TextBlob(text)
    vader = SentimentIntensityAnalyzer()
    vader_scores = vader.polarity_scores(text)
    return {
        'polarity': blob.sentiment.polarity,
        'subjectivity': blob.sentiment.subjectivity,
        'compound': vader_scores['compound'],
        'pos': vader_scores['pos'],
        'neu': vader_scores['neu'],
        'neg': vader_scores['neg']
    }

def create_visualizations(df: pd.DataFrame) -> Dict:
    # 1. Sentiment Distribution Plot
    fig_sentiment = px.histogram(
        df, x='sentiment_polarity',
        title='Sentiment Distribution',
        labels={'sentiment_polarity': 'Sentiment Score'},
        template='plotly_white'
    )
    
    # 2. Sentiment over Time
    df['date'] = pd.to_datetime(df['created_utc']).dt.date
    time_sentiment = df.groupby('date')['sentiment_polarity'].mean().reset_index()
    fig_time = px.line(
        time_sentiment,
        x='date',
        y='sentiment_polarity',
        title='Sentiment Trend Over Time',
        template='plotly_white'
    )
    
    # 3. Radar Chart (Sentiment Components)
    fig_radar = go.Figure(data=go.Scatterpolar(
        r=[df['sentiment_polarity'].mean(), df['sentiment_subjectivity'].mean(), 
           df['sentiment_pos'].mean(), df['sentiment_neu'].mean(), df['sentiment_neg'].mean()],
        theta=['Polarity', 'Subjectivity', 'Positive', 'Neutral', 'Negative'],
        fill='toself'
    ))
    fig_radar.update_layout(title='Sentiment Components')
    
    # 4. Engagement Heatmap
    fig_heatmap = px.density_heatmap(
        df, x='sentiment_polarity', y='score',
        title='Engagement vs Sentiment',
        template='plotly_white'
    )
    
    # 5. Emotion Flow
    fig_emotion = px.line(
        df.sort_values('created_utc'), 
        x='created_utc', 
        y='sentiment_polarity',
        title='Emotion Flow Over Time',
        template='plotly_white'
    )
    
    # 6. Word Cloud
    text = ' '.join(df['title'] + ' ' + df['text'])
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    img = wordcloud.to_image()
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return {
        'sentiment_dist': fig_sentiment.to_json(),
        'time_analysis': fig_time.to_json(),
        'radar_chart': fig_radar.to_json(),
        'engagement_heatmap': fig_heatmap.to_json(),
        'emotion_flow': fig_emotion.to_json(),
        'wordcloud': img_str
    }

@app.get("/analyze/{subreddit}")
async def analyze_subreddit(subreddit: str, limit: int = 2000):
    # Collect data
    posts = await collect_reddit_data(subreddit, limit)
    
    # Create DataFrame
    df = pd.DataFrame(posts)
    
    # Analyze sentiment
    sentiments = [analyze_sentiment(text) for text in df['title'] + ' ' + df['text']]
    df['sentiment_polarity'] = [s['polarity'] for s in sentiments]
    df['sentiment_subjectivity'] = [s['subjectivity'] for s in sentiments]
    df['sentiment_compound'] = [s['compound'] for s in sentiments]
    df['sentiment_pos'] = [s['pos'] for s in sentiments]
    df['sentiment_neu'] = [s['neu'] for s in sentiments]
    df['sentiment_neg'] = [s['neg'] for s in sentiments]
    
    # Generate visualizations
    visualizations = create_visualizations(df)
    
    # Calculate statistics
    stats = {
        "subreddit": subreddit,
        "average_sentiment": df['sentiment_polarity'].mean(),
        "number_of_posts": len(posts),
        "sentiment_breakdown": {
            "positive": len(df[df['sentiment_polarity'] > 0.1]),
            "neutral": len(df[(df['sentiment_polarity'] >= -0.1) & (df['sentiment_polarity'] <= 0.1)]),
            "negative": len(df[df['sentiment_polarity'] < -0.1])
        },
        "visualizations": visualizations
    }
    
    return stats

@app.get("/", response_class=HTMLResponse)
async def get_html():
    return """
    <html>
        <head>
            <title>Reddit Sentiment Analysis Dashboard by Abbas</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
            <style>
                :root {
                    --primary-color: #FF4500;
                    --secondary-color: #1A1A1B;
                    --background-color: #DAE0E6;
                    --card-background: #FFFFFF;
                    --text-color: #1A1A1B;
                    --border-radius: 8px;
                    --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }

                body { 
                    font-family: 'Inter', sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: var(--background-color);
                    color: var(--text-color);
                }

                .container {
                    max-width: 1400px;
                    margin: 0 auto;
                    padding: 20px;
                }

                .header {
                    background: var(--card-background);
                    padding: 20px;
                    border-radius: var(--border-radius);
                    margin-bottom: 20px;
                    box-shadow: var(--shadow);
                }

                .header h1 {
                    color: var(--primary-color);
                    margin: 0;
                    font-size: 2.5em;
                }

                .input-group {
                    display: flex;
                    gap: 10px;
                    margin: 20px 0;
                }

                input {
                    flex: 1;
                    padding: 12px 20px;
                    border: 2px solid #E5E5E5;
                    border-radius: var(--border-radius);
                    font-size: 16px;
                    transition: all 0.3s ease;
                }

                input:focus {
                    border-color: var(--primary-color);
                    outline: none;
                }

                button {
                    background-color: var(--primary-color);
                    color: white;
                    border: none;
                    padding: 12px 30px;
                    border-radius: var(--border-radius);
                    cursor: pointer;
                    font-weight: 600;
                    transition: all 0.3s ease;
                }

                button:hover {
                    background-color: #FF5722;
                    transform: translateY(-1px);
                }

                .grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
                    gap: 20px;
                    margin-top: 20px;
                }

                .chart-container {
                    background: var(--card-background);
                    border-radius: var(--border-radius);
                    padding: 20px;
                    box-shadow: var(--shadow);
                    transition: all 0.3s ease;
                }

                .chart-container:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
                }

                .chart-container h2 {
                    color: var(--secondary-color);
                    margin-top: 0;
                    font-size: 1.5em;
                    border-bottom: 2px solid #E5E5E5;
                    padding-bottom: 10px;
                }

                .chart { 
                    width: 100%; 
                    height: 400px;
                }

                .stats {
                    background: var(--card-background);
                    border-radius: var(--border-radius);
                    padding: 20px;
                    margin: 20px 0;
                    box-shadow: var(--shadow);
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                }

                .stat-card {
                    padding: 15px;
                    background: #F8F9FA;
                    border-radius: var(--border-radius);
                    text-align: center;
                }

                .stat-value {
                    font-size: 24px;
                    font-weight: 600;
                    color: var(--primary-color);
                }

                .stat-label {
                    font-size: 14px;
                    color: #666;
                    margin-top: 5px;
                }

                .loading {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(255, 255, 255, 0.9);
                    display: none;
                    justify-content: center;
                    align-items: center;
                    z-index: 1000;
                }

                .loading-spinner {
                    border: 4px solid #f3f3f3;
                    border-top: 4px solid var(--primary-color);
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    animation: spin 1s linear infinite;
                }

                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }

                .error-message {
                    background: #FFE5E5;
                    color: #D32F2F;
                    padding: 15px;
                    border-radius: var(--border-radius);
                    margin: 10px 0;
                    display: none;
                }

                @media (max-width: 768px) {
                    .grid {
                        grid-template-columns: 1fr;
                    }
                    
                    .input-group {
                        flex-direction: column;
                    }
                    
                    .header h1 {
                        font-size: 2em;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                <h1>
                    Reddit Sentiment Analysis Dashboard by ABBAS 
                    <a href="https://github.com/mdayanabbas" target="_blank">
                        <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" 
                            alt="GitHub" 
                            width="60" 
                            style="vertical-align:middle; margin-left: 200px;"> <!-- Adjust margin as needed -->
                    </a>
                    <a href = "https://x.com/Stat_Sawyer" target = "_blank">    
                        <img src="https://storage.googleapis.com/a1aa/image/MilQTFJW56qBEtYb0p9Ffujc9UmBb6uYpewImYfpgo66pfXOB.jpg" 
                            alt="Twitter" 
                            width="80" 
                            style="vertical-align:middle; margin-left: 10px;"> <!-- Adjust margin as needed -->
                    </a>
                </h1>
                    <div class="input-group">
                        <input type="text" id="subreddit" placeholder="Enter subreddit name (e.g., 'python', 'news')">
                        <button onclick="analyzeSentiment()">Analyze</button>
                    </div>
                    <div class="error-message" id="error-message"></div>
                </div>

                <div class="stats" id="stats"></div>
                
                <div class="grid">
                    <div class="chart-container">
                        <h2>Sentiment Distribution</h2>
                        <div class="chart" id="sentiment_dist"></div>
                    </div>
                    
                    <div class="chart-container">
                        <h2>Time Analysis</h2>
                        <div class="chart" id="time_analysis"></div>
                    </div>
                    
                    <div class="chart-container">
                        <h2>Sentiment Components</h2>
                        <div class="chart" id="radar_chart"></div>
                    </div>
                    
                    <div class="chart-container">
                        <h2>Engagement Analysis</h2>
                        <div class="chart" id="engagement_heatmap"></div>
                    </div>
                    
                    <div class="chart-container">
                        <h2>Emotion Flow</h2>
                        <div class="chart" id="emotion_flow"></div>
                    </div>
                    
                    <div class="chart-container">
                        <h2>Word Cloud</h2>
                        <div class="wordcloud" id="wordcloud"></div>
                    </div>
                </div>
            </div>

            <div class="loading" id="loading">
                <div class="loading-spinner"></div>
            </div>
            
            <script>
                async function analyzeSentiment() {
                    const subreddit = document.getElementById('subreddit').value;
                    const loading = document.getElementById('loading');
                    const errorMessage = document.getElementById('error-message');
                    
                    if (!subreddit) {
                        errorMessage.textContent = 'Please enter a subreddit name';
                        errorMessage.style.display = 'block';
                        return;
                    }
                    
                    loading.style.display = 'flex';
                    errorMessage.style.display = 'none';
                    
                    try {
                        const response = await fetch(`/analyze/${subreddit}`);
                        if (!response.ok) {
                            throw new Error(`Error: ${response.statusText}`);
                        }
                        const data = await response.json();
                        
                        // Update stats
                        updateStats(data);
                        
                        // Update charts
                        updateChart('sentiment_dist', data.visualizations.sentiment_dist);
                        updateChart('time_analysis', data.visualizations.time_analysis);
                        updateChart('radar_chart', data.visualizations.radar_chart);
                        updateChart('engagement_heatmap', data.visualizations.engagement_heatmap);
                        updateChart('emotion_flow', data.visualizations.emotion_flow);
                        
                        // Update word cloud
                        if (data.visualizations.wordcloud) {
                            document.getElementById('wordcloud').innerHTML = `
                                <img src="data:image/png;base64,${data.visualizations.wordcloud}" alt="Word Cloud" style="width:100%;height:auto;">
                            `;
                        } else {
                            document.getElementById('wordcloud').innerHTML = 'Word cloud not available';
                        }
                    } catch (error) {
                        errorMessage.textContent = `Error analyzing subreddit: ${error.message}`;
                        errorMessage.style.display = 'block';
                    } finally {
                        loading.style.display = 'none';
                    }
                }

                function updateStats(data) {
                    const stats = document.getElementById('stats');
                    stats.innerHTML = `
                        <div class="stat-card">
                            <div class="stat-value">${data.average_sentiment.toFixed(3)}</div>
                            <div class="stat-label">Average Sentiment</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${data.number_of_posts}</div>
                            <div class="stat-label">Total Posts</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${data.sentiment_breakdown.positive}</div>
                            <div class="stat-label">Positive Posts</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${data.sentiment_breakdown.negative}</div>
                            <div class="stat-label">Negative Posts</div>
                        </div>
                    `;
                }

                function updateChart(chartId, chartData) {
                    if (chartData) {
                        try {
                            Plotly.newPlot(chartId, JSON.parse(chartData));
                        } catch (error) {
                            console.error(`Error updating chart ${chartId}:`, error);
                            document.getElementById(chartId).innerHTML = 'Chart data not available';
                        }
                    } else {
                        document.getElementById(chartId).innerHTML = 'Chart data not available';
                    }
                }
            </script>
        </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)