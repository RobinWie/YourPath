# this script connects to APIs and handles recommendations

# CREDENTIALS DEFINITION
DATABASE = ""
YOUTUBE_API_DEVELOPER_KEY = ""
SPOTIFY_API_CLIENT_ID = ""
SPOTIFY_API_CLIENT_SECRET = ""

def query_youtube(query):
    import google_auth_oauthlib.flow
    import googleapiclient.discovery
    import googleapiclient.errors

    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

    api_service_name = "youtube"
    api_version = "v3"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=YOUTUBE_API_DEVELOPER_KEY)

    request = youtube.search().list(
        part="snippet",
        maxResults=10,
        q=query
    )
    response = request.execute()

    IDs = []
    Titles = []
    Channels = []
    Thumbnail_URLs = []
    
    for result in response["items"]:
        if result["id"]["kind"] == "youtube#video": # also channels in result, so far only videos used
            IDs.append(result["id"]["videoId"])
            Titles.append(result["snippet"]["title"])
            Channels.append(result["snippet"]["channelTitle"])
            Thumbnail_URLs.append(result["snippet"]["thumbnails"]["default"]["url"])

    return_dict = {
        "id": IDs,
        "title": Titles,
        "channel": Channels,
        "thumbnail_url": Thumbnail_URLs
    }

    return return_dict

def query_youtube_by_id(id_list):
    import google_auth_oauthlib.flow
    import googleapiclient.discovery
    import googleapiclient.errors

    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

    api_service_name = "youtube"
    api_version = "v3"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=YOUTUBE_API_DEVELOPER_KEY)

    response_list = []

    for cur_id in id_list:
        request = youtube.videos().list(
            part="snippet",
            maxResults=1,
            id=cur_id
        )
        response_list.append(request.execute())

    IDs = []
    Titles = []
    Channels = []
    Thumbnail_URLs = []
    for response in response_list:
        for result in response["items"]:
            if result["kind"] == "youtube#video": # also channels in result, so far only videos used
                IDs.append(result["id"])
                Titles.append(result["snippet"]["title"])
                Channels.append(result["snippet"]["channelTitle"])
                Thumbnail_URLs.append(result["snippet"]["thumbnails"]["default"]["url"])

    return_dict = {
        "id": IDs,
        "title": Titles,
        "channel": Channels,
        "thumbnail_url": Thumbnail_URLs
    }

    return return_dict

def query_spotify(query):
    import tekore as tk

    app_token = tk.request_client_token(SPOTIFY_API_CLIENT_ID, SPOTIFY_API_CLIENT_SECRET)

    spotify = tk.Spotify(app_token)

    # shows, = spotify.search('meditation', types=('shows',)) # shows don't work right now, instead tracks
    tracks, = spotify.search(query, types=('track',))

    ids = []
    names = []
    artists = []
    covers = []
    durations = []
    previews = []

    for result in tracks.items:
        ids.append(result.id)
        names.append(result.name)
        artists.append(result.artists[0].name)
        covers.append(result.album.images[0].url)
        durations.append(result.duration_ms)
        previews.append(result.preview_url)

    # durations = durations / 1000 / 60 # ms -> minutes # numpy needed

    return_dict = {
        "id": ids,
        "name": names,
        "artist": artists,
        "cover": covers,
        "duration": durations,
        "preview": previews
    }

    return return_dict

def query_spotify_by_id(id_list):
    import tekore as tk

    app_token = tk.request_client_token(SPOTIFY_API_CLIENT_ID, SPOTIFY_API_CLIENT_SECRET)

    spotify = tk.Spotify(app_token)

    # shows, = spotify.show(cur_id) # shows don't work right now, instead tracks
    
    response_list = []
    for cur_id in id_list:
        response_list.append(spotify.track(cur_id))

        ids = []
        names = []
        artists = []
        covers = []
        durations = []
        previews = []

    for result in response_list:
        ids.append(result.id)
        names.append(result.name)
        artists.append(result.artists[0].name)
        covers.append(result.album.images[0].url)
        durations.append(result.duration_ms)
        previews.append(result.preview_url)

    # durations = durations / 1000 / 60 # ms -> minutes # numpy needed

    return_dict = {
        "id": ids,
        "name": names,
        "artist": artists,
        "cover": covers,
        "duration": durations,
        "preview": previews
    }

    return return_dict

def recommendation(user):
    import sys
    import pymongo
    client = pymongo.MongoClient(DATABASE)
    cluster = client["Cluster0"]["cluster"]

    current_cluster = cluster.find_one({"id": user["cluster"]})
    rec_yt_ids = current_cluster["yt_rec"]
    rec_sf_ids = current_cluster["sf_rec"]


    return_dict = {
        "rec_yt": query_youtube_by_id(rec_yt_ids),
        "rec_sf": query_spotify_by_id(rec_sf_ids)
    }

    return return_dict

def main():
    # IMPORTS
    import sys
    import json
    import pymongo

    # CREDENTIALS
    global DATABASE
    global YOUTUBE_API_DEVELOPER_KEY
    global SPOTIFY_API_CLIENT_ID
    global SPOTIFY_API_CLIENT_SECRET

    # READ INPUT PARAMS
    username = sys.argv[1]
    query = sys.argv[2]
    DATABASE = sys.argv[3]
    YOUTUBE_API_DEVELOPER_KEY = sys.argv[4]
    SPOTIFY_API_CLIENT_ID = sys.argv[5]
    SPOTIFY_API_CLIENT_SECRET = sys.argv[6]

    # CONNECT TO MONGODB
    client = pymongo.MongoClient(DATABASE)
    users_col = client["Cluster0"]["users"]
    current_user = users_col.find({"username": username})[0]

    res_yt = query_youtube(query)
    res_sf = query_spotify(query)
    recommendations = recommendation(current_user)

    res_dict = {
        "rec_yt": recommendations["rec_yt"], # Recommendations
        "rec_sf": recommendations["rec_sf"],
        "res_yt": res_yt,   # All Results
        "res_sf": res_sf
        }

    # return to node by printing as json
    print(json.dumps(res_dict))

if __name__ == "__main__":
    main()