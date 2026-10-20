# woow_odoo_portal_discuss

Odoo 18 模組 `woow_odoo_portal_discuss`：portal 的「My Discussions」頁面模板（`portal_discuss_channels`），`odoo_booking_reservation`（`WOOWTECH/Woow_odoo_internal_booking`）相依它。

## 來源與改名

- 原技術名 `cs_portal_discuss` 18.0.1.0.0，來源 well-101 站上，2026-10-19 收編（woow_paas_platform#1874），內容雜湊 `72e65f82`。
- 18.0.1.0.1 改為正式名 `woow_odoo_portal_discuss`，內容不變（woow_paas_platform#1878）。
- 已安裝舊名的資料庫，搬遷時先用 `standalone-odoo-migrate` 的 `scripts/target/rename-module.sql`（或 `restore.sh --rename-module cs_portal_discuss:woow_odoo_portal_discuss`）在 DB 改名，再用本模組 `-u`。
