# Woow Odoo Portal Discussions（portal 討論區）

Odoo 18 模組 `woow_odoo_portal_discuss`：讓 portal 用戶從 portal 找到並打開自己的 Discuss 對話。

[English](README.md)

Odoo 18 原生就讓 portal 用戶在 `/discuss/channel/<id>` 聊天（訊息、檔案、表情符號），缺的是入口；這個模組補上：

- portal 首頁（`/my`）的**討論區**卡片與清單 **`/my/discussions`**：使用者的私訊、群組，以及開放給 portal（頻道存取群組為 *Portal*）且已加入的頻道；只列置頂中的對話，與 Discuss 側欄同規則（使用者關掉的私訊，有新訊息時會回來）。
- **分頁**：全部／私訊／群組／頻道（`?filterby=all|chat|group|channel`），各自顯示未讀數；沒內容的分頁不顯示（開著的那個保留）。
- 每一列：私訊顯示對方名字與頭像（簽名網址，portal 用戶讀得到）、最後一則訊息（自己的顯示「您：…」）、時間與未讀數；依最近活動或名稱排序、可搜尋名稱、每頁 20 筆。
- 從清單打開的對話頁上方有**返回列**（`/discuss/channel/<id>?discussions=1`），由伺服器產生（沒有內嵌 script），回到進來時的分頁；其他模組可帶 `&back=/my/...`（只接受 portal 路徑加簡單查詢字串，其他一律回 `/my/discussions`）。
- 從清單打開時直接顯示對話：不出現訪客歡迎頁、不自動進全螢幕視訊。
- 對 portal 用戶隱藏**邀請**按鈕。只是畫面上的處理：Odoo 本身就不讓 portal 用戶邀請（對對話沒有寫入權限），邀請搜尋也只列員工；有測試確保這點。

## 安裝

1. 把 `woow_odoo_portal_discuss` 放進 addons path，只相依 `portal`、`mail`，內含繁體中文翻譯。
2. 安裝 **Portal Discussions**。

不能和 `cs_portal_discuss` 同時安裝（manifest `excludes`），兩者都提供 `/my/discussions`。

清單頁保留 18.0.1.0.1 的模板 id `woow_odoo_portal_discuss.portal_discuss_channels` 與路由 `portal_discussions(page=1, **kw)`，`odoo_booking_reservation`（[Woow_odoo_internal_booking](https://github.com/WOOWTECH/Woow_odoo_internal_booking)）擴充了它們；從 18.0.1.0.1 升級只要 `-u woow_odoo_portal_discuss`。

### 取代 cs_portal_discuss

技術名叫 `cs_portal_discuss` 的有兩種不同模組：

1. **Code Sparks 版**（Portal Discuss, Chat & Meetings Hub）。沒有自己的資料表：只換頁面、路由與翻譯，對話不受影響，網址不變。兩個模組都在 addons path 時，在維護時段執行：

   ```
   odoo shell -c <conf> -d <db> --no-http < scripts/replace_cs_portal_discuss.py
   ```

   它會更新模組清單、卸載 `cs_portal_discuss`、安裝 `woow_odoo_portal_discuss`，有裝 `woow_ai_contact_portal_discuss` 時再升級它（它的 AI 分頁掛在清單頁上）。重跑無害。
2. **自製小模組**（只有清單模板，就是本 repo 的起點），有其他模組（例如 `odoo_booking_reservation`）相依它。卸載會連帶卸載那些模組與資料，所以腳本會拒絕執行；請改在資料庫內改名（`ir_module_module`、`ir_model_data`、相依、view key），再 `-u woow_odoo_portal_discuss`。

## 版本紀錄

- 18.0.1.0.0：從某站收編 `cs_portal_discuss` 18.0.1.0.0（自製清單模板）。
- 18.0.1.0.1：改名為 `woow_odoo_portal_discuss`，內容不變。
- 18.0.2.0.0：完整的 portal 討論區功能（本 README），同時取代 Code Sparks 版 `cs_portal_discuss`。

## 擴充

其他模組可覆寫的 `CustomerPortal` 方法（記得呼叫 `super()`）：

| 方法 | 用途 |
|---|---|
| `_portal_discussion_filters()` | 分頁：`{key: {'label', 'domain', 'sequence'}}`，`all` 必須保留 |
| `_prepare_portal_discussion_rows(channels, back_url=None)` | 每一列的顯示資料（title、avatar_url、type_label、preview、last_date、unread、url） |
| `_get_portal_discussion_domain()` | 要列出哪些對話 |

路由 `portal_discussions` 回傳 lazy response，可在 `super()` 之後用 `response.qcontext` 加值。範例：[`woow_ai_contact_portal_discuss`](https://github.com/WOOWTECH/Woow_odoo_discuss_ai) 加上「AI 助理」分頁。

## 測試

`--test-tags /woow_odoo_portal_discuss`（7 個 HttpCase：只列自己的對話且頭像簽名可讀、取消置頂的不列、不認得的參數、返回列與網址檢查、分頁與回到分頁、首頁卡片計數、portal 用戶在伺服器端無法邀請）。

## 授權

LGPL-3。本模組改自 Code Sparks 的 `cs_portal_discuss`（https://code-sparks.odoo.com，LGPL-3），WOOWTECH 改寫了大部分內容；來源與修改紀錄見 `woow_odoo_portal_discuss/NOTICE`。
