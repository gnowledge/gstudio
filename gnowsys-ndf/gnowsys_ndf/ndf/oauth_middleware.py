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
                #redirect_uri = 'landing_page'
               
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
               

               
                user_email = User.objects.filter(email=name).exists()

                if (user_email==True):
                   

                    print ",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
                    nodes = node_collection.one({'email':{'$regex':email,'$options': 'i' },'_type':unicode("Author")})
                    #nodes.access_token = access_token
                    if(nodes!=None):
                        nodes.access_token = access_token
                        print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
                        
                        ####SECOND AND BY-DEFAULT CUSTOMIZE LAYER FOR AUTHENTICATION
                        user = authenticate(username=name, password=None)

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
                        
                        #author = node_collection.one({"created_by":int(member.id),"_type":unicode("Author")})
                        author = node_collection.one({'email':{'$regex':email,'$options': 'i' },'_type':unicode("Author")})
                        print author
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

                return HttpResponseRedirect(reverse('login') ) 
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