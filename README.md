# Woow Odoo Portal Discussions

Odoo 18 module `woow_odoo_portal_discuss`: portal users find and open their
Discuss conversations from the portal.

[繁體中文說明](README_zh-TW.md)

Odoo 18 already lets portal users chat on the Discuss page
`/discuss/channel/<id>` (messages, files, emojis). What it lacks is the way in;
this module adds it:

- A **Discussions** card on the portal home (`/my`) and the list
  **`/my/discussions`**: the user's direct messages, group chats and the
  channels open to portal users (channel access group *Portal*) that they
  joined and keep pinned, with the same rule as the Discuss sidebar (a chat
  the user closed comes back with the next message).
- **Tabs** All / Direct Message / Group / Channel (`?filterby=all|chat|group|channel`)
  with the unread count of each; empty tabs are hidden (the open one stays).
- Each row: the other person's name and avatar for a direct message (signed
  avatar URL, readable by the portal user), the last message (`You: …` for
  one's own), its date and the unread count. Sorted by last activity or name;
  search by name; 20 per page.
- A **back bar** on the Discuss page opened from the list
  (`/discuss/channel/<id>?discussions=1`), rendered on the server (no inline
  script). It returns to the tab the conversation was opened from; another
  module may pass `&back=/my/...` (only portal paths with a simple query
  string are accepted, anything else falls back to `/my/discussions`).
- Opened from the list, the conversation shows at once: no guest welcome page
  and no automatic full-screen video.
- The **Invite** buttons are hidden for portal users. This is cosmetic: Odoo
  itself refuses invitations by portal users (no write access on the
  conversation) and only lists employees in the invite search; a test keeps
  that true.

## Install

1. Put `woow_odoo_portal_discuss` in the addons path. Depends on `portal` and
   `mail` only. zh_TW translations included.
2. Install **Portal Discussions**.

It cannot be installed together with `cs_portal_discuss` (manifest
`excludes`): both serve `/my/discussions`.

The list page keeps the template id `woow_odoo_portal_discuss.portal_discuss_channels`
and the route `portal_discussions(page=1, **kw)` of 18.0.1.0.1, which
`odoo_booking_reservation`
([Woow_odoo_internal_booking](https://github.com/WOOWTECH/Woow_odoo_internal_booking))
extends; upgrading from 18.0.1.0.1 is a plain `-u woow_odoo_portal_discuss`.

### Replacing cs_portal_discuss

Two different modules carry the technical name `cs_portal_discuss`:

1. **The Code Sparks based one** (Portal Discuss, Chat & Meetings Hub). It has
   no tables of its own: only pages, routes and translations change,
   conversations are not touched and the URLs stay the same. With both modules
   in the addons path, in a maintenance window:

   ```
   odoo shell -c <conf> -d <db> --no-http < scripts/replace_cs_portal_discuss.py
   ```

   It updates the module list, uninstalls `cs_portal_discuss`, installs
   `woow_odoo_portal_discuss` and upgrades `woow_ai_contact_portal_discuss`
   when present (its AI tab extends the list page). Safe to run again.
2. **A small self-made one** (only the list template; the origin of this
   repository) that other modules such as `odoo_booking_reservation` depend
   on. Uninstalling it would also uninstall those modules and their data, so
   the script refuses. Rename the module in the database instead
   (`ir_module_module`, `ir_model_data`, dependencies, view keys), then
   `-u woow_odoo_portal_discuss`.

## History

- 18.0.1.0.0: `cs_portal_discuss` 18.0.1.0.0 taken over from a site
  (a self-made list template).
- 18.0.1.0.1: renamed to `woow_odoo_portal_discuss`, content unchanged.
- 18.0.2.0.0: the whole portal discussions feature (this README), replacing
  the Code Sparks based `cs_portal_discuss` as well.

## Extending

`CustomerPortal` methods other modules may override (call `super()`):

| Method | Use |
|---|---|
| `_portal_discussion_filters()` | tabs: `{key: {'label', 'domain', 'sequence'}}`, `all` must stay |
| `_prepare_portal_discussion_rows(channels, back_url=None)` | display data of the rows (title, avatar_url, type_label, preview, last_date, unread, url) |
| `_get_portal_discussion_domain()` | which conversations are listed |

The route `portal_discussions` returns a lazy response: add values with
`response.qcontext` after `super()`. Example:
[`woow_ai_contact_portal_discuss`](https://github.com/WOOWTECH/Woow_odoo_discuss_ai)
adds an "AI Assistants" tab.

## Tests

`--test-tags /woow_odoo_portal_discuss` (7 HttpCase tests: own conversations
only with signed avatars, unpinned chats hidden, unknown parameters, back bar
and its validation, tabs and back to the tab, home card counter, no portal
invitations on the server).

## License

LGPL-3. This module is a modified version of `cs_portal_discuss` by Code Sparks
(https://code-sparks.odoo.com), licensed under LGPL-3. WOOWTECH rewrote most of it;
see `woow_odoo_portal_discuss/NOTICE` for the origin and the changes.
