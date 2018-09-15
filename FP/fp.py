import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import os

#Spotify

cid = os.environ.get('SPOTIFY_CLIENT_ID') # client id d32df7804fa24bd4ac44ea08aa8db7b1
cs = os.environ.get('SPOTIFY_CLIENT_SECRET') # client secret d7b15d31b66c4e73ad9e1309a809bff9
ru = 'https://www.google.com/'

# get the right scope
scope = 'playlist-read-private,playlist-read-collaborative,playlist-modify-public'

username = input("Enter username: ")

token = util.prompt_for_user_token(username,scope,cid,cs,ru)

# prints out the songs in my saved songs
# use these songs as training data maybe
if token:
    sp = spotipy.Spotify(auth=token)

    # use to get user id
    currentUser = sp.current_user()
    #the user id is everything after the backslash
    fullUserID = currentUser['external_urls']['spotify']
    takeTwo = fullUserID.split('user/')
    userID = takeTwo[1]

    # makes a playlist in spotify
    #sp.user_playlist_create(userID,'Test',public=True)
    #print('We made it')

    playlists = sp.user_playlists(userID)
    #print(playlists['items'])
    playlistID = []
    for playlist in playlists['items']:
        #take everything after the last / for the playlist id
        #get the playlist id everything after the last slash
        fullPLID = playlist['external_urls']['spotify']
        #playlist ID has all the ids of my playlists
        playlistID.append(fullPLID.split('playlist/')[1])

    # go into each playlist and put the track ids into a lsit
    idList = []
    for x in playlistID:
        # track info for playlist x
        tracks = sp.user_playlist(userID,x)['tracks']
        count = 0
        # goes through all the tracks and puts the id in idlist
        while count < len(tracks['items']):
            idList.append(tracks['items'][count]['track']['id'])
            count = count + 1
    # idList now has a lot of good song ids

    # need to do analysis on all the songs in the list
    audioA = sp.audio_features(idList[0:50])
    #print(audioA)

    features = []
    # features will have a dict for each song with the audio features
    for track in audioA:
        features.append(track)
        #adds a target feature to each track
        features[-1]['target'] = 1

    print(features)

# make an id list with bad songs
# add them to features with target zero

else:
    print ("Can't get token for", username)
