# Maintainer Guide

For the project owner. It explains what to do after you change something, so that everyone else keeps getting a working one-script setup.

## How sharing works

- Friends get the project files from GitHub: `docker-compose.yml`, the data dump in `db-init/`, the model files in `data/generated/`, and the setup script.
- The 3 app images come from Docker Hub: `furquanahmad/graphtriage-ticketing`, `-inference` and `-graph-seed`. `docker-compose.yml` names the exact tag of each image.
- A friend gets your change only when BOTH are true:
  1. the new image tag is on Docker Hub, and
  2. `docker-compose.yml` on GitHub points to that new tag.
- Never overwrite an existing tag. Always use a new one (1.1 -> 1.2). Docker caches tags, so friends would keep the old image.

The script `scripts/release.ps1` does all of this for you.

## Your daily work (unchanged)

Build and run from source:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

Never run `docker compose down -v` in your own project folder. `-v` deletes your data.

## What did you change?

| You changed | What to do |
|---|---|
| Java code or dashboard (`ticketing-service`) | Commit, then release `ticketing` |
| Python code or its requirements (`inference-service`) | Commit, then release `inference` |
| Scripts in `graph-etl` | Commit, then release `graph-seed` |
| Model files (retrained) | Put the 4 runtime files in `data/generated/`, commit and push. No image needed. Friends use `-Update` |
| MySQL data (tickets, bugs, fixes) | Run `scripts/export-db.ps1`, commit and push. Friends use `-Update -Reset` |
| Neo4j graph | It is built from MySQL by `graph-seed` on first start. Change MySQL data as above |
| Only README or docs | Commit and push |
| `docker-compose.yml` itself | Commit, push, and test like a new user |

The 4 runtime model files are `gnn_model.pt`, `graph_dataset.pt`, `feature_explainer.joblib` and `similarity_explainer.joblib`.

## Release a code change, step by step

1. **Test locally** with the dev command above.
2. **Commit your code** (only the files you changed):

```powershell
   git add ticketing-service
   git commit -m "Describe your change"
```

   Do not commit `.env`, backups, `digest.txt` or `structure.txt`.
3. **Log in to Docker Hub once** (skip if you did it before): `docker login`
4. **Preview** (changes nothing):

```powershell
   powershell -ExecutionPolicy Bypass -File .\scripts\release.ps1 -Services ticketing -DryRun
```

5. **Release**:

```powershell
   powershell -ExecutionPolicy Bypass -File .\scripts\release.ps1 -Services ticketing
```

   Several services: `-Services "ticketing,inference"`. Everything: `-Services all`.

   The script picks the next tag, builds, pushes to Docker Hub, checks the tag is listed, updates `docker-compose.yml`, commits and pushes `main`. If the build or push fails, it restores `docker-compose.yml` and commits nothing.
6. **Test like a new user** (recommended, see the next section).
7. **Tell your friends** to update (see "Friend update").

## Change the data

MySQL data:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\export-db.ps1
git diff --stat db-init
git add db-init
git commit -m "Update data"
git push origin main
```

The app_user table is exported without rows. The app creates the demo user when it starts.
Friends then update with `-Update -Reset` (this deletes their local data and loads the new data).

Retrained models: copy the 4 runtime files to `data/generated/`, then `git add data/generated` (only those 4 are tracked), commit and push. Friends update with `-Update`.

## Test like a new user (safe way)

Important: the test folder must NOT be named `graphtriage`. Docker names volumes after the folder name. A folder named `graphtriage` would reuse your real data and passwords.

```powershell
# 1. Stop YOUR stack (never add -v here)
docker compose -f docker-compose.yml -f docker-compose.dev.yml down

# 2. Run the script like a friend would, in a folder with a different name
New-Item -ItemType Directory C:\gt-test | Out-Null
Set-Location C:\gt-test
irm https://raw.githubusercontent.com/Furquan-Shaikh/graphtriage/main/setup-windows.ps1 -OutFile setup-windows.ps1
$env:GT_INSTALL_DIR = "C:\gt-test\gt-friend-sim"
powershell -ExecutionPolicy Bypass -File .\setup-windows.ps1

# 3. Check the app in the browser (login, predict, explain, Neo4j graph)

# 4. Clean up. -p makes sure only the test project is removed
Set-Location C:\gt-test\gt-friend-sim
docker compose -p gt-friend-sim down -v
Set-Location C:\
Remove-Item C:\gt-test -Recurse -Force
Remove-Item Env:GT_INSTALL_DIR

# 5. Start your own stack again
Set-Location <your project folder>
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

## Friend update

Tell your friend to run these two lines in PowerShell:

```powershell
irm https://raw.githubusercontent.com/Furquan-Shaikh/graphtriage/main/setup-windows.ps1 -OutFile setup-windows.ps1
powershell -ExecutionPolicy Bypass -File .\setup-windows.ps1 -Update
```

`-Update` downloads the latest project files from GitHub (the friend's data stays) and recreates the containers, so new images and new model files are used.
If you changed the data too, add `-Reset`: `... -Update -Reset`. This deletes the friend's local data and loads the new data.

## Never do this

- `docker compose down -v` in your own project folder.
- Reuse or overwrite an image tag.
- Commit `.env` or your backup folder.
- Push a `docker-compose.yml` that points to a tag that is not on Docker Hub (the release script prevents this).
- Name a test folder `graphtriage`.

## Troubleshooting

- **push denied**: run `docker login`.
- **Tag already exists**: set a newer tag in `docker-compose.yml` and run the release again.
- **Your branch is behind GitHub**: run `git pull`, then release again.
- **Uncommitted changes**: commit them first. The image must match committed code.
- **Friend still sees the old version**: check that `docker-compose.yml` on GitHub shows the new tag and that the friend ran `-Update`.