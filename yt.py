import requests
import csv
import os

api_key = os.environ['YOUTUBE_API_KEY']


def getComments(token, videoID):
    api = None
    if token:
        api = 'https://www.googleapis.com/youtube/v3/commentThreads?key={}&part=snippet&videoId={}&maxResults=100&pageToken={}'.format(
            api_key, videoID, token)
    else:
        api = 'https://www.googleapis.com/youtube/v3/commentThreads?key={}&part=snippet&videoId={}&maxResults=100'.format(
            api_key, videoID)

    req = requests.get(api)
    data = req.json()
    return data


def getStatistics(videoID):
    api = "https://www.googleapis.com/youtube/v3/videos?part=statistics&id={}&key={}".format(
        videoID, api_key)
    req = requests.get(api)
    data = req.json()
    return data


def start():
    print("1: Get Youtube Comments")
    print("2: Get Youtube Video Statistics\n")
    select = int(input("Enter Selection: "))
    if select == 1:
        videoID = input("\nEnter Youtube Video ID: ")
        comments = []
        next_token = None
        next_page = True
        while next_page:
            data = getComments(next_token, videoID)
            if 'nextPageToken' in data:
                next_token = data['nextPageToken']
                comments.extend(data['items'])
            else:
                if 'items' in data:
                    comments.extend(data['items'])
                    next_page = False
                else:
                    next_page = False
        if len(comments) > 0:
            with open('ytComments.csv', 'w', encoding="UTF-8") as file:
                writer = csv.writer(file, delimiter=",", lineterminator="\n")
                writer.writerow(['id', 'name', 'text', 'image', 'channel',
                                'commentlikes', 'publishedAt', 'updatedAt'])
                for item in comments:
                    commentData = item['snippet']['topLevelComment']
                    writer.writerow([
                        commentData['id'],
                        commentData['snippet']['authorDisplayName'],
                        commentData['snippet']['textDisplay'],
                        commentData['snippet']['authorProfileImageUrl'],
                        commentData['snippet']['authorChannelUrl'],
                        commentData['snippet']['likeCount'],
                        commentData['snippet']['publishedAt'],
                        commentData['snippet']['updatedAt']
                    ])
        else:
            print('No Comments Found')

    elif select == 2:
        videoID = input("\nEnter Youtube Video ID: ")
        data = getStatistics(videoID)
        if 'items' in data:
            with open('ytstatistics.csv', 'w', encoding="UTF-8") as file:
                writer = csv.writer(file, delimiter=",", lineterminator="\n")
                writer.writerow(['id', 'views', 'likes', 'comments'])
                writer.writerow([
                    videoID,
                    data['items'][0]['statistics']['viewCount'],
                    data['items'][0]['statistics']['likeCount'],
                    data['items'][0]['statistics']['commentCount']
                ])
