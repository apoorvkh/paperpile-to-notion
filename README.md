# Paperpile to Notion Sync Tool

A simple tool to automatically sync your Paperpile library with a Notion database.

To use, please (1) fork or template this repo, and (2) follow the instructions at [seba-1511's README](https://github.com/seba-1511/sync-paperpile-notion/blob/5af47cfa94cf957fd9dd3010ad42d6dd41fd38fc/README.md). EXCEPT that your Notion database should have the following column titles/types:

```
"Reference ID": title
"Title": rich_text
"Authors": rich_text
"Year": rich_text
```

My Paperpile BibTeX settings are as follows:

<img width="588" alt="image" src="https://github.com/apoorvkh/paperpile-to-notion/assets/7005565/d3e807c9-21fb-4761-bab0-824df20c36e2">

This repository should be stable, but I plan on adding more features in the future.

---

Inspired by [jmuchovej/paperpile-notion](https://github.com/jmuchovej/paperpile-notion) and [seba-1511/sync-paperpile-notion](https://github.com/seba-1511/sync-paperpile-notion). Actually, this is effectively a fork/rewrite of seba-1511's repository, so much original credit goes to them.
