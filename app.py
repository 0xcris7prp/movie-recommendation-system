import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pickle
import pandas as pd
import requests

app = dash.Dash(__name__)

def fetch_poster(movie_id):
    response = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=00d2b899204c5a0c61e14e38fd991b12&language=en-US")
    data = response.json()
    return "https://image.tmdb.org/t/p/w500" + data['poster_path']

def fetch_details(movie_id):
    response = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=00d2b899204c5a0c61e14e38fd991b12&language=en-US")
    data = response.json()
    return data['overview'], data['runtime']

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_poster = []
    recommended_movies_overview = []
    recommended_movies_runtime = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_poster.append(fetch_poster(movie_id))
        overview, runtime = fetch_details(movie_id)
        recommended_movies_overview.append(overview)
        recommended_movies_runtime.append(runtime)

    return recommended_movies, recommended_movies_poster, recommended_movies_overview, recommended_movies_runtime

# Load data
movie_dict = pickle.load(open('movies.pkl', 'rb'))
movies = pd.DataFrame(movie_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

app.layout = html.Div([
    html.H1("CineMatch - A Movie Recommender System",
            style={'text-align': 'center', 'color': '#ec3008', 'margin-top': '20px','font-family':'Sans-serif'}),
    html.Div([
        dcc.Dropdown(
            id='movie-dropdown',
            options=[{'label': title, 'value': title} for title in movies['title']],
            value=movies['title'][0],
            style={'width': '50%', 'margin': '0 auto', 'padding': '10px'}
        ),
        html.Button('Show Recommendations', id='show-rec-btn', n_clicks=0,
                    style={'background-color': '#1abc9c', 'color': '#ecf0f1', 'border': 'none','border-radius': '10px', 'padding': '10px 20px',
                           'cursor': 'pointer', 'margin-top': '20px'})
    ], style={'text-align': 'center'}),

    html.Div(id='poster-container', style={'display': 'flex', 'justify-content': 'space-around', 'margin-top': '40px'}),

    html.Div(id='movie-details',
             style={'margin-top': '20px', 'text-align': 'center', 'color': '#bdc3c7', 'font-size': '18px',
                    'padding': '20px', 'border': '1px solid #7f8c8d', 'border-radius': '10px', 'width': '50%',
                    'margin': '20px auto', 'background-color': '#212f3d'})
], style={'background-color': '#212f3d', 'min-height': '100vh','min-width': '100vh' , 'padding': '20px'})


@app.callback(
    Output('poster-container', 'children'),
    Output('movie-details', 'children'),
    Input('show-rec-btn', 'n_clicks'),
    Input({'type': 'poster', 'index': dash.dependencies.ALL}, 'n_clicks'),
    State('movie-dropdown', 'value')
)
def update_recommendations(n_clicks_show, n_clicks_poster, selected_movie_name):
    ctx = dash.callback_context

    if not ctx.triggered:
        return '', ''

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'show-rec-btn':
        names, posters, overviews, runtimes = recommend(selected_movie_name)

        posters_html = []
        for i in range(5):
            posters_html.append(html.Div([
                html.Img(src=posters[i],
                         style={'width': '150px', 'height': '225px', 'cursor': 'pointer', 'border-radius': '10px',
                                'box-shadow': '0px 4px 8px rgba(0, 0, 0, 0.8)'}, id={'type': 'poster', 'index': i}),
                html.Div(names[i],
                         style={'text-align': 'center', 'color': '#ecf0f1', 'margin-top': '10px', 'width': '150px',
                                'white-space': 'nowrap', 'overflow': 'hidden', 'text-overflow': 'ellipsis'})
            ], style={'text-align': 'center'}))

        return posters_html, None

    elif 'poster' in triggered_id:
        button_index = eval(triggered_id)['index']
        names, posters, overviews, runtimes = recommend(selected_movie_name)

        return dash.no_update, html.Div([
            html.H3(names[button_index], style={'color': '#e74c3c'}),
            html.P([html.Span("Overview: ", style={'color': '#e74c3c', 'font-weight': 'bold'}),
                    overviews[button_index]]),
            html.P([html.Span("Runtime: ", style={'color': '#e74c3c', 'font-weight': 'bold'}),
                    f"{runtimes[button_index]} minutes"])
        ], style={'color': '#ecf0f1', 'padding': '20px', 'border': '1px solid #7f8c8d', 'border-radius': '10px', 
                  'background-color': '#2c3e50'})


if __name__ == '__main__':
    app.run_server(debug=True)
