#!/usr/bin/python

# This sample executes a search request for the specified search term.
# Sample usage:
#   python search.py --max-search-results=50 --max-comment-results=100
#   --output-file=./cars.txt --query="fast cars;top gear;lamborghini;nissan"
# NOTE: To use the sample, you must provide a developer key obtained
#       in the Google APIs Console. Search for "REPLACE_ME" in this code
#       to find the correct place to provide that key..

import argparse

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = 'REPLACE_ME'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


def youtube_search(youtube, query, max_search_results):
    # Call the search.list method to retrieve results matching the specified
    # query term.
    search_response = youtube.search().list(
        q=query,
        part='id,snippet',
        maxResults=max_search_results).execute()

    videos = []
    for search_result in search_response.get('items', []):
        if search_result['id']['kind'] == 'youtube#video':
            videos.append(search_result['id']['videoId'])
    return videos


def get_comment_threads(youtube, video_id, options):
    results = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=options.max_comment_results,
        textFormat="plainText").execute()

    comments = []
    for item in results['items']:
        comment = item["snippet"]["topLevelComment"]
        text = comment["snippet"]["textDisplay"]
        comments.append(text)
    return comments


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--output-file', help='Output file', default='./data.txt')
    parser.add_argument(
        '--max-search-results', help='Max search results', default=25)
    parser.add_argument(
        '--max-comment-results', help='Max comments results', default=50)
    parser.add_argument(
        '--query', help='Search terms separated by semicolon', required=True)
    args = parser.parse_args()

    try:
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                        developerKey=DEVELOPER_KEY)

        queries = args.query.split(';')

        fout = open(args.output_file, 'w')
        for query in queries:
            print("Querying for {}".format(query))
            try:
                videos = youtube_search(youtube, query, args.max_search_results)
            except HttpError as e:
                continue
            for vid in videos:
                try:
                    comments = get_comment_threads(youtube, vid, args)
                except HttpError as e:
                    continue
                for comment in comments:
                    fout.write(comment.encode('utf-8') + '\n')
        fout.close()

    except HttpError as e:
        print('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))
