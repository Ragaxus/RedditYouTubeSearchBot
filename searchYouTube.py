#!/usr/bin/python

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import youtubeAPIconfig

class YouTubeSearcher:
    # Assumes existence of youtubeAPIconfig.py file, not included in this repo.
    # To use this, make a file called youtubeAPIconfig.py in the same directory, and within it,
    # Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
    # tab of
    #   https://cloud.google.com/console
    # Please ensure that you have enabled the YouTube Data API for your project.
    
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    def __init__(self):  
        self.youtube = build(YouTubeSearcher.YOUTUBE_API_SERVICE_NAME, YouTubeSearcher.YOUTUBE_API_VERSION,
        developerKey=youtubeAPIconfig.DEVELOPER_KEY)
      
    #Returns the first YouTube search for a query
    #in the format { "title": title of video, "id": videoId).
    def search(self,query):
        options = lambda: None
        setattr(options, "q", query)
        setattr(options, "max_results", 1)
        return self.doSearch(options)
    
    
    def doSearch(self,options):
      # Call the search.list method to retrieve results matching the specified
      # query term.
      retval = {}
      search_response = self.youtube.search().list(
        q=options.q,
        part="id,snippet",
        type="video",
        maxResults=options.max_results
      ).execute()
      
      if (search_response["pageInfo"]["totalResults"] > 0):
          search_result=search_response.get("items", [])[0]
          retval["title"]=search_result["snippet"]["title"]
          retval["id"]=search_result["id"]["videoId"]
      return retval


if __name__ == "__main__":
  argparser.add_argument("--q", help="Search term", default="Google")
  argparser.add_argument("--max-results", help="Max results", default=25)
  args = argparser.parse_args()
  try:
    yt = YouTubeSearcher()
    print yt.doSearch(args)
  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
