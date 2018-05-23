from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
# from django.views.generic import RedirectView

from registration.backends.default.views import RegistrationView
from registration.backends.default.views import ActivationView
from jsonrpc import jsonrpc_site

# from gnowsys_ndf.ndf.forms import *
from gnowsys_ndf.settings import GSTUDIO_SITE_NAME,GSTUDIO_USERNAME_SELECTION_WIDGET
from gnowsys_ndf.ndf.views.email_registration import password_reset_email, password_reset_error, GstudioEmailRegistrationForm
from gnowsys_ndf.ndf.forms import UserChangeform, UserResetform
from gnowsys_ndf.ndf.views.home import homepage, landing_page
from gnowsys_ndf.ndf.views.methods import tag_info
from gnowsys_ndf.ndf.views.custom_app_view import custom_app_view, custom_app_new_view
from gnowsys_ndf.ndf.views import rpc_resources
if GSTUDIO_SITE_NAME.lower() == 'clix':
    login_template = 'registration/login_clix.html'
    logout_template = "ndf/landing_page_clix.html"
else:
    login_template = 'registration/login.html'
    logout_template = 'registration/logout.html'

urlpatterns = patterns('',
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^pref_lang/$', include('gnowsys_ndf.ndf.urls.languagepref')),

    # gstudio admin url's
    (r'^admin/', include('gnowsys_ndf.ndf.urls.gstudio_admin')),

    # --mobwrite-- commented for time being
    # (r'^raw/(?P<name>.+)/', 'gnowsys_ndf.mobwrite.views.raw'),
    # (r'^r/(?P<name>.+)/', 'gnowsys_ndf.mobwrite.views.raw'),
    # (r'^m/(?P<name>.+)/', 'gnowsys_ndf.mobwrite.views.html'),
    # (r'^t/(?P<name>.+)/', 'gnowsys_ndf.mobwrite.views.text'),
    # (r'^new/$', 'gnowsys_ndf.mobwrite.views.new'),
    # (r'^mobwrite/', 'gnowsys_ndf.mobwrite.views.mobwrite'),
    # --end of mobwrite

    # url(r'^(?P<group_id>[^/]+)/mailclient[/]error[/](?P<error_obj>[\w-]+)$', 'gnowsys_ndf.ndf.views.mailclient.mailclient_error_display', name='mailclient_error_display'),

    url(r'^$', homepage, {"group_id": "home"}, name="homepage"),
    url(r'^welcome/?', landing_page, name="landing_page"),

    url(r'^captcha/', include('captcha.urls')),
    (r'^', include('gnowsys_ndf.ndf.urls.captcha')),

    # all main apps
    (r'^(?P<group_id>[^/]+)/mailclient', include('gnowsys_ndf.ndf.urls.mailclient')),
    (r'^(?P<group_id>[^/]+)/analytics', include('gnowsys_ndf.ndf.urls.analytics')),
    (r'^(?P<group_id>[^/]+)/file', include('gnowsys_ndf.ndf.urls.file')),
    (r'^(?P<group_id>[^/]+)/jhapp', include('gnowsys_ndf.ndf.urls.jhapp')),
    (r'^(?P<group_id>[^/]+)/filehive', include('gnowsys_ndf.ndf.urls.filehive')),
    (r'^(?P<group_id>[^/]+)/image', include('gnowsys_ndf.ndf.urls.image')),
    (r'^(?P<group_id>[^/]+)/audio', include('gnowsys_ndf.ndf.urls.audio')),
    (r'^(?P<group_id>[^/]+)/video', include('gnowsys_ndf.ndf.urls.video')),
    (r'^(?P<group_id>[^/]+)/page', include('gnowsys_ndf.ndf.urls.page')),
    (r'^(?P<group_id>[^/]+)/group', include('gnowsys_ndf.ndf.urls.group')),
    (r'^(?P<group_id>[^/]+)/partner', include('gnowsys_ndf.ndf.urls.partner')),
    (r'^(?P<group_id>[^/]+)/forum', include('gnowsys_ndf.ndf.urls.forum')),
    (r'^(?P<group_id>[^/]+)/quiz', include('gnowsys_ndf.ndf.urls.quiz')),
    (r'^(?P<group_id>[^/]+)/discussion', include('gnowsys_ndf.ndf.urls.discussion')),
    (r'^(?P<group_id>[^/]+)/unit',include('gnowsys_ndf.ndf.urls.unit')),
    # (r'^api/v1|api',include('gnowsys_ndf.ndf.urls.api')),
    (r'^api/v1',include('gnowsys_ndf.ndf.urls.api_v1')),
    (r'^api/v2',include('gnowsys_ndf.ndf.urls.api_v2')),
    
    # Commented following url for khaal hackathon
    (r'^(?P<group_id>[^/]+)/course', include('gnowsys_ndf.ndf.urls.course')),

    # (r'^(?P<group_id>[^/]+)/gcourse', include('gnowsys_ndf.ndf.urls.gcourse')),

    (r'^(?P<group_id>[^/]+)/program', include('gnowsys_ndf.ndf.urls.program')),
    (r'^(?P<group_id>[^/]+)/module', include('gnowsys_ndf.ndf.urls.module')),
    (r'^(?P<group_id>[^/]+)/search', include('gnowsys_ndf.ndf.urls.search_urls')),
    (r'^(?P<group_name>[^/]+)/task', include('gnowsys_ndf.ndf.urls.task')),
    (r'^(?P<group_id>[^/]+)/batch', include('gnowsys_ndf.ndf.urls.batch')),
    (r'^(?P<group_id>[^/]+)/ajax/', include('gnowsys_ndf.ndf.urls.ajax-urls')),
    (r'^(?P<group_id>[^/]+)/bib_app', include('gnowsys_ndf.ndf.urls.Bib_App')),
    (r'^(?P<group_id>[^/]+)/wikidata', include('gnowsys_ndf.ndf.urls.wikidata')),
    (r'^(?P<group_id>[^/]+)/', include('gnowsys_ndf.ndf.urls.user')),
    (r'^(?P<group_id>[^/]+)/ratings', include('gnowsys_ndf.ndf.urls.ratings')),
    (r'^(?P<group_id>[^/]+)/topics', include('gnowsys_ndf.ndf.urls.topics')),
    (r'^(?P<group_id>[^/]+)/curriculum', include('gnowsys_ndf.ndf.urls.curriculum')),
    (r'^(?P<group_id>[^/]+)/e-library', include('gnowsys_ndf.ndf.urls.e-library')),
    (r'^(?P<group_id>[^/]+)/e-book', include('gnowsys_ndf.ndf.urls.e-book')),
    (r'^(?P<group_id>[^/]+)/term', include('gnowsys_ndf.ndf.urls.term')),
    (r'^(?P<group_id>[^/]+)/event', include('gnowsys_ndf.ndf.urls.event')),
    (r'^(?P<group_id>[^/]+)/data-review', include('gnowsys_ndf.ndf.urls.data_review')),
    (r'^(?P<group_id>[^/]+)/observation', include('gnowsys_ndf.ndf.urls.observation')),
    (r'^(?P<group_id>[^/]+)/compare', include('gnowsys_ndf.ndf.urls.version')),
    (r'^(?P<group_id>[^/]+)/moderation', include('gnowsys_ndf.ndf.urls.moderation')),
    (r'^(?P<group_id>[^/]+)/feeds', include('gnowsys_ndf.ndf.urls.feeds')),
    (r'^(?P<group_id>[^/]+)/trash',include('gnowsys_ndf.ndf.urls.trash')),
    (r'^(?P<group_id>[^/]+)/buddy',include('gnowsys_ndf.ndf.urls.buddy')),
    (r'^(?P<group_id>[^/]+)/translation',include('gnowsys_ndf.ndf.urls.translation')),
    (r'^(?P<group_id>[^/]+)/node',include('gnowsys_ndf.ndf.urls.node')),
    # needs to decide on asset and it's url(s).
    # (r'^(?P<group_id>[^/]+)/asset',include('gnowsys_ndf.ndf.urls.asset')),

    (r'^(?P<group_id>[^/]+)/type_created',include('gnowsys_ndf.ndf.urls.type_created')),

    url(r'^(?P<group_id>[^/]+)/topic_details/(?P<app_Id>[\w-]+)', 'gnowsys_ndf.ndf.views.topics.topic_detail_view', name='topic_details'),

    # -- django-json-rpc method calls --
    url(r'^json/browse/$', 'jsonrpc.views.browse', name='jsonrpc_browser'),
    url(r'^json/$', jsonrpc_site.dispatch, name='jsonrpc_mountpoint'),
    # url for directly calling RPC method from browser
    (r'^json/(?P<method>[a-zA-Z0-9.-_]+)$', jsonrpc_site.dispatch),
    # ---end of django-json-rpc

    # -- mis --
    (r'^(?P<group_id>[^/]+)/mis', include('gnowsys_ndf.ndf.urls.mis', namespace='mis'), {'app_name': "MIS"}),
    (r'^(?P<group_id>[^/]+)/mis-po', include('gnowsys_ndf.ndf.urls.mis', namespace='mis-po'), {'app_name': "MIS-PO"}),
    # ---end of mis

    #test url
    (r'^dev/', include('gnowsys_ndf.ndf.urls.dev_utils')),
    (r'^tools/', include('gnowsys_ndf.ndf.urls.tools')),
    # meeting app
    # (r'^online/', include('online_status.urls')),   #for online_users.
    # url(r'^(?P<group_id>[^/]+)/inviteusers/(?P<meetingid>[^/]+)','gnowsys_ndf.ndf.views.meeting.invite_meeting', name='invite_meeting'),
    # url(r'^(?P<group_id>[^/]+)/meeting/(?P<meetingid>[^/]+)','gnowsys_ndf.ndf.views.meeting.output', name='newmeeting'),
    # url(r'^(?P<group_id>[^/]+)/meeting','gnowsys_ndf.ndf.views.meeting.dashb', name='Meeting'),
    # url(r'^(?P<group_id>[^/]+)/online','gnowsys_ndf.ndf.views.meeting.get_online_users', name='get_online_users'),
    # following url (name="meeting") kept uncommented to avoid errors
    url(r'^(?P<group_id>[^/]+)/meeting','gnowsys_ndf.ndf.views.meeting.dashb', name='meeting'),
    url(r'^about.html/','gnowsys_ndf.ndf.views.site.site_about',name='site_about'),    
    url(r'^credits.html/','gnowsys_ndf.ndf.views.site.site_credits',name='site_credits'),    
    url(r'^contact.html/','gnowsys_ndf.ndf.views.site.site_contact',name='site_contact'),    
    url(r'^termsofservice.html/','gnowsys_ndf.ndf.views.site.site_termsofuse',name='site_termsofuse'),    
    url(r'^privacypolicy.html/','gnowsys_ndf.ndf.views.site.site_privacypolicy',name='site_privacypolicy'),    
    # --end meeting app

    # (r'^(?P<group_id>[^/]+)/Observations', include('gnowsys_ndf.ndf.urls.observation')),

    # --discussion--
    # url(r'^(?P<group_id>[^/]+)/(?P<node_id>[^/]+)/create_discussion$', 'gnowsys_ndf.ndf.views.discussion.create_discussion', name='create_discussion'),
    # url(r'^(?P<group_id>[^/]+)/(?P<node_id>[^/]+)/discussion_reply$', 'gnowsys_ndf.ndf.views.discussion.discussion_reply', name='discussion_reply'),
    # url(r'^(?P<group_id>[^/]+)/discussion_delete_reply$', 'gnowsys_ndf.ndf.views.discussion.discussion_delete_reply', name='discussion_delete_reply'),
    # --end of discussion

    url(r'^(?P<group_id>[^/]+)/visualize', include('gnowsys_ndf.ndf.urls.visualise_urls')),

    (r'^explore/', include('gnowsys_ndf.ndf.urls.explore')),
    url(r'^help-page/(?P<page_name>[^/]+)$', 'gnowsys_ndf.ndf.views.home.help_page_view', name='help_page_view'),
    url(r'^(?P<group_id>[^/]+)/$', 'gnowsys_ndf.ndf.views.group.group_dashboard', name='groupchange'),
    # ---listing sub partners---
    url(r'^(?P<group_id>[^/]+)/partners$', 'gnowsys_ndf.ndf.views.partner.partner_list', name='partnerlist'),
    # --------end of listing sub partners--------
    # -- tags --
    #url(r'^(?P<group_id>[^/]+)/tags$', 'gnowsys_ndf.ndf.views.methods.tag_info', name='tag_info'),
    url(r'^(?P<group_id>[^/]+)/tags/(?P<tagname>[^/]+)$', 'gnowsys_ndf.ndf.views.methods.tag_info', name='tag_info'),
    # ---end of tags

    # -- annotations --
    # url(r'^(?P<group_id>[^/]+)/annotationlibInSelText$', 'gnowsys_ndf.ndf.views.ajax_views.annotationlibInSelText', name='annotationlibInSelText'),
    # url(r'^(?P<group_id>[^/]+)/delComment$', 'gnowsys_ndf.ndf.views.ajax_views.delComment', name='delComment'),
    # ---end of annotations

    # -- custom apps --
    # (r'^(?P<group_id>[^/]+)/(?P<app_name>[^/]+)', include('gnowsys_ndf.ndf.urls.custom_app')),
    # url(r'^(?P<group_id>[^/]+)/(?P<app_name>[^/]+)/(?P<app_id>[\w-]+)$', custom_app_view, name='GAPPS'),
    # url(r'^(?P<group_id>[^/]+)/(?P<app_name>[^/]+)/(?P<app_id>[\w-]+)/(?P<app_set_id>[\w-]+)$', custom_app_view, name='GAPPS_set'),
    # url(r'^(?P<group_id>[^/]+)/(?P<app_name>[^/]+)/(?P<app_id>[\w-]+)/(?P<app_set_id>[\w-]+)/(?P<app_set_instance_id>[\w-]+)$', custom_app_view, name='GAPPS_set_instance'),
    # url(r'^(?P<group_id>[^/]+)/(?P<app_name>[^/]+)/(?P<app_id>[\w-]+)/(?P<app_set_id>[\w-]+)/(?P<app_set_instance_id>[\w-]+)/edit/$', custom_app_new_view, name='GAPPS_set_instance_edit'),
    # url(r'^(?P<group_id>[^/]+)/(?P<app_name>[^/]+)/(?P<app_id>[\w-]+)/(?P<app_set_id>[\w-]+)/new/$', custom_app_new_view, name='GAPPS_set_new_instance'),
    # --- end of custom apps

    # (r'^home','gnowsys_ndf.ndf.views.group.group_dashboard'),
    # (r'^home/', 'gnowsys_ndf.ndf.views.home.homepage'),

    (r'^benchmarker/', include('gnowsys_ndf.benchmarker.urls')),



    url(r'^(?P<group_id>[^/]+)/repository/?$', 'gnowsys_ndf.ndf.views.methods.repository', name='repository'),
    url(r'^get_gridfs_resource/(?P<gridfs_id>[^/]+)/?$', 'gnowsys_ndf.ndf.views.file.get_gridfs_resource', name='get_gridfs_resource'),

    # django-registration
    url(r'^accounts/password/change/done/', auth_views.password_change_done, {'template_name': 'registration/password_change_done.html'}, name='password_change_done'),
    url(r'^accounts/password/change/', auth_views.password_change, {'password_change_form': UserChangeform, 'template_name': 'registration/password_change_form.html'}),
    url(r'^accounts/password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', auth_views.password_reset_confirm, {'set_password_form': UserResetform},name='password_reset_confirm'),
    url(r'^accounts/password/reset/complete/$', auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^accounts/password/reset/done/$',auth_views.password_reset_done,name="password_reset_done"),
    url(r'^accounts/password/reset/error/$', password_reset_error , name='password_reset_error'),
    url(r'^accounts/password/reset/$',
        password_reset_email,
        {
            'template_name': 'registration/password_reset_form.html',
            'email_template_name': 'registration/password_reset_email.html',
            'subject_template_name':'registration/password_reset_email_subject.txt'
        },
        name='password_reset'
    ),

    url(r'^accounts/activate/(?P<activation_key>\w+)/$',
        ActivationView.as_view(
            template_name='registration/activation_complete.html',
            get_success_url=getattr(
                settings, 'REGISTRATION_EMAIL_ACTIVATE_SUCCESS_URL',
                lambda request, user: '/accounts/activate/complete/'),
        ),
        name='registration_activate'),

    url(r'^accounts/register/$',
        RegistrationView.as_view(
            form_class=GstudioEmailRegistrationForm,
            get_success_url=getattr(
                settings, 'REGISTRATION_EMAIL_REGISTER_SUCCESS_URL',
                lambda request, user: '/accounts/register/complete/'),
        ),
        name='registration_register'),

    # url(r'^accounts/login/$', auth_views.login ,{'template_name': login_template}, name='login'),
    url(r'^accounts/login/$', auth_views.login ,{'template_name': login_template, 'extra_context': {'USERNAME_SELECTION_WIDGET': GSTUDIO_USERNAME_SELECTION_WIDGET}}, name='login'),
    url(r'^accounts/logout/$', auth_views.logout ,{'template_name': logout_template}, name='logout'),
    url(r'^accounts/', include('registration_email.backends.default.urls')),

   # --end of django-registration

   (r'^status/cache/$', 'gnowsys_ndf.ndf.views.cache.cache_status'),
    # url(r'^Beta/', TemplateView.as_view(template_name= 'gstudio/beta.html'), name="beta"),
    url(r'^(?P<user_id>[\w-]+)/profile$', 'gnowsys_ndf.ndf.views.userDashboard.save_profile', name='save_user_profile'),

)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT,
        }),
)
