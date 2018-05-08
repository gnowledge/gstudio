from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

###############Mastodon OAUTH Dependancy##########
import mastodon
from django.contrib.auth import authenticate, login
from mastodon import Mastodon
from django.template.response import TemplateResponse,loader
from gnowsys_ndf.ndf.models import *
from django.contrib.auth.models import User
from django.shortcuts import render
from django.contrib import messages
########################################


class mastodon_login(object):
    def moauth(self,request):
       
        if request.method == 'POST':
               
            #form = mform(request.POST)

            ###GET username and password from user#####
            Username = request.POST.get('username')
            Password = request.POST.get('password')
           
            
            ###CHECKING CLIENT CREDENTIALS USING MASTODON API##########
            mastodon_var = mastodon.Mastodon(
               
                client_id='gnowsys_ndf/gstudio_configs/NROER-client_cred.secret',
                api_base_url='https://member.metastudio.org'
            )

            access_token = None

            ####GET ACCESS FROM MASTODON HERE#######
            try:
                access_token  = mastodon_var.log_in(
                Username,
                Password,
                to_file='gnowsys_ndf/gstudio_configs/NROER-access_token.secret',
               
               
                )
                mastodon_var2 = Mastodon(
                    client_id = 'gnowsys_ndf/gstudio_configs/NROER-client_cred.secret',
                    access_token = access_token,
                    api_base_url = 'https://member.metastudio.org'
                )
            except Exception as e:
                print e
                pass       
               
            name = Username
            email = Username
            password = Password
                       
            if access_token:
               
                ###check whether given email is present in user table or not####
                user_email = User.objects.filter(email=name).exists()
                   
                if user_email:
             
                    ##Fetch auth object using email
                    nodes = node_collection.one({'email':{'$regex':email,'$options': 'i' },'_type':unicode("Author")})

                    if(nodes!=None):
                        #nodes.access_token = access_token
                        if (nodes.access_token!=None): 

                        ####SECOND AND BY-DEFAULT CUSTOMIZE LAYER FOR AUTHENTICATION
                            user = authenticate(username=name, password=None)

                            if user is not None:
                            
                                if user.is_active:
                                    user.is_active=True
                                   
                                    login(request,user)
                                   
                                    return HttpResponseRedirect( reverse('landing_page') )
                            else:
                                HttpResponse("Error1")
                        else:
                            nodes.access_token=access_token
                        ####SECOND AND BY-DEFAULT CUSTOMIZE LAYER FOR AUTHENTICATION
                            user = authenticate(username=name, password=None)

                            if user is not None:
                            
                                if user.is_active:
                                    user.is_active=True
                                   
                                    login(request,user)
                                   
                                    return HttpResponseRedirect( reverse('landing_page') )
                            else:
                                HttpResponse("Error1")

                    else:
                        ##Creating auth object for user
                        member = User.objects.get(email=name) 
                        Author.create_author(member.id,agency_type='Other')
                        
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
                                           
                        ##GET EMAIL TO CREATE AUTH OBJECT FOR USER
                        member = User.objects.get(email=name)
                        Author.create_author(member.id,agency_type='Other')                       
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
                error_msg_flag = "You entered wrong credentials"
                template = loader.get_template('registration/login.html')
                context = {'error_msg_flag':error_msg_flag} 
                return render(request,'registration/login.html',context)
            
        else:
          
            return HttpResponse("Invalid Credentials.")


# Below class used for overriding defualt authenticate method of django
class CustomBackendAuthenticationForDjango:
   
    # Create an authentication method
    # This is called by the standard Django login procedure
    def authenticate(self, username=None, password=None):

        try:
            # Try to find a user matching your username
            return User.objects.get(email=username)
            
        except User.DoesNotExist:
            # No user was found, return None - triggers default login failed
            return None

    # Required for your backend to work properly - unchanged in most scenarios
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None