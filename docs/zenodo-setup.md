# Zenodo DOI 申請步驟

Zenodo 給 GitHub repo 永久 DOI（每次 release 自動更新版本 DOI）。Mercury MCP 需要兩個 DOI：
- 軟體（這個 repo）
- 資料集（觀測 JSON 檔案）

## Step 1: 連 Zenodo 跟 GitHub（一次性，5 分鐘）

1. 開 https://zenodo.org/account/login/
2. 點 **"Log in with GitHub"** — 用 norika1207-lab 帳號授權
3. 進 https://zenodo.org/account/settings/github/
4. 找到 `norika1207-lab/mercury-mcp` repo
5. 把右邊的 toggle switch 打開 (OFF → ON)

完成後 Zenodo 會監聽這個 repo 的 GitHub Release。

## Step 2: 建第一個 Release（觸發 DOI 分配）

在本機：

```bash
cd <your-clone>/mercury-mcp
git tag -a v0.1.0 -m "Mercury MCP v0.1 — Initial release with 23-model database"
git push origin v0.1.0
```

然後在 GitHub web 上：
1. 開 https://github.com/norika1207-lab/mercury-mcp/releases/new
2. Choose tag: `v0.1.0`
3. Release title: `v0.1.0 — 23-LLM cross-architecture observation database, 7 MCP tools`
4. Description: 複製 README 的 "Headline findings" 段
5. 按 **"Publish release"**

Zenodo 會自動 archive、給 DOI（通常 1-2 分鐘內）。

## Step 3: 取得 DOI + 更新 README

幾分鐘後：
1. 回到 https://zenodo.org/account/settings/github/
2. 找到 mercury-mcp，會看到旁邊有 DOI 連結
3. 複製 DOI（格式：`10.5281/zenodo.XXXXXXX`）

然後我幫你把 DOI 填回 README 跟 CITATION.cff（取代 `XXXXXXX` placeholder）。

## Step 4: （可選）資料集另開一個 DOI

如果未來想讓論文 cite 「資料集」跟「軟體」分開（學術界比較喜歡這樣）：

1. 把 `data/heat-summaries/*.json` 跟 `data/layer-fingerprints/*.json` 打包成 `.zip`
2. 開 https://zenodo.org/uploads/new
3. Upload type: **Dataset**
4. Title: `Mercury: 23-LLM Cross-Architecture Hot-Dim Observation Data`
5. 填 metadata（作者、License: CC-BY-4.0、Related identifier: 軟體 DOI）
6. Publish → 拿到資料集專用 DOI

## 預期結果

完成後 README 會有：

```
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
```

論文 cite Mercury 時可以寫 `@dataset{...doi=10.5281/zenodo.XXXXXXX}`，正式可追溯。
