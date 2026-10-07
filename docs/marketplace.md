# RhapsodIA Marketplace

RhapsodIA can be consumed directly from its remote Git repository.  
A manual `git clone` is not required.

Repository:

```text
https://github.com/ginmp8/rhapsodia
```

Marketplace name:

```text
rhapsodia
```

Plugin name:

```text
rhapsodia
```

---

## GitHub Copilot CLI

### Add the marketplace

```bash
copilot plugin marketplace add ginmp8/rhapsodia
```

Track a specific branch:

```bash
copilot plugin marketplace add ginmp8/rhapsodia#main
```

Pin to a specific release:

```bash
copilot plugin marketplace add ginmp8/rhapsodia#v0.6.0
```

### List registered marketplaces

```bash
copilot plugin marketplace list
```

### Browse RhapsodIA

```bash
copilot plugin marketplace browse rhapsodia
```

JSON output:

```bash
copilot plugin marketplace browse rhapsodia --json
```

### Install RhapsodIA

```bash
copilot plugin install rhapsodia@rhapsodia
```

### List installed plugins

```bash
copilot plugin list
```

### Refresh the RhapsodIA marketplace

This refreshes the marketplace catalog:

```bash
copilot plugin marketplace update rhapsodia
```

Refresh all registered marketplaces:

```bash
copilot plugin marketplace update
```

`refresh` is also supported as an alias:

```bash
copilot plugin marketplace refresh rhapsodia
```

### Update RhapsodIA

```bash
copilot plugin update rhapsodia
```

Update all installed plugins:

```bash
copilot plugin update --all
```

### Disable RhapsodIA

```bash
copilot plugin disable rhapsodia
```

### Enable RhapsodIA

```bash
copilot plugin enable rhapsodia
```

### Uninstall RhapsodIA

```bash
copilot plugin uninstall rhapsodia
```

Aliases are also available:

```bash
copilot plugin remove rhapsodia
copilot plugin rm rhapsodia
```

### Remove the marketplace

```bash
copilot plugin marketplace remove rhapsodia
```

If plugins from the marketplace are still installed:

```bash
copilot plugin marketplace remove rhapsodia --force
```

`--force` also uninstalls plugins installed from that marketplace.

---

## OpenAI Codex / ChatGPT

The Codex CLI can register, inspect, refresh, and remove marketplace sources.

Plugin installation is currently performed through the Plugins browser rather than a `codex plugin install` CLI command.

### Add the marketplace

```bash
codex plugin marketplace add ginmp8/rhapsodia
```

Track `main` explicitly:

```bash
codex plugin marketplace add ginmp8/rhapsodia --ref main
```

Pin to a release:

```bash
codex plugin marketplace add ginmp8/rhapsodia --ref v0.6.0
```

A full Git URL can also be used:

```bash
codex plugin marketplace add https://github.com/ginmp8/rhapsodia.git
```

### List marketplaces

```bash
codex plugin marketplace list
```

### Refresh the RhapsodIA marketplace

```bash
codex plugin marketplace upgrade rhapsodia
```

Refresh every configured marketplace:

```bash
codex plugin marketplace upgrade
```

### Install RhapsodIA

Start Codex:

```bash
codex
```

Then open the plugin browser:

```text
/plugins
```

Select:

```text
RhapsodIA
```

and choose:

```text
Install plugin
```

The same marketplace can also be browsed from the ChatGPT desktop app through the Plugins Directory.

### Remove the marketplace

```bash
codex plugin marketplace remove rhapsodia
```

### Repository-level enable/disable

For repository-local control, use `.codex/config.toml`:

```toml
[plugins."rhapsodia@rhapsodia"]
enabled = true
```

Disable it with:

```toml
[plugins."rhapsodia@rhapsodia"]
enabled = false
```

---

## Claude Code

### Add the marketplace

```bash
claude plugin marketplace add ginmp8/rhapsodia
```

Track a specific branch:

```bash
claude plugin marketplace add ginmp8/rhapsodia#main
```

Pin to a release:

```bash
claude plugin marketplace add ginmp8/rhapsodia#v0.6.0
```

A full Git URL can also be used:

```bash
claude plugin marketplace add https://github.com/ginmp8/rhapsodia.git
```

### List marketplaces

```bash
claude plugin marketplace list
```

### Install RhapsodIA

User scope:

```bash
claude plugin install rhapsodia@rhapsodia
```

Explicit user scope:

```bash
claude plugin install rhapsodia@rhapsodia --scope user
```

Project scope:

```bash
claude plugin install rhapsodia@rhapsodia --scope project
```

Local repository scope:

```bash
claude plugin install rhapsodia@rhapsodia --scope local
```

### Add the marketplace and install interactively in one step

Inside a Claude Code session:

```text
/plugin install rhapsodia --marketplace ginmp8/rhapsodia
```

### List installed plugins

