# -*- coding: utf-8 -*-
import re

from markupsafe import Markup

from odoo import fields
from odoo.exceptions import AccessError
from odoo.tests import HttpCase, tagged, new_test_user


@tagged('post_install', '-at_install')
class TestPortalDiscussions(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.portal = new_test_user(cls.env, 'wpd_portal', groups='base.group_portal', name='Portal Pat')
        cls.other_portal = new_test_user(cls.env, 'wpd_other', groups='base.group_portal', name='Other Olga')
        cls.internal = new_test_user(cls.env, 'wpd_internal', groups='base.group_user', name='Internal Ivy')
        Channel = cls.env['discuss.channel']
        cls.chat = Channel.with_user(cls.internal).channel_get([cls.portal.partner_id.id]).with_user(cls.env.user)
        cls.chat.with_user(cls.internal).message_post(
            body=Markup('Hello <b>Pat</b>, your order shipped'), message_type='comment')
        cls.portal_channel = Channel.create({
            'name': 'Customer News', 'channel_type': 'channel',
            'group_public_id': cls.env.ref('base.group_portal').id})
        cls.portal_channel._add_members(partners=cls.portal.partner_id)
        cls.internal_channel = Channel.create({
            'name': 'Staff Only', 'channel_type': 'channel',
            'group_public_id': cls.env.ref('base.group_user').id})
        cls.internal_channel._add_members(partners=cls.portal.partner_id)
        cls.other_chat = Channel.with_user(cls.internal).channel_get([cls.other_portal.partner_id.id]).with_user(cls.env.user)

    def _list(self, query=''):
        response = self.url_open('/my/discussions' + query)
        self.assertEqual(response.status_code, 200, query)
        return response.text

    def test_list_shows_own_conversations_only(self):
        self.authenticate('wpd_portal', 'wpd_portal')
        page = self._list()
        self.assertIn('/discuss/channel/%s?discussions=1' % self.chat.id, page)
        self.assertIn('/discuss/channel/%s?discussions=1' % self.portal_channel.id, page)
        self.assertNotIn('/discuss/channel/%s?' % self.internal_channel.id, page)
        self.assertNotIn('/discuss/channel/%s?' % self.other_chat.id, page)
        # a chat is named after the other person, with the last message and the unread count
        self.assertIn('Internal Ivy', page)
        self.assertIn('Hello Pat, your order shipped', page)
        self.assertIn('o_portal_discussion_unread', page)
        # the other person's avatar is readable by the portal user (signed URL)
        avatar = re.search(r'src="(/web/image/res\.partner/%s/avatar_128\?access_token=[^"]+)"' % self.internal.partner_id.id, page)
        self.assertTrue(avatar, 'signed avatar URL')
        image = self.url_open(avatar.group(1).replace('&amp;', '&'))
        self.assertEqual(image.status_code, 200)
        placeholder = self.url_open('/web/image/res.partner/%s/avatar_128' % self.internal.partner_id.id)
        self.assertNotEqual(image.content, placeholder.content, 'without the token the portal user gets the placeholder')

    def test_unpinned_chat_is_hidden_until_a_new_message(self):
        member = self.chat.channel_member_ids.filtered(lambda m: m.partner_id == self.portal.partner_id)
        member.unpin_dt = fields.Datetime.now()
        self.env.flush_all()
        self.authenticate('wpd_portal', 'wpd_portal')
        self.assertNotIn('/discuss/channel/%s?' % self.chat.id, self._list())

    def test_unknown_parameters_fall_back_to_defaults(self):
        self.authenticate('wpd_portal', 'wpd_portal')
        for query in ('?sortby=bogus', '?filterby=bogus', '?search_in=bogus&search=x',
                      '?sortby=name&filterby=chat', '?search=%25', '/page/99'):
            self._list(query)
        page = self._list('?filterby=chat')
        self.assertIn('/discuss/channel/%s?discussions=1' % self.chat.id, page)
        self.assertNotIn('/discuss/channel/%s?' % self.portal_channel.id, page)

    def test_back_bar_is_rendered_on_the_server(self):
        self.authenticate('wpd_portal', 'wpd_portal')
        page = self.url_open('/discuss/channel/%s?discussions=1' % self.chat.id).text
        self.assertIn('id="o_portal_discuss_back_bar"', page)
        self.assertIn('href="/my/discussions"', page)
        self.assertIn('o_portal_discuss_has_back_bar', page)
        self.assertIn('href="/my/ai"', self.url_open('/discuss/channel/%s?discussions=1&back=/my/ai' % self.chat.id).text)
        for unsafe in ('https://evil.example', '//evil.example', '/web/login', 'javascript:alert(1)', '/my/../web'):
            page = self.url_open('/discuss/channel/%s?discussions=1&back=%s' % (self.chat.id, unsafe)).text
            self.assertIn('href="/my/discussions"', page, unsafe)
            self.assertNotIn('evil.example', page)
        plain = self.url_open('/discuss/channel/%s' % self.chat.id).text
        self.assertNotIn('o_portal_discuss_back_bar', plain)
        self.assertNotIn('o_portal_discuss_has_back_bar', plain)

    def test_home_card(self):
        self.authenticate('wpd_portal', 'wpd_portal')
        self.assertIn('href="/my/discussions"', self.url_open('/my').text)
        counters = self.make_jsonrpc_request('/my/counters', {'counters': ['portal_discussion_count']})
        self.assertEqual(counters['portal_discussion_count'], 2)

    def test_tabs_and_back_to_the_tab(self):
        self.authenticate('wpd_portal', 'wpd_portal')
        page = self._list()
        tabs = re.findall(r'data-tab="([a-z_]+)"', page)
        # empty tabs (no group conversation) are hidden
        self.assertEqual(tabs, ['all', 'chat', 'channel'])
        self.assertIn('o_portal_discussion_tab_unread', page)
        # an empty tab stays visible while it is open
        self.assertEqual(re.findall(r'data-tab="([a-z_]+)"', self._list('?filterby=group')),
                         ['all', 'chat', 'group', 'channel'])
        # a conversation opened from a tab leads back to that tab
        page = self._list('?filterby=chat')
        url = '/discuss/channel/%s?discussions=1&amp;back=/my/discussions%%3Ffilterby%%3Dchat' % self.chat.id
        self.assertIn(url, page)
        chat_page = self.url_open(url.replace('&amp;', '&')).text
        self.assertIn('href="/my/discussions?filterby=chat"', chat_page)
        # from "All" the conversation leads back to the list itself
        self.assertIn('/discuss/channel/%s?discussions=1"' % self.chat.id, self._list())

    def test_portal_user_cannot_invite_on_the_server(self):
        # the hidden "Invite" buttons are only cosmetic: Odoo itself refuses it
        group = self.env['discuss.channel'].with_user(self.internal).create_group(
            partners_to=[self.portal.partner_id.id]).with_user(self.env.user)
        with self.assertRaises(AccessError):
            group.with_user(self.portal).add_members(partner_ids=[self.other_portal.partner_id.id])
        found = self.env['res.partner'].with_user(self.portal).search_for_channel_invite('Ivy', channel_id=group.id)
        self.assertEqual(found['count'], 0)
