import argparse
import json
from pathlib import Path
import subprocess


def api(path, method="GET", payload=None):
    command = ["gh", "api", "--method", method, path]
    if payload is not None:
        command += ["--input", "-"]
    result = subprocess.run(command, input=json.dumps(payload) if payload is not None else None,
                            text=True, capture_output=True, check=True)
    return json.loads(result.stdout) if result.stdout.strip() else {}


def reconcile(apply):
    config = json.loads((Path(__file__).resolve().parents[1] / "studio.json").read_text())
    organization = config["organization"]
    if api("user")["login"] != "phenix3443":
        raise SystemExit("Use the phenix3443 account for studio administration.")
    profile = api(f"orgs/{organization}")
    changes = {key: value for key, value in config["profile"].items() if profile.get(key) != value}
    if changes:
        print("Organization profile:", json.dumps(changes))
        if apply:
            updated = api(f"orgs/{organization}", "PATCH", changes)
            assert all(updated.get(key) == value for key, value in changes.items())
    for name, desired in config["repositories"].items():
        repo = api(f"repos/{organization}/{name}")
        assert not repo["private"], "Only public repository metadata belongs in studio.json."
        changes = {key: value for key, value in desired.items() if repo.get(key) != value}
        if changes:
            print(name + ":", json.dumps(changes))
            if apply:
                updated = api(f"repos/{organization}/{name}", "PATCH", changes)
                assert all(updated.get(key) == value for key, value in changes.items())
    page = 1
    while True:
        repos = api(f"orgs/{organization}/repos?type=all&per_page=100&page={page}")
        for repo in repos:
            if repo["archived"]:
                continue
            path = "repos/" + repo["full_name"]
            print("Security baseline:", repo["full_name"])
            if not apply:
                continue
            if config["security"]["dependabot_alerts_for_active_repositories"]:
                api(path + "/vulnerability-alerts", "PUT")
                api(path + "/vulnerability-alerts")
            if repo["private"]:
                continue
            security = {}
            if config["security"]["public_secret_scanning"]:
                security["secret_scanning"] = {"status": "enabled"}
            if config["security"]["public_push_protection"]:
                security["secret_scanning_push_protection"] = {"status": "enabled"}
            if security:
                updated = api(path, "PATCH", {"security_and_analysis": security})
                assert all(updated["security_and_analysis"][key]["status"] == "enabled" for key in security)
            if config["security"]["public_private_vulnerability_reporting"]:
                api(path + "/private-vulnerability-reporting", "PUT")
                assert api(path + "/private-vulnerability-reporting")["enabled"]
        if len(repos) < 100:
            break
        page += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preview or apply the studio's free GitHub security and profile settings.")
    parser.add_argument("--apply", action="store_true")
    reconcile(parser.parse_args().apply)
