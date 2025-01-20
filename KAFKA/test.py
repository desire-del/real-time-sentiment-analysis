import requests
import csv
from datetime import datetime

# Étape 1 : Ajouter votre Bearer Token
BEARER_TOKEN = ""

# Étape 2 : Configurer l'en-tête d'autorisation
HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

# Étape 3 : Fonction pour récupérer des tweets avec tous les champs disponibles
def fetch_all_tweet_fields(query, max_results=10):
    """
    Fetch tweets with all possible fields using the Twitter API v2.
    
    :param query: The search keyword or hashtag.
    :param max_results: Maximum number of tweets to retrieve (up to 100 per request).
    :return: List of tweets with all available fields.
    """
    url = "https://api.twitter.com/2/tweets/search/recent"
    params = {
        "query": query,
        "max_results": max_results,
        "tweet.fields": "id,text,created_at,lang,source,public_metrics,geo,conversation_id,reply_settings",
        "user.fields": "id,username,name,verified,profile_image_url,location",
        "expansions": "author_id"
    }

    response = requests.get(url, headers=HEADERS, params=params)
    
    if response.status_code == 200:
        data = response.json()
        tweets = data.get("data", [])
        includes = data.get("includes", {}).get("users", [])
        users = {user["id"]: user for user in includes}
        
        # Attach user details to each tweet
        for tweet in tweets:
            author_id = tweet.get("author_id")
            tweet["author"] = users.get(author_id, {})
        
        return tweets
    else:
        print(f"Error {response.status_code}: {response.json()}")
        return []

# Étape 4 : Fonction pour sauvegarder les tweets avec tous les champs dans un CSV
def save_to_csv_all_fields(tweets, filename="tweets_all_fields.csv"):
    """
    Save tweets with all available fields to a CSV file.
    
    :param tweets: List of tweets with all fields.
    :param filename: Name of the CSV file to save.
    """
    # Collect all unique keys across tweets
    all_keys = set()
    for tweet in tweets:
        all_keys.update(tweet.keys())
        all_keys.update(tweet.get("author", {}).keys())
    
    # Write to CSV
    with open(filename, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=sorted(all_keys))
        writer.writeheader()
        
        for tweet in tweets:
            row = tweet.copy()
            author = row.pop("author", {})
            row.update(author)  # Merge author fields with tweet fields
            writer.writerow(row)

    print(f"All tweets with fields have been saved to: {filename}")

# Étape 5 : Exemple d'utilisation
if __name__ == "__main__":
    keywords = [
    # Général sur l'IA
    "Artificial Intelligence",
    "AI",
    "Machine Learning",
    "Deep Learning",
    "Neural Networks",
    "Generative AI",
    "Natural Language Processing",
    "NLP",
    "Computer Vision",
    "ChatGPT",
    "OpenAI",
    "AI Ethics",
    "Transformers",
    "Reinforcement Learning",
    "GANs",
    "AI Research",
    "AI for Good",
    "AI Tools",
    "Explainable AI",
    "XAI",
    "AI in Healthcare",
    "AI in Education",
    
    # Outils et frameworks
    "PyTorch",
    "TensorFlow",
    "Keras",
    "Hugging Face",
    "Scikit-learn",
    "OpenCV",
    "NLTK",
    "SpaCy",
    "FastAI",
    "ONNX",

    # Applications et tendances
    "AI-powered",
    "AI Automation",
    "AI Startups"
]
  # The search keyword or hashtag
    num_tweets = 100  # Maximum number of tweets to retrieve
    
    # Fetch tweets with all fields
    tweets = fetch_all_tweet_fields(" OR ".join(keywords)+" lang:en", num_tweets)
    
    # Save tweets to a CSV file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"tweets_all_fields_{timestamp}.csv"
    save_to_csv_all_fields(tweets, csv_filename)