```bash
claude plugin list
```

### Show RhapsodIA details

```bash
claude plugin details rhapsodia
```

### Refresh the marketplace catalog

```bash
claude plugin marketplace update rhapsodia
```

Refresh every marketplace catalog:

```bash
claude plugin marketplace update
```

> Refreshing every marketplace catalog does not automatically mean every installed plugin is upgraded.

### Update RhapsodIA

```bash
claude plugin update rhapsodia@rhapsodia
```

### Disable RhapsodIA

```bash
claude plugin disable rhapsodia@rhapsodia
```

### Enable RhapsodIA

```bash
claude plugin enable rhapsodia@rhapsodia
```

### Uninstall RhapsodIA

User scope:

```bash
claude plugin uninstall rhapsodia@rhapsodia
```

Project scope:

```bash
claude plugin uninstall rhapsodia@rhapsodia --scope project
```

Local scope:

```bash
claude plugin uninstall rhapsodia@rhapsodia --scope local
```

### Remove unused plugin dependencies

```bash
claude plugin prune
```

### Remove the marketplace

```bash
claude plugin marketplace remove rhapsodia
```

---

## Cursor

> `agent` is the current primary Cursor CLI command.  
> `cursor-agent` remains available as a backward-compatible alias.

### Add the marketplace

```bash
agent plugin marketplace add https://github.com/ginmp8/rhapsodia
```

Using the legacy-compatible CLI name:

```bash
cursor-agent plugin marketplace add https://github.com/ginmp8/rhapsodia
```

### Track a specific Git ref

```bash
agent plugin marketplace add --git-ref main https://github.com/ginmp8/rhapsodia
```

Pin to a release:

```bash
agent plugin marketplace add --git-ref v0.6.0 https://github.com/ginmp8/rhapsodia
```

### List marketplaces

```bash
agent plugin marketplace list
```

### Refresh RhapsodIA

```bash
agent plugin marketplace update rhapsodia
```

### Remove the marketplace

```bash
agent plugin marketplace remove rhapsodia
```

### Install RhapsodIA

Cursor does not currently provide a supported non-interactive equivalent to:

```text
agent plugin install rhapsodia
```

Start Cursor Agent:

```bash
agent
```

Then open plugin management:

```text
/plugin
```

Open the marketplace, select **RhapsodIA**, and install it.

Alternatively, use the Cursor IDE:

```text
Settings
→ Plugins
→ RhapsodIA
→ Install
```

For plugins published in Cursor's public marketplace, the editor also supports:

```text
/add-plugin
```

### Team Marketplace

For an organization-wide marketplace:

```text
Cursor Dashboard
→ Plugins & MCPs
→ Team Marketplaces
→ Add Marketplace
→ Import from Repo
```

Repository:

```text
https://github.com/ginmp8/rhapsodia
```

Enable **Auto Refresh** if the marketplace should automatically re-index changes pushed to its tracked GitHub branch.

---

## Recommended Installation

### GitHub Copilot

```bash
copilot plugin marketplace add ginmp8/rhapsodia
copilot plugin install rhapsodia@rhapsodia
```

### OpenAI Codex

```bash
codex plugin marketplace add ginmp8/rhapsodia
codex
```

Then:

```text
/plugins → RhapsodIA → Install plugin
```

### Claude Code

```bash
claude plugin marketplace add ginmp8/rhapsodia
claude plugin install rhapsodia@rhapsodia
```

### Cursor

```bash
agent plugin marketplace add https://github.com/ginmp8/rhapsodia
agent
```

Then:

```text
/plugin → RhapsodIA → Install
```

---

## Updating RhapsodIA

### GitHub Copilot

```bash
copilot plugin marketplace update rhapsodia
copilot plugin update rhapsodia
```

### OpenAI Codex

```bash
codex plugin marketplace upgrade rhapsodia
```

Then use the Plugins browser when an installation/update action is required.

### Claude Code

```bash
claude plugin marketplace update rhapsodia
claude plugin update rhapsodia@rhapsodia
```

### Cursor

```bash
agent plugin marketplace update rhapsodia
```

For Team Marketplaces hosted on GitHub, **Auto Refresh** can keep the marketplace index synchronized with the configured branch.

---

## Pinning a Release

Use release pinning when reproducibility is more important than automatically following the latest marketplace version.

### Copilot

```bash
copilot plugin marketplace add ginmp8/rhapsodia#v0.6.0
```

### Codex

```bash
codex plugin marketplace add ginmp8/rhapsodia --ref v0.6.0
```

### Claude Code

```bash
claude plugin marketplace add ginmp8/rhapsodia#v0.6.0
```

### Cursor

```bash
agent plugin marketplace add --git-ref v0.6.0 https://github.com/ginmp8/rhapsodia
```

For normal installations that should follow the latest RhapsodIA release, track the default branch instead of pinning a release tag.