from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = patterns(
    '',
    # Admin URL
    url(r'^admin/', include(admin.site.urls)),
    
    # Website URL
    url(r'^$', include('website.urls')),
    
    # App URLs
    url(r'^apps/voornamen/', include('app_voornamen.urls')), 
    url(r'^apps/dodentocht/', include('app_dodentocht.urls')), 
    url(r'^apps/voetbalelo/', include('app_voetbalelo.urls')),
    url(r'^apps/locationhistory/', include('app_locationhistory.urls')),
    url(r'^apps/draw/', include('app_draw.urls')),
    url(r'^apps/sentiment/', include('app_sentiment.urls')),
)

# Load static files
from exergos import settings
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)