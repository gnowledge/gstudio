from django.shortcuts import render_to_response, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.views.generic import RedirectView
from gnowsys_ndf.ndf.views.methods import get_execution_time
from gnowsys_ndf.ndf.views.analytics import *



###############Mastodon OAUTH Dependancy##########
from gnowsys_ndf.ndf.forms import mform
import mastodon
from django.contrib.auth import authenticate, login
from mastodon import Mastodon 
from django.template.response import TemplateResponse
from gnowsys_ndf.ndf.models import *
from django.contrib.auth.models import User
########################################

# from django.contrib.auth.models import User
# from rest_framework import authentication
# from rest_framework import exceptions





class test(object):
    def moauth(self,request):
        
        if request.method == 'POST':
            # from mastodon import Mastodon
                
            form = mform(request.POST)
            ###GET username and password from user##### 
            Username = request.POST.get('username')
            Password = request.POST.get('password')
            
             
            ###CHECKING CLIENT CREDENTIALS########## 
            mastodon_var = mastodon.Mastodon(
                
                client_id='gnowsys_ndf/ndf/NROER-client_cred.secret',
                api_base_url='https://member.metastudio.org'
            )

            access_token = None
            ####GET ACCESS FROM MASTODON HERE#######
            try:
                access_token  = mastodon_var.log_in(
                Username,
                Password,
                to_file='gnowsys_ndf/ndf/NROER-access_token.secret',
                redirect_uri = 'landing_page'
                
                )
                mastodon_var2 = Mastodon(
                    client_id = 'gnowsys_ndf/ndf/NROER-client_cred.secret',
                    access_token = access_token,
                    api_base_url = 'https://member.metastudio.org'
                )
            except Exception as e:
                print e
                pass        
                
            name = Username
            email = Username 
            password = None
            


            print "============0000000000================"
            print access_token
            print "----------------------------"

            
            if access_token:
                #headers = {'Authorization': 'Bearer ' +access_token}

                if User.objects.filter(username=name).exists():
                    
                    print "///////////////////////////"
                    request.session['username'] = name
                    request.session['email'] = email
                    member = User.objects.get(username=name)
                    request.session['member_id'] = member.id
                    userobj = User.objects.get(id=member.id)
                    
                    print userobj
                    
                    #author = node_collection.one({"created_by":int(member.id),"_type":unicode("Author")})
                    #nodes = node_collection.one({'email':{'$regex':email,'$options': 'i' },'_type':unicode("Author")})
                    #nodes.access_token
                    #print nodes.access_token
                    #print author
                    #pa = author.access_token

                    #print author
                    #print request.session['member_id']
                    #print member.id
                    print ",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
                    nodes = node_collection.one({'email':{'$regex':email,'$options': 'i' },'_type':unicode("Author")})
                    #nodes.access_token = access_token
                    if(nodes!=None):
                        nodes.access_token = access_token
                        print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
                    ####SECOND AND BY-DEFAULT LAYER FOR AUTHENTICATION
                        user = authenticate(username=name, password=None)
                        #$client_id = 6ba5502ade8966e0869a442fe52bc1e7a3b4ca8c85b8738ad839a2b026b74c5d
                        #$client_secret = 3980dce0f8e1d4a4869b7725bcd318d8c5d40d6e67f02f7553b205d93741db80
                        #$usename = name
                        #$password = password
                        #user = "curl -X POST -d client_id=6ba5502ade8966e0869a442fe52bc1e7a3b4ca8c85b8738ad839a2b026b74c5d&client_secret=3980dce0f8e1d4a4869b7725bcd318d8c5d40d6e67f02f7553b205d93741db80&grant_type=password&username=username&password=password  -Ss https://member.metastudio.org/oauth/token"
                        #print user
                        #print self.access_token
                        #user = User.objects.get(id=member.id)

                        #user.backend = 'django.contrib.auth.backends.ModelBackend'
                        #user.backend = 'django.contrib.auth.backends.ModelBackend'
                        #user = mastodon_var.account_verify_credentials
                        #print user
                        print "+++++++++++++++++++++++++"
                        if user is not None:
                        #if access_token in request.session:
                            if user.is_active:
                                user.is_active=True
                                #print "//////////////////////////////"
                                login(request,user)
                                
                            #return mastodon_var.auth_request_url(client_id=client_id, redirect_uris='http://172.17.0.2:8000/welcome')
                                return HttpResponseRedirect( reverse('landing_page') )
                        else:
                            HttpResponse("Error1")
                    else:
                        execfile("/home/docker/code/gstudio/doc/deployer/create_auth_objs.py")
                        #print member.id
                        #print "-------------------"
                        author = node_collection.one({"created_by":int(member.id),"_type":unicode("Author")})
                        author.access_token = access_token
                        author.save()
                        user = authenticate(username=name, password=None)
                        if user is not None:
                            if user.is_active:
                                login(request, user)
                                return HttpResponseRedirect( reverse('landing_page') )
                            else:
                                HttpResponse("Error1")

                else:
                    member = User.objects.create_user(name,email,password)
                    member.save()


                    nodes = node_collection.one({'email':{'$regex':email,'$options': 'i' },'_type':unicode("Author")})
                    # print "*************************"

                    # print nodes
                    # print "*************************"
                    if(nodes!=None):

                        print "Successs!!!!!!"
                        user = authenticate(username=name, password=None)
                        if user is not None:
                            if user.is_active:
                                print "********"
                                login(request, user)
                                return HttpResponseRedirect( reverse('landing_page') )
                            else:
                                HttpResponse("Error2")



                    else:
    #################################                    
                        execfile("/home/docker/code/gstudio/doc/deployer/create_auth_objs.py")
                        #print member.id
                        print "//////////////"
                        author = node_collection.one({"created_by":int(member.id),"_type":unicode("Author")})
                        author.access_token = access_token
                        author.save()
                        ####SECOND AND BY-DEFAULT LAYER FOR AUTHENTICATION
                        user = authenticate(username=name, password=None)
                        if user is not None:
                            if user.is_active:
                                login(request, user)
                                return HttpResponseRedirect( reverse('landing_page') )
                            else:
                                HttpResponse("Error2")
                return HttpResponseRedirect( reverse('landing_page') )   
                  
            else:
                #t = TemplateResponse(request, 'login_template', {})
                #return t.render()
                #HttpResponseRedirect( reverse('landing_page') )
                return HttpResponse("You entered wrong credentials")
            #return HttpResponseRedirect( reverse('landing_page') )
        else:
           
            return HttpResponse("Invalid Credentials.")




# Name my backend 'MyCustomBackend'
class MyCustomBackend:

    # Create an authentication method
    # This is called by the standard Django login procedure
    def authenticate(self, username=None, password=None):

        try:
            # Try to find a user matching your username
            user = User.objects.get(username=username)

            
            if(user):
                # return the Django user object
                return user
            else:
                # return None - triggers default login failed
                return None
        except User.DoesNotExist:
            # No user was found, return None - triggers default login failed
            return None

    # Required for your backend to work properly - unchanged in most scenarios
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None