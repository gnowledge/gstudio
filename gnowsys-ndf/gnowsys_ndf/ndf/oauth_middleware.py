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


class test(object):
    def moauth(self,request):
       
        if request.method == 'POST':
            # from mastodon import Mastodon
               
            form = mform(request.POST)

            ###GET username and password from user#####
            Username = request.POST.get('username')
            Password = request.POST.get('password')
           
            
            ###CHECKING CLIENT CREDENTIALS USING MASTODON API##########
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
           

           
            if access_token:
               
                ###check whether given email is present in user table or not####
                user_email = User.objects.filter(email=name).exists()

                if (user_email==True):
                   

                    ##Fetch auth object using email
                    nodes = node_collection.one({'email':{'$regex':email,'$options': 'i' },'_type':unicode("Author")})
                    #nodes.access_token = access_token

                    if(nodes!=None):
                        nodes.access_token = access_token
                       
                        
                        ####SECOND AND BY-DEFAULT CUSTOMIZE LAYER FOR AUTHENTICATION
                        user = authenticate(username=name, password=None)

                        print "+++++++++++++++++++++++++"
                        if user is not None:
                        
                            if user.is_active:
                                user.is_active=True
                               
                                login(request,user)
                               
                                return HttpResponseRedirect( reverse('landing_page') )
                        else:
                            HttpResponse("Error1")
                    else:
                        ##Creating auth object for user
                        execfile("/home/docker/code/gstudio/doc/deployer/create_auth_objs.py")
                        
                        ##Fetch auth object using email
                        author = node_collection.one({'email':{'$regex':email,'$options': 'i' },'_type':unicode("Author")})
                        
                        ##Assign access token for auth object
                        author.access_token = access_token

                        author.save()

                        #By default layer and customise layer of authentication
                        user = authenticate(username=name, password=None)
                        if user is not None:
                            if user.is_active:
                                login(request, user)
                                return HttpResponseRedirect( reverse('landing_page') )
                            else:
                                HttpResponse("Error1")

                else:
                    ##Creating user in django user table 
                    member = User.objects.create_user(name,email,password)
                    member.save()

                    ##Fetch auth object using email
                    nodes = node_collection.one({'email':{'$regex':email,'$options': 'i' },'_type':unicode("Author")})

                    if(nodes!=None):

                        
                        user = authenticate(username=name, password=None)
                        if user is not None:
                            if user.is_active:
                                
                                login(request, user)
                                return HttpResponseRedirect( reverse('landing_page') )
                            else:
                                HttpResponse("Error2")



                    else:
                                           
                        execfile("/home/docker/code/gstudio/doc/deployer/create_auth_objs.py")
                       
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

                return HttpResponseRedirect(reverse('login') ) 
            
        else:
          
            return HttpResponse("Invalid Credentials.")




# Below class used for overriding defualt authenticate method of django
class MyCustomBackend:
   
    # Create an authentication method
    # This is called by the standard Django login procedure
    def authenticate(self, username=None, password=None):

        try:
            # Try to find a user matching your username
            user = User.objects.get(email=username)

           
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