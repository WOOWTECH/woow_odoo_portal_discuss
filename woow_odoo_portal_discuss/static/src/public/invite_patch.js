/** @odoo-module */
// Portal users do not invite people: Odoo refuses it on the server (no write
// access on the conversation) and the invite search only lists employees, so
// the "Invite" header action and the member panel button only lead to errors.
import { threadActionsRegistry } from "@mail/core/common/thread_actions";
import { ChannelMemberList } from "@mail/discuss/core/common/channel_member_list";
import { patch } from "@web/core/utils/patch";
import { user } from "@web/core/user";

const inviteAction = threadActionsRegistry.get("invite-people", null);
if (inviteAction) {
    patch(inviteAction, {
        condition() {
            return Boolean(user.isInternalUser) && super.condition(...arguments);
        },
    });
}

patch(ChannelMemberList.prototype, {
    get portalDiscussCanInvite() {
        return Boolean(user.isInternalUser);
    },
});
