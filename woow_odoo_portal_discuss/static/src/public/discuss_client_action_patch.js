/** @odoo-module */
// Portions derived from cs_portal_discuss by Code Sparks (https://code-sparks.odoo.com), LGPL-3.
// Modified by WOOWTECH, 2026. See NOTICE.
// Opened from the portal list (/discuss/channel/<id>?discussions=1): show the
// conversation at once, without the guest welcome page and without starting
// the full-screen video view. Every access is optional: if these Discuss
// internals change in an Odoo update, Odoo's own behaviour stays.
import { DiscussClientAction } from "@mail/core/public_web/discuss_client_action";
import "@mail/discuss/call/public/discuss_client_action_patch";
import { browser } from "@web/core/browser/browser";
import { patch } from "@web/core/utils/patch";

function openedFromPortalList() {
    return new URLSearchParams(browser.location.search).has("discussions");
}

patch(DiscussClientAction.prototype, {
    setup() {
        super.setup(...arguments);
        if (!openedFromPortalList()) {
            return;
        }
        const thread = this.store?.discuss_public_thread;
        if (thread?.defaultDisplayMode === "video_full_screen") {
            thread.defaultDisplayMode = "";
        }
        if (this.publicState) {
            this.publicState.welcome = false;
        }
    },
});
