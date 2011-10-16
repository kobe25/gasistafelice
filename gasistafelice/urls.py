from django.conf.urls.defaults import *
from django.conf import settings

# Base generic admin site for superusers
from django.contrib import admin
admin.autodiscover()

from gasistafelice.gas_admin.models import gas_admin

js_info_dict = {
    'domain'  : 'djangojs',
    'packages' : ('gasistafelice.localejs', ),
}

urlpatterns = patterns('',

	(r'^$'       , 'base.views.index'  ),
	(r'^%s$'     % settings.URL_PREFIX , 'base.views.index'  ),

	(r'^%srest/' % settings.URL_PREFIX, include('rest.urls')),

	(r'^%saccounts/login/$' % settings.URL_PREFIX, 'django.contrib.auth.views.login'),
	(r'^%saccounts/logout/$' % settings.URL_PREFIX, 'django.contrib.auth.views.logout_then_login'),

    (r'^gas-admin/', include(gas_admin.urls)),
    (r'^%sadmin/' % settings.URL_PREFIX, include(admin.site.urls)),

	(r'^%sjsi18n/$'% settings.URL_PREFIX, 'django.views.i18n.javascript_catalog', js_info_dict),

)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )

