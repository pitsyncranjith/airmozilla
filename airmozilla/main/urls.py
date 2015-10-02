from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView
from django.views.decorators.cache import cache_page

from .views import (
    pages,
    misc,
    calendar,
    feeds,
    edit,
    reports,
)


urlpatterns = patterns(
    '',
    url(r'^__debugger__', misc.debugger__),
    url(r'^god-mode/$', misc.god_mode, name='god_mode'),
    url(r'^$', pages.home, name='home'),
    url(r'^channels/(?P<channel_slug>[-\w]+)/$', pages.home,
        name='home_channels'),
    url(r'^page/1/$', RedirectView.as_view(url='/'), name='first_page'),
    url(r'^page/(?P<page>\d+)/$', pages.home, name='home'),
    url(r'^channels/(?P<channel_slug>[-\w]+)/page/(?P<page>\d+)/$',
        pages.home, name='home_channels'),
    url(r'^channels/$', pages.channels, name='channels'),
    url(r'^login/$', pages.page, name='login',
        kwargs={'template': 'main/login.html'}),
    url(r'^login-failure/$', pages.page, name='login_failure',
        kwargs={'template': 'main/login_failure.html'}),
    url(r'^thumbnails/$', pages.thumbnails, name='thumbnails'),
    url(r'^calendar/$', calendar.calendar, name='calendar'),
    url(r'^calendar/data.json$', calendar.calendar_data, name='calendar_data'),
    url(r'^calendars/$', calendar.calendars, name='calendars'),
    url(r'^calendar/(company|contributors|public).ics$',
        calendar.events_calendar_ical, name='calendar_ical'),
    url(r'^feed/itunes/$',
        # cache_page(60 * 60)(feeds.ITunesFeed()),
        feeds.ITunesFeed(),
        name='itunes_feed'),
    url(r'^feed/itunes/(?P<channel_slug>[-\w]+)$',
        # cache_page(60 * 60)(feeds.ITunesFeed()),
        feeds.ITunesFeed(),
        name='itunes_feed'),
    url(r'^feed/(?P<private_or_public>'
        'company|public|private|contributors)?/?$',
        cache_page(60 * 60)(feeds.EventsFeed()),
        name='feed'),
    url(r'^feed/(?P<private_or_public>company|public|private|contributors)'
        r'/(?P<format_type>webm)/?$',
        cache_page(60 * 60)(feeds.EventsFeed()),
        name='feed_format_type'),
    url(r'^feed/(?P<channel_slug>[-\w]+)/$',
        cache_page(60 * 60)(feeds.EventsFeed()),
        name='channel_feed_default'),
    url(r'^feed/(?P<channel_slug>[-\w]+)/'
        r'(?P<private_or_public>company|public|private|contributors)/?$',
        cache_page(60 * 60)(feeds.EventsFeed()),
        name='channel_feed'),
    url(r'^feed/(?P<channel_slug>[-\w]+)/'
        r'(?P<private_or_public>company|public|private|contributors)/'
        r'(?P<format_type>webm|mp4)/?$',
        cache_page(60 * 60)(feeds.EventsFeed()),
        name='channel_feed_format_type'),
    url(r'^tagcloud/$', pages.tag_cloud, name='tag_cloud'),
    url(r'^livehits/(?P<id>\d+)/$',
        pages.event_livehits, name='event_livehits'),
    url(r'^unpicked-pictures/$', reports.unpicked_pictures,
        name='unpicked_pictures'),
    url(r'^too-few-tags/$', reports.too_few_tags,
        name='too_few_tags'),
    url(r'^contributors/$',
        pages.contributors,
        name='contributors'),
    url(r'^executive-summary/$',
        reports.executive_summary,
        name='executive_summary'),
    url(r'^all-tags/$', pages.all_tags, name='all_tags'),
    url(r'^(?P<slug>[-\w]+)/$', pages.EventView.as_view(),
        name='event'),
    url(r'^(?P<slug>[-\w]+)/video/$', pages.EventVideoView.as_view(),
        name='event_video'),
    url(r'^(?P<slug>[-\w]+)/related-content/$', pages.related_content,
        name='related_content'),
    url(r'^(?P<slug>[-\w]+)/permission-denied/$', pages.permission_denied,
        name='permission_denied'),
    url(r'^(?P<slug>[-\w]+)/edit/$', edit.EventEditView.as_view(),
        name='event_edit'),
    url(r'^(?P<slug>[-\w]+)/edit/chapters/$',
        edit.EventEditChaptersView.as_view(),
        name='event_edit_chapters'),
    url(r'^(?P<slug>[-\w]+)/(?P<id>\d+)/change/$',
        edit.EventRevisionView.as_view(),
        name='event_change'),
    url(r'^(?P<slug>[-\w]+)/discussion/$', pages.EventDiscussionView.as_view(),
        name='event_discussion'),
    url(r'^(?P<slug>[-\w]+)/(?P<id>\d+)/difference/$',
        edit.EventRevisionView.as_view(difference=True),
        name='event_difference'),
    url(r'^(?P<slug>[-\w]+)/status/$',
        pages.event_status,
        name='event_status'),
    url(r'^edgecast.smil$',
        misc.edgecast_smil,
        name='edgecast_smil'),
    url(r'^crossdomain.xml$',
        misc.crossdomain_xml,
        name='crossdomain_xml'),

)
