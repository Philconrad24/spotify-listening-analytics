import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from datetime import datetime
import time

# Credentials
CLIENT_ID = "aaa4b2dc80db452fa225eb51dc025beb"
CLIENT_SECRET = "a0690a2cee3d40b8a449c60b5fdb335f"
REDIRECT_URI = "http://127.0.0.1:8888/callback"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="user-library-read user-top-read user-read-recently-played"
))

print("🎵 Collecting your Spotify data...\n")

# 1. Get your top tracks
print("📊 Fetching top tracks...")
top_tracks_data = []
time_ranges = ['short_term', 'medium_term', 'long_term']
time_labels = ['Last 4 weeks', 'Last 6 months', 'All time']

for time_range, label in zip(time_ranges, time_labels):
    print(f"   Getting {label}...")
    tracks = sp.current_user_top_tracks(limit=50, time_range=time_range)
    for track in tracks['items']:
        top_tracks_data.append({
            'track_name': track['name'],
            'artist_name': track['artists'][0]['name'],
            'artist_id': track['artists'][0]['id'],
            'track_id': track['id'],
            'popularity': track['popularity'],
            'duration_ms': track['duration_ms'],
            'duration_min': round(track['duration_ms'] / 60000, 2),
            'time_range': label,
            'album': track['album']['name'],
            'release_date': track['album']['release_date'],
            'explicit': track['explicit']
        })

print(f"✅ Collected {len(top_tracks_data)} top tracks")

# 2. Get audio features (with error handling)
print("\n🎼 Fetching audio features...")
track_ids = list(set([t['track_id'] for t in top_tracks_data]))
audio_features_data = []

# Try to get audio features in smaller batches
batch_size = 50  # Smaller batch size
successful = 0
failed = 0

for i in range(0, len(track_ids), batch_size):
    batch = track_ids[i:i+batch_size]
    try:
        features = sp.audio_features(batch)
        if features:
            audio_features_data.extend([f for f in features if f is not None])
            successful += len([f for f in features if f is not None])
        time.sleep(0.5)  # Be nice to the API
    except Exception as e:
        failed += len(batch)
        print(f"   ⚠️ Could not fetch features for batch {i//batch_size + 1}: {str(e)[:50]}")
        continue

print(f"✅ Successfully collected audio features for {successful} tracks")
if failed > 0:
    print(f"⚠️ Failed to get features for {failed} tracks (this is okay for now)")

# 3. Create DataFrames
df_tracks = pd.DataFrame(top_tracks_data)

# If we got any audio features, merge them
if audio_features_data:
    df_features = pd.DataFrame(audio_features_data)
    df_full = df_tracks.merge(
        df_features[['id', 'danceability', 'energy', 'key', 'loudness', 
                     'speechiness', 'acousticness', 'instrumentalness', 
                     'liveness', 'valence', 'tempo']],
        left_on='track_id',
        right_on='id',
        how='left'
    )
    df_full = df_full.drop('id', axis=1)
else:
    df_full = df_tracks
    print("\n⚠️ No audio features collected - you can still analyze your data!")

# 4. Get your top artists
print("\n👥 Fetching top artists...")
top_artists_data = []

for time_range, label in zip(time_ranges, time_labels):
    artists = sp.current_user_top_artists(limit=20, time_range=time_range)
    for artist in artists['items']:
        genres = ", ".join(artist['genres'][:3]) if artist['genres'] else "Unknown"
        top_artists_data.append({
            'artist_name': artist['name'],
            'artist_id': artist['id'],
            'genres': genres,
            'popularity': artist['popularity'],
            'followers': artist['followers']['total'],
            'time_range': label
        })

df_artists = pd.DataFrame(top_artists_data)
print(f"✅ Collected {len(df_artists)} artist entries")

# 5. Get recently played
print("\n⏱️ Fetching recently played tracks...")
recent_tracks = []
try:
    recent = sp.current_user_recently_played(limit=50)
    for item in recent['items']:
        track = item['track']
        recent_tracks.append({
            'track_name': track['name'],
            'artist_name': track['artists'][0]['name'],
            'played_at': item['played_at'],
            'duration_min': round(track['duration_ms'] / 60000, 2)
        })
    df_recent = pd.DataFrame(recent_tracks)
    print(f"✅ Collected {len(df_recent)} recently played tracks")
except Exception as e:
    print(f"⚠️ Could not fetch recently played: {e}")
    df_recent = pd.DataFrame()

# 6. Save all data
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Save main dataset
filename_tracks = f"spotify_tracks_{timestamp}.csv"
df_full.to_csv(filename_tracks, index=False)

# Save artists
filename_artists = f"spotify_artists_{timestamp}.csv"
df_artists.to_csv(filename_artists, index=False)

# Save recent plays if we got them
if not df_recent.empty:
    filename_recent = f"spotify_recent_{timestamp}.csv"
    df_recent.to_csv(filename_recent, index=False)

# Print summary
print("\n" + "=" * 60)
print("🎉 DATA COLLECTION COMPLETE!")
print("=" * 60)
print(f"\n📁 Files saved:")
print(f"   • {filename_tracks}")
print(f"   • {filename_artists}")
if not df_recent.empty:
    print(f"   • {filename_recent}")

print(f"\n📈 Summary:")
print(f"   • Total unique tracks: {len(df_full)}")
print(f"   • Total artists: {df_artists['artist_name'].nunique()}")
print(f"   • Audio features collected: {successful} tracks")

print("\n🎵 Your Top 5 Most Popular Tracks:")
print(df_full.nlargest(5, 'popularity')[['track_name', 'artist_name', 'popularity']])

print("\n👥 Your Top 5 Artists (Last 6 Months):")
top_artists_medium = df_artists[df_artists['time_range'] == 'Last 6 months'].nlargest(5, 'popularity')
for idx, row in top_artists_medium.iterrows():
    print(f"   {row['artist_name']} - {row['genres']}")

print("\n✅ Ready for analysis! Use these CSV files in your Jupyter notebook.")