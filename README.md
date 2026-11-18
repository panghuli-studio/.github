# Panghuli Studio community files

This repository owns the public organization profile and shared contribution, issue, pull request, and security reporting guidance. Repository-specific instructions take precedence.

- `profile/README.md`: public organization homepage.
- `CONTRIBUTING.md` and `SECURITY.md`: shared contribution and private vulnerability reporting guidance.
- `.github/`: default Issue and PR templates, plus ownership of this repository.
- `studio.json`: organization identity, public repository descriptions, and the free security baseline.
- `.github/workflows/secret-scan.yml`: reusable gitleaks scan for pull requests and pushes; usage in [docs/secret-scan.md](docs/secret-scan.md).

## Administration

Use Python 3 and GitHub CLI authenticated as `phenix3443`. Preview with `python3 scripts/configure-studio.py`; apply with `python3 scripts/configure-studio.py --apply`. The script reads the declaration, updates changed metadata, applies free security features to active repositories, and verifies the result. Archived repositories and repository visibility are left unchanged. Private repositories receive Dependabot alerts; paid private code and secret scanning are not enabled.

Update the declaration in a PR before changing the corresponding GitHub setting. Keep credentials, private project metadata, and runtime inventory out of this public repository.
