# -*- coding: utf-8 -*-
# Portions derived from cs_portal_discuss by Code Sparks (https://code-sparks.odoo.com), LGPL-3.
# Modified by WOOWTECH, 2026. See NOTICE.
from urllib.parse import quote, urlencode

from odoo import http, _
from odoo.osv import expression
from odoo.tools.mail import html_to_inner_content
from odoo.tools.misc import limited_field_access_token
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.http import request

PAGE_SIZE = 20
PREVIEW_LENGTH = 80
DISCUSSIONS_URL = '/my/discussions'


class PortalDiscussions(CustomerPortal):
    """/my/discussions: the portal user's conversations (direct messages, groups,
    channels open to portal users), one tab per kind, and the home card."""

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'portal_discussion_count' in counters:
            values['portal_discussion_count'] = request.env['discuss.channel'].sudo().search_count(
                self._get_portal_discussion_domain())
        return values

    def _get_portal_discussion_domain(self):
        """Conversations of the current user shown on /my/discussions.

        Same rule as the Discuss sidebar: the user is a member and has the
        conversation pinned (a chat the user closed stays hidden until a new
        message arrives, which pins it again). Channels are only listed when
        they are open to portal users.
        """
        partner = request.env.user.partner_id
        portal_group = request.env.ref('base.group_portal')
        return [
            ('channel_member_ids', 'any', [('partner_id', '=', partner.id), ('is_pinned', '=', True)]),
            '|',
                ('channel_type', 'in', ('chat', 'group')),
                '&',
                    ('channel_type', '=', 'channel'),
                    ('group_public_id', '=', portal_group.id),
        ]

    def _portal_discussion_filters(self):
        """Tabs of /my/discussions (?filterby=<key>), in display order.

        Other modules extend it (override, call super, add or change entries):
        each entry has a ``label``, a ``domain`` (added to the user's
        conversations) and a ``sequence``. 'all' must stay. A tab without
        conversations is hidden unless it is open.
        """
        return {
            'all': {'label': _('All'), 'domain': [], 'sequence': 0},
            'chat': {'label': _('Direct Message'), 'domain': [('channel_type', '=', 'chat')], 'sequence': 20},
            'group': {'label': _('Group'), 'domain': [('channel_type', '=', 'group')], 'sequence': 30},
            'channel': {'label': _('Channel'), 'domain': [('channel_type', '=', 'channel')], 'sequence': 40},
        }

    def _portal_discussions_url(self, filterby='all', **params):
        """URL of the list on the tab `filterby` (other non-empty `params` kept)."""
        query = {key: value for key, value in params.items() if value}
        if filterby and filterby != 'all':
            query = {'filterby': filterby, **query}
        return DISCUSSIONS_URL + ('?' + urlencode(query) if query else '')

    def _portal_discussion_url(self, channel, back_url=None):
        """Where a listed conversation opens: the Discuss page with the
        portal back bar (?discussions=1), leading back to `back_url`."""
        url = '/discuss/channel/%s?discussions=1' % channel.id
        if back_url and back_url != DISCUSSIONS_URL:
            url += '&back=' + quote(back_url, safe='/')
        return url

    def _portal_discussion_type_labels(self):
        return {
            'chat': _('Direct Message'),
            'group': _('Group'),
            'channel': _('Channel'),
        }

    def _prepare_portal_discussion_rows(self, channels, back_url=None):
        """Display data of the listed conversations (sudo records, the domain
        already limits them to the user's own conversations); opened
        conversations lead back to `back_url` (default: the list)."""
        partner = request.env.user.partner_id
        type_labels = self._portal_discussion_type_labels()
        members = request.env['discuss.channel.member'].sudo().search([
            ('channel_id', 'in', channels.ids), ('partner_id', '=', partner.id)])
        member_by_channel = {member.channel_id.id: member for member in members}
        last_message_ids = dict(request.env['mail.message'].sudo()._read_group(
            [('model', '=', 'discuss.channel'), ('res_id', 'in', channels.ids),
             ('message_type', 'in', ('comment', 'email'))],
            ['res_id'], ['id:max'],
        ))
        last_messages = request.env['mail.message'].sudo().browse(list(last_message_ids.values()))
        last_message_by_channel = {message.res_id: message for message in last_messages}
        rows = []
        for channel in channels:
            others = channel.channel_member_ids.partner_id - partner
            if channel.channel_type == 'chat' and others:
                title = ', '.join(others.mapped('name'))
                # signed URL, as Discuss does for non-internal users (who may not
                # read the partner): only for members of the user's own chats
                avatar_url = '/web/image/res.partner/%s/avatar_128?access_token=%s' % (
                    others[0].id, limited_field_access_token(others[0], 'avatar_128'))
            else:
                title = channel.name
                avatar_url = '/web/image/discuss.channel/%s/avatar_128' % channel.id
            message = last_message_by_channel.get(channel.id)
            preview = ''
            if message:
                preview = html_to_inner_content(message.body or '')
                if len(preview) > PREVIEW_LENGTH:
                    preview = preview[:PREVIEW_LENGTH - 1] + '…'
                if not preview and message.attachment_ids:
                    preview = _('Attachment')
                if message.author_id == partner and preview:
                    preview = _('You: %s', preview)
            member = member_by_channel.get(channel.id)
            rows.append({
                'channel': channel,
                'title': title,
                'avatar_url': avatar_url,
                'type_label': type_labels.get(channel.channel_type, channel.channel_type),
                'preview': preview,
                'last_date': message.date if message else (channel.last_interest_dt or channel.create_date),
                'unread': member.message_unread_counter if member else 0,
                'url': self._portal_discussion_url(channel, back_url),
            })
        return rows

    def _prepare_portal_discussion_tabs(self, filters, filterby, sortby):
        """Tabs with the number of conversations and of unread messages."""
        DiscussChannel = request.env['discuss.channel'].sudo()
        base_domain = self._get_portal_discussion_domain()
        members = request.env['discuss.channel.member'].sudo().search([
            ('partner_id', '=', request.env.user.partner_id.id),
            ('channel_id', 'in', DiscussChannel.search(base_domain).ids)])
        unread_by_channel = {member.channel_id.id: member.message_unread_counter for member in members}
        tabs = []
        for key, tab in sorted(filters.items(), key=lambda item: (item[1].get('sequence', 50), item[0])):
            channel_ids = DiscussChannel.search(expression.AND([base_domain, tab['domain']])).ids
            if not channel_ids and key not in ('all', filterby):
                continue
            tabs.append({
                'key': key,
                'label': tab['label'],
                'count': len(channel_ids),
                'unread': sum(unread_by_channel.get(channel_id, 0) for channel_id in channel_ids),
                'url': self._portal_discussions_url(key, sortby=sortby if sortby != 'date' else None),
            })
        return tabs

    @http.route(['/my/discussions', '/my/discussions/page/<int:page>'], type='http', auth="user", website=True)
    def portal_discussions(self, page=1, sortby=None, filterby=None, search=None, search_in='all', **kwargs):
        DiscussChannel = request.env['discuss.channel'].sudo()
        values = self._prepare_portal_layout_values()
        domain = self._get_portal_discussion_domain()

        searchbar_sortings = {
            'date': {'label': _('Last Activity'), 'order': 'last_interest_dt desc, id desc'},
            'name': {'label': _('Name'), 'order': 'name, id'},
        }
        if sortby not in searchbar_sortings:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        filters = self._portal_discussion_filters()
        if filterby not in filters:
            filterby = 'all'
        domain = expression.AND([domain, filters[filterby]['domain']])

        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('Search in All')},
            'name': {'input': 'name', 'label': _('Name')},
        }
        if search_in not in searchbar_inputs:
            search_in = 'all'
        if search:
            domain = expression.AND([domain, [('name', 'ilike', search)]])

        discussion_count = DiscussChannel.search_count(domain)
        pager = portal_pager(
            url="/my/discussions",
            url_args={'sortby': sortby, 'filterby': filterby, 'search_in': search_in, 'search': search},
            total=discussion_count,
            page=page,
            step=PAGE_SIZE,
        )
        channels = DiscussChannel.search(domain, order=order, limit=PAGE_SIZE, offset=pager['offset'])
        back_url = self._portal_discussions_url(filterby, sortby=sortby if sortby != 'date' else None)

        values.update({
            'channels': channels,
            'discussion_rows': self._prepare_portal_discussion_rows(channels, back_url),
            'discussion_tabs': self._prepare_portal_discussion_tabs(filters, filterby, sortby),
            'page_name': 'discussions',
            'pager': pager,
            'default_url': '/my/discussions',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'filterby': filterby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
        })
        return request.render('woow_odoo_portal_discuss.portal_discuss_channels', values)
