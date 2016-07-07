import urllib, urllib2, socket
import hashlib, random
from xml.dom import minidom 
from xml.dom.minidom import Node 


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
    
def joinURL(meetingID, username, PW, SALT, URL):
    url_join = URL + "api/join?"
    
    parameters = {'meetingID' : meetingID,
                  'fullName' : username,
                  'password' : PW,
                  }
    
    parameters = urllib.urlencode(parameters)
    return url_join + parameters + '&checksum=' + hashlib.sha1("join" + parameters + SALT).hexdigest()


def createMeetingURL(name, meetingID, attendeePW, moderatorPW, welcome, logoutURL, SALT, URL):
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


def createMeeting( username, meetingID, welcomeString, mPW, aPW, SALT, URL, logoutURL ):

    create_url = createMeetingURL(username, meetingID, aPW, mPW, welcomeString, logoutURL, SALT, URL )
    xml = bbb_wrap_load_file( create_url )

    if(xml):
        return assign2Dict(xml)       
        
    #if unable to reach the server
    return None
