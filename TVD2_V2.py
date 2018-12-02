import lirc
import xmltv
from datetime import datetime, timedelta
import pprint
from collections import defaultdict 
import pyttsx3
import urllib.request
import time
from interruptingcow import timeout

POLL_TIME = 12
WORDS_PER_MINUTES = 300
TIMEOUT = 3

class TvListings:
    def __init__(self):
        self.channelsCare = {'BBC One Yorks', 'BBC Two Eng', 'ITV', 'Channel 4', 'Channel 5','ITV2','BBC Four','ITV3', 'Pick'}
        self.lastUpdatedListings = datetime.now() - timedelta(hours=POLL_TIME)
        self.currentProgrammes = defaultdict(list)
        self.nextProgrammes = defaultdict(list)
        self.channelsInputDict = {}
        

    def Update_Listings(self):
        #urllib.request.urlretrieve("http://www.xmltv.co.uk/feed/6721", "tvlistings.xml")
        self.channelsInputDict = xmltv.read_channels(open('tvlistings.xml', 'r'))
        self.programmeInputDict = xmltv.read_programmes(open('tvlistings.xml', 'r'))
        self.lastUpdatedListings = datetime.now()
    
    def Retrieve_Listings(self):
        
        nowTime = datetime.now()
        if (nowTime - self.lastUpdatedListings) >= timedelta(minutes=POLL_TIME):
            self.Update_Listings()
        date_object = nowTime.strftime('%Y%m%d%H%S') + '00'
    
        # Print channels
        channelsDict = {}
        for i in self.channelsInputDict:
            channelsDict[i['id']] = i['display-name'][0][0]
        

        currentDictList = defaultdict(list)
        nextDictList = defaultdict(list)
            
        for programme in self.programmeInputDict:
            if channelsDict[programme['channel']] in self.channelsCare:
                if(int(programme['start'].split(' ')[0]) < int(date_object)):
                    currentDictList[programme['channel']].append(programme)
                else:
                    nextDictList[programme['channel']].append(programme)
        
        currentProgrammes = defaultdict(list)
        nextProgrammes = defaultdict(list)
        
        for channel in currentDictList:
           currentProgrammes[channelsDict[channel]] = max(currentDictList[channel], key = lambda programme: programme['start'])
           
        for channel in nextDictList:
           nextProgrammes[channelsDict[channel]] = min(nextDictList[channel], key = lambda programme: programme['start'])
        

        return(currentProgrammes, nextProgrammes)

def ReadChannel(channel,numberToChannels):
    engine = pyttsx3.init()
    engine.setProperty('rate', WORDS_PER_MINUTES)
    curChannel = numberToChannels[channel]          
    engine.say(curChannel)
    engine.runAndWait()
    
def ReadDesc(Programme,channel,numberToChannels):
    engine = pyttsx3.init()
    engine.setProperty('rate', WORDS_PER_MINUTES)
   
    curChannel = numberToChannels[channel]          
    #engine.say(curChannel)
    engine.say(Programme[curChannel]['title'][0][0])
    engine.say(Programme[curChannel]['desc'][0][0])            
    engine.runAndWait()
    

def getUserInput(channel):
    boolReadDesc = False
    boolReadChannel = True
    numInput= 1
    strInput =' '
    x =[]
    uInput = input('Enter control key code : ')
    x.append(uInput) #= lirc.nextcode()
    print(x[0])
    if(len(x) > 0):
            if (x[0] == 'KEY_PAGEDOWN'):
                channel -= 1
                if (channel == 0):
                    channel = 9
            elif (x[0] == 'KEY_PAGEUP'):
                channel += 1
                if (channel == 10):
                    channel = 1
            elif(x[0][4].isdigit() ==True):
                
                strInput = x[0][4]
                timeoutStart = time.time()
                x=[]
                while time.time()<timeoutStart + TIMEOUT:
                        uInput = input('Enter control key code : ')
                        x.append(uInput) #= lirc.nextcode()
                        strInput = strInput + x[0][4]
                        break
                channel = int(strInput)
                print(channel)
                    
            elif(x[0] == 'KEY_INFO'):
                boolReadChannel = False
                boolReadDesc = True
            else:
                print("Error")
    return(channel,boolReadChannel,boolReadDesc)


if __name__ == '__main__':
 

    #urllib.request.urlretrieve("http://www.xmltv.co.uk/feed/6721", "tvlistings.xml")
    guide = TvListings()
    currentProgrammes, nextProgrammes = guide.Retrieve_Listings()
    #sockid = lirc.init("myprogram")
    nowtime = time.time()
    channel = 3
    numberToChannels = {1:'BBC One Yorks', 2:'BBC Two Eng', 3:'ITV', 4:'Channel 4', 5:'Channel 5', 6:'ITV2', 7:'BBC Four', 8:'ITV3', 9:'Pick'}
    print('READY')
    engine = pyttsx3.init()
    engine.setProperty('rate', WORDS_PER_MINUTES)
    
    boolReadChannel = True
    boolReadDesc = False
    
    while(True):
  
        if((time.time() - nowtime) > 43200):
            currentProgrammes, nextProgrammes = guide.Retrieve_Listings()
            nowtime = time.time()
        
        channel,boolReadChannel,boolReadDesc = getUserInput(channel)
        print(channel)
        if (boolReadChannel == True):
            ReadChannel(channel,numberToChannels)
            
        if (boolReadDesc == True):
            ReadDesc(currentProgrammes,channel,numberToChannels)
            
    #lirc.deinit()
