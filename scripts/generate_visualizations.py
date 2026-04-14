import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from wordcloud import WordCloud
import os
import json
import matplotlib
matplotlib.use('Agg')  # Use Agg backend to avoid tkinter issues

def generate_plots():
    # Create static/plots directory if it doesn't exist
    os.makedirs('static/plots', exist_ok=True)
    
    try:
        # Load data
        data = pd.read_csv("Data/Dataset.csv")
        
        # Process sentiment using VADER
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        analyzer = SentimentIntensityAnalyzer()
        
        # Calculate sentiment scores
        data['review_text'] = data['review_text'].astype(str)
        scores = []
        for text in data['review_text']:
            score = analyzer.polarity_scores(text)
            scores.append(score['compound'])
        
        data['sentiment_score'] = scores
        data['sentiment'] = pd.cut(data['sentiment_score'], 
                                 bins=[-1, -0.05, 0.05, 1], 
                                 labels=['Negative', 'Neutral', 'Positive'])
        
        # Generate wordcloud
        plt.figure(figsize=(10,10))
        tweet_All = " ".join(str(review) for review in data['review_text'])
        wordcloud = WordCloud(max_font_size=50, max_words=100, background_color="black").generate(tweet_All)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.savefig('static/plots/wordcloud.png')
        plt.close()
        
        # Sentiment distribution
        plt.figure(figsize=(12,6))
        data['sentiment'].value_counts().plot(kind='bar')
        plt.title('Sentiment Distribution')
        plt.xlabel('Sentiment')
        plt.ylabel('Count')
        plt.tight_layout()
        plt.savefig('static/plots/sentiment_dist.png')
        plt.close()

        # Basic statistics
        stats = {
            'total_reviews': len(data),
            'positive_pct': len(data[data['sentiment'] == 'Positive']) / len(data) * 100,
            'negative_pct': len(data[data['sentiment'] == 'Negative']) / len(data) * 100,
            'neutral_pct': len(data[data['sentiment'] == 'Neutral']) / len(data) * 100,
            'avg_score': data['sentiment_score'].mean()
        }
        
        with open('static/plots/stats.json', 'w') as f:
            json.dump(stats, f)
            
    except Exception as e:
        print(f"Error generating plots: {str(e)}")
        # Create empty stats on error
        stats = {
            'total_reviews': 0,
            'positive_pct': 0,
            'negative_pct': 0,
            'neutral_pct': 0,
            'avg_score': 0,
            'error': str(e)
        }
        with open('static/plots/stats.json', 'w') as f:
            json.dump(stats, f)

if __name__ == "__main__":
    generate_plots()
