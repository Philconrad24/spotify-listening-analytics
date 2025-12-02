import spotipy
from spotipy.oauth2 import SpotifyOAuth

# REPLACE THESE WITH YOUR CREDENTIALS
CLIENT_ID = "ADD CLIENT ID HERE"
CLIENT_SECRET = "ADD CLIENT SECRET HERE"
REDIRECT_URI = "http://127.0.0.1:8888/callback"

# Set up Spotify connection
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="user-library-read user-top-read user-read-recently-played"
))

print("🎵 Connecting to Spotify...\n")

# Get your top tracks from last 6 months
print("=" * 50)
print("YOUR TOP 10 TRACKS (LAST 6 MONTHS)")
print("=" * 50)
top_tracks = sp.current_user_top_tracks(limit=10, time_range='medium_term')

for idx, track in enumerate(top_tracks['items'], 1):
    artist = track['artists'][0]['name']
    song = track['name']
    popularity = track['popularity']
    print(f"{idx}. {song} - {artist} (Popularity: {popularity})")

print("\n" + "=" * 50)
print("YOUR TOP 5 ARTISTS (LAST 6 MONTHS)")
print("=" * 50)
top_artists = sp.current_user_top_artists(limit=5, time_range='medium_term')

for idx, artist in enumerate(top_artists['items'], 1):
    name = artist['name']
    genres = ", ".join(artist['genres'][:3]) if artist['genres'] else "No genre"
    followers = artist['followers']['total']
    print(f"{idx}. {name}")
    print(f"   Genres: {genres}")
    print(f"   Followers: {followers:,}\n")

print("Success! Your Spotify API is working!")