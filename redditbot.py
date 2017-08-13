#TODO - Parse typo's
#TODO2 - Create more functions (e.g. post building into a function)

import time
import praw
import re
import urllib2
import signal, sys
import searchYouTube

class RedditYouTubeBot:

    cachedAlreadyDone = "YouTubeSearchBotdone.txt"
    def __init__(self):
        # This string is sent by praw to reddit in accordance to the API rules
        user_agent = "YouTube Bot v1.0 by /u/hborel"
        self.r = praw.Reddit("YouTubeSearchBot",user_agent=user_agent)
        # Fill in the subreddit(s) here. Multisubs are done with + (e.g. MagicTCG+EDH)
        self.subreddit = self.r.subreddit('hborelbottest')

        # This loads the already parsed comments from a backup text file    
        self.already_done = []
        try:
            with open(RedditYouTubeBot.cachedAlreadyDone,'r') as f:
                for i in f:
                    self.already_done.append(i.replace("\n", ""))
        except IOError:
            pass    
                
        # Start up the YouTube searcher
        self.youtubeSearcher = searchYouTube.YouTubeSearcher()
        
    
    # Function that backs up the most recent batch of parsed comments
    def write_done(self,doneList):
        with open(RedditYouTubeBot.cachedAlreadyDone, "a") as f:
            for i in doneList:
                f.write(str(i) + '\n')

    #most stuff happens here
    def processComment(self,comment,doneBatch):
        ids = []
        ids.append(comment.id)
        # Checks if the post is not actually the bot itself (since the details say [[CARDNAME]]
        if comment.id not in self.already_done and not str(comment.author) == self.r.user.me().name:
            print "        Match: %s" % comment.id
            songs = self.getSongsFromBody(comment.body)
            reply = self.constructReply(songs)
            # Posting might fail (too long, ban, reddit down etc), so cancel the post and print the error
            if (reply):
                try:
                    comment.reply(reply)
                except Exception,e: print str(e)
            # Add the post to the list of parsed comments
            doneBatch.append(comment.id)
    # This function is nearly the same as comment parsing, except it takes submissions (should be combined later)
    def processSubmission(self,submission,doneBatch):
        if submission.id not in self.already_done:
            print "        Found: %s" % submission.id
            songs = self.getSongsFromBody(submission.selftext)
            reply = self.constructReply(songs)
            # Posting might fail (too long, ban, reddit down etc), so cancel the post and print the error
            if (reply):
                try:
                    submission.reply(reply)
                except Exception,e: print str(e)
            doneBatch.append(submission.id)
        for comment in submission.comments.list():
            self.processComment(comment,doneBatch)
    def getSongsFromBody(self,body):
        # Regex that finds the text encaptured with [[ ]]
        songs = re.findall("\[\[([^\[\]]*)\]\]", body)
        # Because a comment can only have a max length, limit to only the first 30 requests
        if len(songs) > 30: songs = songs[0:30]
        return set(songs) #set removes duplicates
    def constructReply(self,songs):
        reply = ""
        # Set removes any duplicates
        for songQuery in songs:
            # Checks if a card exists
            searchResult = self.youtubeSearcher.search(songQuery)
            if searchResult:
                # Builds the post
                reply += "[%s](https://www.youtube.com/watch?v=%s)" % (searchResult.get("title"), searchResult.get("id"))
                reply += "\n\n"
            else:
                reply += "No results found for query %s. \n" % songQuery
        # If a post was built before, complete it and post it to reddit
        if reply:
            reply += "^^Questions? ^^Message ^^/u/hborel ^^- ^^Post ^^YouTube ^^link ^^using ^^[[YOUTUBE ^^QUERY]]"
        return reply

    def run(self):
        # Infinite loop that calls the function. The function outputs the post-ID's of all parsed comments.
        # The ID's of parsed comments is compared with the already parsed comments so the list stays clean
        # and memory is not increased. It sleeps for 15 seconds to wait for new posts.
        while True:
            new_done = []
            for submission in self.subreddit.new(limit=10):
                self.processSubmission(submission,new_done)
            # Back up the parsed comments to a file
            self.already_done += new_done
            self.write_done(new_done)
            time.sleep(15)


if __name__ == "__main__":
    r = RedditYouTubeBot()
    r.run()


