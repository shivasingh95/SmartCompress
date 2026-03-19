# Deploy SmartCompress AI

This app is ready for deployment on Streamlit Community Cloud.

## Before you deploy

1. Put this project in a GitHub repository.
2. Make sure these files are in the repo root:
   - `app.py`
   - `requirements.txt`
   - `utils/`
3. Do not upload `venv/` or `temp/`. The `.gitignore` already excludes them.

## Recommended target

Use Streamlit Community Cloud because this project is already a Streamlit app and does not require a custom backend service.

## Deploy steps

1. Push the project to GitHub.
2. Sign in to Streamlit Community Cloud.
3. Create a new app.
4. Select your GitHub repository.
5. Set the main file path to `app.py`.
6. In advanced settings, choose Python 3.10 to match the environment verified locally.
7. Deploy the app.

## Notes

- The app uses `imageio-ffmpeg`, so you do not need to install FFmpeg manually.
- Dependency versions are pinned in `requirements.txt` to match a working local build.
- Uploaded files are stored temporarily during processing and then cleaned up automatically.

## If deployment fails

Check these first:

1. The repository contains `app.py` in the root.
2. `requirements.txt` is present in the root.
3. The repository does not include the local virtual environment.
4. The app is deployed with Python 3.10.
