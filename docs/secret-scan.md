# Secret scan workflow

`.github/workflows/secret-scan.yml` is a reusable workflow that runs the [gitleaks](https://github.com/gitleaks/gitleaks) binary over the commits of the calling event and fails the job when it finds a secret. It runs the program directly, so it needs no `gitleaks-action` license key.

## Calling it

Add this file to a repository as `.github/workflows/secret-scan.yml`:

```yaml
name: Secret scan
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read
jobs:
  gitleaks:
    uses: panghuli-studio/.github/.github/workflows/secret-scan.yml@main
```

`@main` follows gitleaks upgrades made here; use a commit hash instead to control when a repository takes them. The job runs on the organization's self-hosted runner, which serves private repositories only. Pass `with: runs-on: <label>` to use another runner.

## What is scanned

| Event | Commits |
| --- | --- |
| `pull_request` | The pull request's commits (`base..head`). |
| `push` | The pushed commits (`before..after`). A new branch, or a force push whose previous tip is gone, scans the whole history of the new tip. |
| Anything else | The whole history of the triggering commit. |

Every commit in the range is scanned, so a secret added in one commit and deleted in a later one still fails the job: it stays readable in history.

The log and the job summary list the rule, file, line, commit and fingerprint of each finding. gitleaks runs with `--redact` and the report template has no field for the matched text, so the secret itself is never printed.

## Handling a finding

1. Revoke or rotate the secret with its provider. Do this first: the value is already in a pushed commit.
2. On a pull request branch, rewrite the commits so the secret is gone, then force-push.
3. For a false positive, or a revoked secret that stays in history, add the reported fingerprint to `.gitleaksignore` in the repository root, with a comment line giving the reason:

   ```text
   # Example key from the vendor's documentation, not a credential
   <commit>:<file>:<rule>:<line>
   ```

## Repository configuration

- `.gitleaks.toml` in the repository root replaces the default rules when present. Start it with `[extend]` and `useDefault = true` to keep the defaults and add allowlists or rules.
- `.gitleaksignore` in the repository root lists fingerprints to skip.

Both files are read from the checked-out commit, so a pull request that changes them changes its own scan. Review such changes like code.

## Upgrading gitleaks

1. Pick a release from <https://github.com/gitleaks/gitleaks/releases>.
2. Open its `gitleaks_<version>_checksums.txt` and copy the SHA-256 of `gitleaks_<version>_linux_x64.tar.gz`.
3. Set `GITLEAKS_VERSION` and `GITLEAKS_SHA256` in the workflow to the new values in one PR.

The job refuses to run a download whose checksum differs.
