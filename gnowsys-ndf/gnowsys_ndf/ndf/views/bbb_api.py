import urllib, urllib2, socket
import hashlib, random
from xml.dom import minidom 
from xml.dom.minidom import Node 

# ----------------------UTILITY FUNCTIONS--------------------------------------

def bbb_wrap_load_file(url):
    timeout = 10
    socket.setdefaulttimeout(timeout)

    try:
        req = urllib2.urlopen(url)
        return minidom.parse(req)
    except:
        return False
        

def assign2Dict(xml):
    try:
        mapping = {}
        response = xml.firstChild
        for child in response.childNodes:
            
            if( child.hasChildNodes() ):
                mapping[child.tagName] = child.firstChild.nodeValue
            else:
                mapping[child.tagName] = None
                                
        return mapping
    except:
        return False
    

# --------------------------GET URLs-------------------------------------------


def joinURL(meetingID, username, PW, SALT, URL):
    '''
    This method returns the url to join the specified meeting.

    Parameters:
        meetingID -- the unique meeting identifier used to store the meeting in the bigbluebutton server
        username -- the display name to be used when the user joins the meeting
        PW -- the attendee or moderator password of the meeting
        SALT -- the security salt of the bigbluebutton server
        URL -- the url of the bigbluebutton server

    Return:
        The url to join the meeting
    '''

    url_join = URL + "api/join?"
    
    parameters = {'meetingID' : meetingID,
                  'fullName' : username,
                  'password' : PW,
                  }
    
    parameters = urllib.urlencode(parameters)
    return url_join + parameters + '&checksum=' + hashlib.sha1("join" + parameters + SALT).hexdigest()


def createMeetingURL(name, meetingID, attendeePW, moderatorPW, welcome, logoutURL, SALT, URL):
    '''
    This method returns the url to join the specified meeting.

    Parameters:
        name -- a name fot the meeting
        meetingID -- the unique meeting identifier used to store the meeting in the bigbluebutton server
        attendeePW -- the attendee of the meeting
        moderatorPW -- the moderator of the meeting
        welcome -- the welcome message that gets displayed on the chat window
        logoutURL -- the URL that the bbb client will go to after users logouut
        SALT -- the security salt of the bigbluebutton server
        URL -- the url of the bigbluebutton server

    Return:
        The url to join the meeting
    '''

    url_create = URL + "api/create?"
    voiceBridge = 70000 + random.randint(0, 9999);
    parameters = {'name': name,
                  'meetingID' : meetingID,
                  'attendeePW' : attendeePW,
                  'moderatorPW' : moderatorPW,
                  'voiceBridge' : voiceBridge,
                  'logoutURL' : logoutURL,
                  }

    parameters = urllib.urlencode(parameters)
   
    welcome_parameters = ''
    if (welcome and welcome != ''):
        welcome_parameters = {'welcome': welcome.strip()} 
        welcome_parameters = urllib.urlencode(welcome_parameters)
        welcome_parameters = "&" + welcome_parameters
    
    params = parameters + welcome_parameters
    return url_create  + params + '&checksum=' + hashlib.sha1("create" + params + SALT).hexdigest() 

# -------------------------------------CREATE----------------------------------

def createMeeting(username, meetingID, welcomeString, mPW, aPW, SALT, URL, logoutURL ):
    '''
    This method creates a meeting and return an array of the xml packet

    Parameters:
        username -- name of the meeting to be created
        meetingID -- the unique meeting identifier used to store the meeting in the bigbluebutton server
        welcomeString -- the welcome message to be displayed when a user logs in to the meeting
        mPW -- the moderator password of the meeting
        aPW -- the attendee password of the meeting
        SALT -- the security salt of the bigbluebutton server
        URL -- the url of the bigbluebutton server
        logoutURL -- the url the user should be redirected to when they logout of bigbluebutton

    Return:
       - Null if unable to reach the bigbluebutton server
       - False if an error occurs while parsing
       - Dictionary containing the values of the xml packet
    '''
    create_url = createMeetingURL(username, meetingID, aPW, mPW, welcomeString, logoutURL, SALT, URL )
    xml = bbb_wrap_load_file( create_url )

    if(xml):
        return assign2Dict(xml)       
        
    #if unable to reach the server
    return None
