# -*- coding: utf-8 -*-
{
    'name': 'Portal Discussions',
    'version': '18.0.2.0.0',
    'category': 'Productivity/Discuss',
    'summary': 'Portal users list and open their Discuss conversations from /my/discussions',
    'description': """
Portal Discussions
==================

Odoo 18 already lets portal users chat on the Discuss page
/discuss/channel/<id>. This module gives them the way in:

* "Discussions" card on the portal home and the /my/discussions list:
  their direct messages, group chats and the channels open to portal users
  that they joined and keep pinned (same rule as the Discuss sidebar)
* Tabs All / Direct Message / Group / Channel (?filterby=) with unread
  counts; empty tabs hidden; other modules add tabs through
  _portal_discussion_filters()
* Each row: the other person's name and avatar (signed URL), the last
  message, its date and the unread count; sorted by last activity; search
* A back bar on the Discuss page opened from the list
  (?discussions=1, optional ?back=/my/... validated), server-rendered
* The conversation opens at once (no guest welcome page, no automatic
  full-screen video); the "Invite" buttons are hidden for portal users
  (Odoo refuses portal invitations on the server anyway)

Replaces cs_portal_discuss (both cannot be installed together).
    """,
    'author': 'WOOWTECH',
    'website': 'https://github.com/WOOWTECH/woow_odoo_portal_discuss',
    'license': 'LGPL-3',
    'depends': ['portal', 'mail'],
    'excludes': ['cs_portal_discuss'],
    'data': [
        'views/portal_templates.xml',
        'views/discuss_public_templates.xml',
    ],
    'assets': {
        'mail.assets_public': [
            'woow_odoo_portal_discuss/static/src/public/**/*',
        ],
    },
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
