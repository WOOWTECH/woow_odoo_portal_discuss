# -*- coding: utf-8 -*-
import re

from odoo import _
from odoo.http import request
from odoo.addons.mail.controllers.discuss.public_page import PublicPageController

DISCUSSIONS_URL = '/my/discussions'
# a "back" target must stay on this site's portal (/my, /my/...): no scheme,
# no host, no "//"; a simple query string is kept (a tab of the list:
# /my/discussions?filterby=chat)
SAFE_BACK_URL = re.compile(r'^/my(/[A-Za-z0-9_\-]+)*/?(\?[A-Za-z0-9_\-.=&%+]*)?$')


class PortalDiscussPublicPage(PublicPageController):
    """Back bar of the Discuss page opened from the portal list
    (/discuss/channel/<id>?discussions=1[&back=/my/...])."""

    def _response_discuss_public_template(self, store, channel):
        response = super()._response_discuss_public_template(store, channel)
        params = request.httprequest.args
        if 'discussions' in params and getattr(response, 'qcontext', None) is not None:
            back = params.get('back') or DISCUSSIONS_URL
            if not SAFE_BACK_URL.match(back):
                back = DISCUSSIONS_URL
            to_list = back.split('?')[0].rstrip('/') == DISCUSSIONS_URL
            response.qcontext.update({
                'portal_discuss_back_url': back,
                'portal_discuss_back_label': _('Back to Discussions') if to_list else _('Back'),
            })
        return response
