#	Copyright 2011 Omar Shammas
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#Versions:
#	0.1		--  written by Omar Shammas (email : omar DOT shammas [a t ] g m ail DOT com)
#				Initial version works with 0.7 version of the BBB API                   


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
    
#------------------------------------------------GET URLs-------------------------------------------------
#
#This method returns the url to join the specified meeting.
#
#@param meetingID -- the unique meeting identifier used to store the meeting in the bigbluebutton server
#@param username -- the display name to be used when the user joins the meeting
#@param PW -- the attendee or moderator password of the meeting
#@param SALT -- the security salt of the bigbluebutton server
#@param URL -- the url of the bigbluebutton server
#
#@return The url to join the meeting

def joinURL(meetingID, username, PW, SALT, URL):
    url_join = URL + "api/join?"
    
    parameters = {'meetingID' : meetingID,
                  'fullName' : username,
                  'password' : PW,
                  }
    
    parameters = urllib.urlencode(parameters)
    return url_join + parameters + '&checksum=' + hashlib.sha1("join" + parameters + SALT).hexdigest()

#
#This method returns the url to join the specified meeting.
#
#@param name -- a name fot the meeting
#@param meetingID -- the unique meeting identifier used to store the meeting in the bigbluebutton server
#@param attendeePW -- the attendee of the meeting
#@param moderatorPW -- the moderator of the meeting
#@param welcome -- the welcome message that gets displayed on the chat window
#@param logoutURL -- the URL that the bbb client will go to after users logouut
#@param SALT -- the security salt of the bigbluebutton server
#@param URL -- the url of the bigbluebutton server
#
#@return The url to join the meeting

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


#
#This method returns the url to check if the specified meeting is running.
#
#@param meetingID -- the unique meeting identifier used to store the meeting in the bigbluebutton server
#@param SALT -- the security salt of the bigbluebutton server
#@param URL -- the url of the bigbluebutton server
#
#@return The url to check if the specified meeting is running.
#
def isMeetingRunningURL( meetingID, URL, SALT ):
    base_url = URL + "api/isMeetingRunning?"
    
    parameters = {'meetingID' : meetingID,}
    parameters = urllib.urlencode(parameters)
    
    return base_url + parameters + '&checksum=' + hashlib.sha1("isMeetingRunning" + parameters + SALT).hexdigest() 


#
#This method returns the url to getMeetingInfo of the specified meeting.
#
#@param meetingID -- the unique meeting identifier used to store the meeting in the bigbluebutton server
#@param modPW -- the moderator password of the meeting
#@param SALT -- the security salt of the bigbluebutton server
#@param URL -- the url of the bigbluebutton server
#
#@return The url to check if the specified meeting is running.
#
def getMeetingInfoURL( meetingID, modPW, URL, SALT ):
    base_url = URL + "api/getMeetingInfo?"
    
    parameters = {'meetingID' : meetingID,
                  'password' : modPW,
                  }
    parameters = urllib.urlencode(parameters)
    
    return base_url + parameters + '&checksum=' + hashlib.sha1("getMeetingInfo" + parameters + SALT).hexdigest()  


#
#This method returns the url for listing all meetings in the bigbluebutton server.
#
#@param SALT -- the security salt of the bigbluebutton server
#@param URL -- the url of the bigbluebutton server
#
#@return The url of getMeetings.
#
def getMeetingsURL(URL, SALT):
    base_url = URL + "api/getMeetings?"

    parameters = {'random' : (random.random() * 1000 ),}
    parameters = urllib.urlencode(parameters)
    
    return base_url + parameters + '&checksum=' + hashlib.sha1("getMeetings" + parameters + SALT).hexdigest()


#
#This method returns the url to end the specified meeting.
#
#@param meetingID -- the unique meeting identifier used to store the meeting in the bigbluebutton server
#@param modPW -- the moderator password of the meeting
#@param SALT -- the security salt of the bigbluebutton server
#@param URL -- the url of the bigbluebutton server
#
#@return The url to end the specified meeting.
#
def endMeetingURL( meetingID, modPW, URL, SALT ):
    base_url = URL + "api/end?"

    parameters = {'meetingID' : meetingID,
                  'password' : modPW,
                  }
    parameters = urllib.urlencode(parameters)
    
    return base_url + parameters + '&checksum=' + hashlib.sha1("end" + parameters + SALT).hexdigest() 




#-----------------------------------------------CREATE---------------------------------------------------- 
#
#This method creates a meeting and return an array of the xml packet
#
#@param username 
#@param meetingID -- the unique meeting identifier used to store the meeting in the bigbluebutton server
#@param welcomeString -- the welcome message to be displayed when a user logs in to the meeting
#@param mPW -- the moderator password of the meeting
#@param aPW -- the attendee password of the meeting
#@param SALT -- the security salt of the bigbluebutton server
#@param URL -- the url of the bigbluebutton server
#@param logoutURL -- the url the user should be redirected to when they logout of bigbluebutton
#
#@return
#    - Null if unable to reach the bigbluebutton server
#    - False if an error occurs while parsing
#    - Dictionary containing the values of the xml packet
#
def createMeeting( username, meetingID, welcomeString, mPW, aPW, SALT, URL, logoutURL ):

    create_url = createMeetingURL(username, meetingID, aPW, mPW, welcomeString, logoutURL, SALT, URL )
    xml = bbb_wrap_load_file( create_url )

    if(xml):
        return assign2Dict(xml)       
        
    #if unable to reach the server
    return None


#-------------------------------------------getMeetingInfo---------------------------------------------------
#
#This method calls the getMeetingInfo on the bigbluebutton server and returns an array.
#
#@param meetingID -- the unique meeting identifier used to store the meeting in the bigbluebutton server
#@param modPW -- the moderator password of the meeting
#@param SALT -- the security salt of the bigbluebutton server
#@param URL -- the url of the bigbluebutton server
#
#@return 
#    - None if unable to reach the bigbluebutton server
#    - Dictionary containing the values of the xml packet
#        - If the returncode == 'FAILED' it returns a dictionary containing a returncode, messagekey, and message. 
#        - If the returncode == 'SUCCESS' it returns a dictionary containing a meetingID, moderatorPW, attendeePW, 
#          hasBeenForciblyEnded, running, startTime, endTime, participantCount, moderatorCount, and attendees.

def getMeetingInfo( meetingID, modPW, URL, SALT ):
    getMeetingInfo_url = getMeetingInfoURL(meetingID, modPW, URL, SALT )
    xml = bbb_wrap_load_file( getMeetingInfo_url )

    if(xml):  
        mapping = {}
        response = xml.firstChild
        for child in response.childNodes:
            
            if( child.hasChildNodes() ):
                #Makes a dictionary for attendees inside mapping
                if(child.tagName == "attendees"):
                    attendees = {}
                    #Makes a dictionary for attendee inside attendees
                    for atnds in child.childNodes:
                        attendee = {}
                        #Adds the elements to the attendee dictionary
                        for atnd in atnds.childNodes:
                            if( atnd.hasChildNodes() ):
                                attendee[atnd.tagName] = atnd.firstChild.nodeValue
                            else:
                                attendee[atnd.tagName] = None
                        #Updates the attendees dictionary with the attendee we just parsed
                        attendees[ attendee["userID"] ] = attendee
                    
                    #Once completed parsing the attendees we add that dictionary to mapping
                    mapping[child.tagName] = attendees                    
                else:
                    mapping[child.tagName] = child.firstChild.nodeValue    
            else:
                mapping[child.tagName] = None
        return mapping
    
    #if unable to reach the server
    return None


#-----------------------------------------------getMeetings------------------------------------------------------
#
#This method calls getMeetings on the bigbluebutton server, then calls getMeetingInfo for each meeting and concatenates the result.
#
#@param URL -- the url of the bigbluebutton server
#@param SALT -- the security salt of the bigbluebutton server
#
#@return  
#    - None if unable to reach the bigbluebutton server
#    - Dictionary containing the values of the xml packet
#        - If the returncode == 'FAILED' it returns a dictionary containing a returncode, messagekey, and message. 
#        - If the returncode == 'SUCCESS' it returns a dictionary containing all the meetings. Each item  meetingID, moderatorPW, attendeePW, 
#          hasBeenForciblyEnded, running, startTime, endTime, participantCount, moderatorCount, and attendees.

#    - Null if the server is unreachable
#    - If FAILED then returns an array containing a returncode, messageKey, message.
#    - If SUCCESS then returns an array of all the meetings. Each element in the array is an array containing a meetingID, 
#     moderatorPW, attendeePW, hasBeenForciblyEnded, running.
#
def getMeetings( URL, SALT ):
    getMeetings_url = getMeetingsURL( URL, SALT )
    xml = bbb_wrap_load_file( getMeetings_url )
    
    if(xml):  
        mapping = {}
        response = xml.firstChild
        for child in response.childNodes:
            
            if( child.hasChildNodes() ):
                
                #Makes a dictionary for meetings inside mapping
                if(child.tagName == "meetings"):
                    meetings = {}
                    
                    #Makes a dictionary for meeting inside meetings
                    for mtgs in child.childNodes:
                        meeting = {}
                        
                        #Adds the elements to the meeting dictionary
                        for mtg in mtgs.childNodes:
                            if( mtg.hasChildNodes() ):
                                meeting[mtg.tagName] = mtg.firstChild.nodeValue
                            else:
                                meeting[mtg.tagName] = None
                        #Updates the meetings dictionary with the meeting we just parsed
                        meetings[ meeting["meetingID"] ] = meeting
                    #Once completed parsing the meetings we add that dictionary to mapping
                    mapping[child.tagName] = meetings
                                   
                else:
                    mapping[child.tagName] = child.firstChild.nodeValue    
            else:
                mapping[child.tagName] = None
                   
        return mapping
    
    #if unable to reach the server
    return None

#------------------------------------------------End Meeting------------------------------------
#
#This method calls end meeting on the specified meeting in the bigbluebutton server.
#
#@param meetingID -- the unique meeting identifier used to store the meeting in the bigbluebutton server
#@param modPW -- the moderator password of the meeting
#@param SALT -- the security salt of the bigbluebutton server
#@param URL -- the url of the bigbluebutton server
#
#@return
#    - Null if the server is unreachable
#     - A dictionary containing a returncode, messageKey, message.
#
def endMeeting( meetingID, modPW, URL, SALT ):
    endMeeting_url = endMeetingURL( meetingID, modPW, URL, SALT )
    xml = bbb_wrap_load_file( endMeeting_url )

    if(xml):
        return assign2Dict(xml)
    
    #if unable to reach the server
    return None

#------------------------------------------------isMeetingRunning------------------------------------
#
#This method check the BigBlueButton server to see if the meeting is running (i.e. there is someone in the meeting)
#
#@param meetingID -- the unique meeting identifier used to store the meeting in the bigbluebutton server
#@param SALT -- the security salt of the bigbluebutton server
#@param URL -- the url of the bigbluebutton server
#
#@return A boolean of true if the meeting is running and false if it is not running
#
def isMeetingRunning( meetingID, URL, SALT ):    
    isMeetingRunning_url = isMeetingRunningURL( meetingID, URL, SALT )
    xml = bbb_wrap_load_file( isMeetingRunning_url )

    if(xml):
        return assign2Dict(xml)
    
    #if unable to reach the server
    return None