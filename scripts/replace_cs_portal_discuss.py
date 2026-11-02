# Replace cs_portal_discuss by woow_odoo_portal_discuss in one database.
#
#   odoo shell -c <conf> -d <db> --no-http < scripts/replace_cs_portal_discuss.py
#
# Both modules must be in the addons path. Neither has its own tables: only
# pages, routes and translations change, conversations are not touched, and
# the URLs stay the same (/my/discussions, /discuss/channel/<id>?discussions=1).
# Run it in a maintenance window: between the uninstall and the install the
# portal has no discussion list. Safe to run again.
import logging

_logger = logging.getLogger('replace_cs_portal_discuss')
Module = env['ir.module.module']
Module.update_list()  # new module known, dependencies of the bridge refreshed


def state(name):
    return Module.search([('name', '=', name)]).state


old = Module.search([('name', '=', 'cs_portal_discuss'), ('state', '=', 'installed')])
# Uninstalling a module also uninstalls the modules depending on it, with
# their data. Some sites have a small self-made module named
# cs_portal_discuss that other modules depend on (e.g. odoo_booking_reservation):
# there the module must be renamed in the database instead (see README).
dependents = Module.search([
    ('state', 'in', ('installed', 'to upgrade')),
    ('dependencies_id.name', '=', 'cs_portal_discuss'),
])
if old and dependents:
    raise SystemExit('stopped: %s depend on cs_portal_discuss; uninstalling it would remove them and their '
                     'data. Rename the module in the database instead (README).' % ', '.join(dependents.mapped('name')))
if old:
    old.button_immediate_uninstall()
    print('cs_portal_discuss: uninstalled')
new = Module.search([('name', '=', 'woow_odoo_portal_discuss')])
if not new:
    raise SystemExit('woow_odoo_portal_discuss is not in the addons path')
if new.state != 'installed':
    new.button_immediate_install()
    print('woow_odoo_portal_discuss: installed')
# woow_ai_contact_portal_discuss (AI contacts tab): its page extension of the
# old list was removed with cs_portal_discuss; an upgrade recreates it on the
# new list
bridge = Module.search([('name', '=', 'woow_ai_contact_portal_discuss'), ('state', '=', 'installed')])
if bridge:
    bridge.button_immediate_upgrade()
    print('woow_ai_contact_portal_discuss: upgraded')
env.cr.commit()
print('states:', {name: state(name) for name in (
    'cs_portal_discuss', 'woow_odoo_portal_discuss', 'woow_ai_contact_portal_discuss')})
