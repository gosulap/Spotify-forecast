import spotipy
import trackRetriever
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import os
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier
import trackRetriever

#Spotify

cid = os.environ.get('SPOTIFY_CLIENT_ID') # client id
cs = os.environ.get('SPOTIFY_CLIENT_SECRET') # client secret
ru = 'https://www.google.com/'
badPlayListId = '45adBm5TCkkMszbwhKHQNL'
# get the right scope
scope = 'playlist-read-private,playlist-read-collaborative,playlist-modify-public'

username = input("Enter username: ")

badArtists = []
badPeople = input("Which Artists do you not like? Enter them with commas in between: ")
badArtists = badPeople.split(',')



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

    # go into each playlist and put the track ids into a lsit
    idList = trackRetriever.getTracks("pradhitg",cid,cs,ru)
   
    # these are the track in my bad playlist
    badTracks = trackRetriever.get_playlist_tracks(userID,badPlayListId,sp)
    

    for track in badTracks:
        idList.remove(track['track']['id'])

    features = []
    #print(audioA)
    # features will have a dict for each song with the audio features
    for i in range(0,len(idList),50):
        audioA = sp.audio_features(idList[0:50])
        for track in audioA:
            features.append(track)
            #adds a target feature to each track
            features[-1]['target'] = 1


# make an id list with bad songs
# add them to features with target zero
    badidList = []
    count1 = 0
    # goes through all the tracks and puts the id in idlist

    while count1 < len(badTracks):
        badidList.append(badTracks[count1]['track']['id'])
        count1 = count1 + 1


    for i in range(0,len(badidList),50):
        audioB = sp.audio_features(badidList[0:50])
        for track in audioB:
            features.append(track)
            #adds a target feature to each track
            features[-1]['target'] = 0

    trainingData = pd.DataFrame(features)

    train, test = train_test_split(trainingData, test_size = 0.15)

    #Define the set of features that we want to look at
    features = ["danceability", "loudness", "valence", "energy", "instrumentalness", "acousticness", "key", "speechiness", "duration_ms"]
    #Split the data into x and y test and train sets 
    x_train = train[features]
    y_train = train["target"]
    x_test = test[features]
    y_test = test["target"]


    ada = AdaBoostClassifier(n_estimators=100)
    ada.fit(x_train, y_train)
    ada_pred = ada.predict(x_test)
    score = accuracy_score(y_test, ada_pred) * 100
    #print("Accuracy using ada: ", round(score, 1), "%")

    gbc = GradientBoostingClassifier(n_estimators=100, learning_rate=.1, max_depth=1, random_state=0)
    gbc.fit(x_train, y_train)
    predicted = ada.predict(x_test)
    score = accuracy_score(y_test, predicted)*100
    #print("Accuracy using Gbc: ", round(score, 1), "%")

    #find a playlist that we should search through
    newReleases = sp.new_releases('US')
    newSongs = []


    while newReleases['albums']['next']:
        for release in newReleases['albums']['items']:
            if(release['album_type'] == 'album'):
                album = sp.album(release['id'])
                for track in album['tracks']['items']:
                    if track['artists'][0]['name'] not in badArtists:
                        newSongs.append(track)

        newReleases = sp.next(newReleases["albums"])

    newSongIds = []
    for i in range(len(newSongs)):
        newSongIds.append(newSongs[i]['id'])

    newReleasesFeatures = []
    j = 0
    for i in range(0,len(newSongIds),50):
        audioC = sp.audio_features(newSongIds[0:50])
        for track in audioC:
            if(j < len(newSongs)):
                track['song_title'] = newSongs[j]['name']
                track['artist'] = newSongs[j]['artists'][0]['name']
                newReleasesFeatures.append(track)
                j = j + 1

    newReleasesDataFrame = pd.DataFrame(newReleasesFeatures)
    pred = ada.predict(newReleasesDataFrame[features])

    i = 0
    checkTheseOut = []

    for prediction in pred:
        if(prediction == 1):
            checkTheseOut.append(newReleasesDataFrame['song_title'][i])
            print("Song: "+newReleasesDataFrame['song_title'][i]+ ", By: "+newReleasesDataFrame['artist'][i])
            #print(i)
        i = i + 1
    print(len(checkTheseOut))
else:
    print ("Can't get token for", username)
