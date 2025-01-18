import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from pymongo import MongoClient

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
print(client.list_database_names())
db = client["tweetDB"]
collection = db["tweetCollection"]

# Charger les données de MongoDB dans un DataFrame
def load_data():
    data = list(collection.find())
    df = pd.DataFrame(data)
    print(df.shape)
    return df

# Créer l'application Dash
app = dash.Dash(__name__)

# Styles CSS pour rendre le tableau de bord attrayant
app.title = "Twitter Analytics Dashboard"
app.css.config.serve_locally = True

# Mise en page de l'application
app.layout = html.Div(
    style={
        "fontFamily": "Arial, sans-serif",
        "backgroundColor": "#000000",  # Fond noir pour le thème de X
        "color": "#FFFFFF",  # Texte en blanc
        "padding": "20px",
        "margin": "auto",
    },
    children=[
        html.H1(
            "Twitter Analytics Dashboard",
            style={"textAlign": "center", "color": "#FFFFFF", "marginBottom": "20px"},  # Titre en blanc
        ),

        # Row 1: Histogramme des sentiments
        html.Div(
            style={"display": "flex", "justifyContent": "space-between", "marginBottom": "20px"},
            children=[
                html.Div(
                    style={
                        "backgroundColor": "#1C1C1C",  # Gris très foncé pour les cartes
                        "border": "1px solid #333333",  # Bordure sombre
                        "padding": "10px",
                        "borderRadius": "8px",
                        "width": "48%",
                    },
                    children=[
                        html.H3("Répartition des Sentiments", style={"textAlign": "center", "color": "#FFFFFF"}),  # Titre en blanc
                        dcc.Graph(id="sentiment-histogram"),
                    ],
                ),

                # Nuage de hashtags
                html.Div(
                    style={
                        "backgroundColor": "#1C1C1C",
                        "border": "1px solid #333333",
                        "padding": "10px",
                        "borderRadius": "8px",
                        "width": "48%",
                    },
                    children=[
                        html.H3("Top 10 Hashtags", style={"textAlign": "center", "color": "#FFFFFF"}),  # Titre en blanc
                        dcc.Graph(id="hashtag-cloud"),
                    ],
                ),
            ],
        ),

        # Row 2: Engagement vs Followers
        html.Div(
            style={
                "backgroundColor": "#1C1C1C",
                "border": "1px solid #333333",
                "padding": "10px",
                "borderRadius": "8px",
                "marginBottom": "20px",
            },
            children=[
                html.H3("Engagement vs Nombre de Followers", style={"textAlign": "center", "color": "#FFFFFF"}),  # Titre en blanc
                dcc.Graph(id="engagement-graph"),
            ],
        ),

        # Intervalle de mise à jour
        dcc.Interval(
            id="update-interval",
            interval=5000,  # Mise à jour toutes les 5 secondes
            n_intervals=0,
        ),
    ],
)

# Callback pour mettre à jour les graphiques
@app.callback(
    [Output("sentiment-histogram", "figure"),
     Output("hashtag-cloud", "figure"),
     Output("engagement-graph", "figure")],
    [Input("update-interval", "n_intervals")]
)
def update_graphs(n):
    # Charger les données
    df = load_data()

    # Vérification des colonnes nécessaires
    if df.empty or not {"sentiment", "hashtags", "engagement"}.issubset(df.columns):
        return {}, {}, {}

    # Histogramme des sentiments
    sentiment_histogram = px.histogram(
        df, x="sentiment",
        title="Répartition des Sentiments",
        labels={"sentiment": "Sentiment", "count": "Nombre de Tweets"},
        color="sentiment",
        color_discrete_map={"positive": "#2ecc71", "neutral": "#f1c40f", "negative": "#e74c3c"},
        template="plotly_dark",  # Utilisation du thème sombre de Plotly
    )

    # Nuage de hashtags (Top 10)
    hashtag_counts = pd.Series([tag for tags in df["hashtags"].dropna() for tag in tags]).value_counts()
    hashtag_df = pd.DataFrame({"Hashtag": hashtag_counts.index, "Count": hashtag_counts.values})
    hashtag_cloud = px.bar(
        hashtag_df.head(10), x="Hashtag", y="Count",
        title="Top 10 des Hashtags",
        labels={"Hashtag": "Hashtag", "Count": "Nombre d'Utilisations"},
        color="Hashtag",
        template="plotly_dark",  # Utilisation du thème sombre de Plotly
    )

    # Graphique d'engagement
    engagement_graph = px.scatter(
        df, x="followers_count", y="engagement",
        size="engagement", color="sentiment",
        title="Engagement vs Nombre de Followers",
        labels={"followers_count": "Nombre de Followers", "engagement": "Engagement"},
        color_discrete_map={"positive": "#2ecc71", "neutral": "#f1c40f", "negative": "#e74c3c"},
        template="plotly_dark",  # Utilisation du thème sombre de Plotly
    )

    return sentiment_histogram, hashtag_cloud, engagement_graph

# Lancer l'application
if __name__ == "__main__":
    app.run_server(debug=True)
