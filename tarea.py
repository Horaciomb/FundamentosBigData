import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

# ------------------------------------------
# 1. Configura tus credenciales de Spotify
# ------------------------------------------
CLIENT_ID = "9f25cfc8480b4032ad3d6a9d59933d05"
CLIENT_SECRET = "007ca8de9e384baebbd731f14500e256"
os.environ["SPOTIPY_CLIENT_ID"] = CLIENT_ID
os.environ["SPOTIPY_CLIENT_SECRET"] = CLIENT_SECRET

# Inicializa el cliente de Spotipy
client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# ------------------------------------------
# 2. Helper para mostrar DataFrames bonito
# ------------------------------------------
def display_df(df: pd.DataFrame, title: str = None):
    """
    Imprime un DataFrame con un encabezado y formato uniforme.
    """
    if title:
        border = "=" * (len(title) + 4)
        print(f"\n{border}\n= {title} =\n{border}")
    print(df.to_string(index=False))
    print()

# ------------------------------------------
# 3. Filtrar canciones <4min de artistas femeninas
# ------------------------------------------
def get_short_tracks_by_female_artists(
    playlist_id: str,
    max_duration_sec: int = 4 * 60,
    female_artists: list[str] = None
) -> pd.DataFrame:
    """
    Devuelve un DataFrame con las pistas de la playlist que:
      • Duran menos de max_duration_sec (segundos)
      • Su artista principal aparece en female_artists
    """
    if female_artists is None:
        female_artists = [
            "Adele", "Billie Eilish", "Rosalía", "Taylor Swift",
            "Shakira", "Dua Lipa", "Karol G", "SZA"
        ]
    max_ms = max_duration_sec * 1000

    results = sp.playlist_items(
        playlist_id,
        fields="items.track(name,artists(name),duration_ms),next",
        limit=100
    )

    tracks = []
    while True:
        for item in results["items"]:
            t = item["track"]
            dur = t["duration_ms"]
            artist = t["artists"][0]["name"]
            if dur < max_ms and artist in female_artists:
                tracks.append({
                    "Playlist ID": playlist_id,
                    "Título": t["name"],
                    "Artista": artist,
                    "Duración (s)": dur // 1000
                })
        if results.get("next"):
            results = sp.next(results)
        else:
            break

    return pd.DataFrame(tracks)

# ------------------------------------------
# 4. Procesar múltiples playlists
# ------------------------------------------
def get_short_tracks_multiple_playlists(
    playlist_ids: list[str],
    max_duration_sec: int = 4 * 60,
    female_artists: list[str] = None
) -> pd.DataFrame:
    """
    Itera sobre varias playlists y concatena todos los resultados.
    """
    dfs = []
    for pid in playlist_ids:
        df = get_short_tracks_by_female_artists(pid, max_duration_sec, female_artists)
        dfs.append(df)
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    else:
        return pd.DataFrame(columns=["Playlist ID", "Título", "Artista", "Duración (s)"])

# ------------------------------------------
# 5. Ejecución de ejemplo
# ------------------------------------------
if __name__ == "__main__":
    # A) Define aquí tu(s) playlist ID(s)
    playlist_ids = [
        "6JWwOuZXAJfbAnqzrnSab6"
        # agrega más si quieres...
    ]

    # B) Llama a la función
    df_result = get_short_tracks_multiple_playlists(playlist_ids)

    # C) Muestra los resultados
    display_df(df_result, "Canciones <4min de Artistas Femeninas")
