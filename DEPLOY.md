# Deploy heheDownloader (standalone) so you can use it anytime

This is a **single app**: one Flask server that downloads videos with yt-dlp and sends the file to your browser. Deploy it once and use it from anywhere.

---

## Where to deploy

These platforms work well and have a free tier:

| Platform   | Free tier        | Best for              |
|-----------|------------------|------------------------|
| **Render**| Yes (spins down) | Easiest, good docs     |
| **Railway** | Yes (usage-based) | Very quick deploy   |
| **Fly.io** | Yes (limits)     | Global regions         |

**Not suitable:** Vercel, Netlify (serverless only; this app needs a long-running process and ffmpeg).

---

## Option 1: Deploy on Render (recommended)

1. **Push your code to GitHub**  
   Create a repo and push this project (at least `app.py`, `requirements.txt`, `Dockerfile`).

2. **Sign up / log in**  
   Go to [render.com](https://render.com) and connect your GitHub account.

3. **New Web Service**  
   - Dashboard → **New +** → **Web Service**
   - Connect the repo that contains this project
   - Use these settings:

   | Field | Value |
   |-------|--------|
   | **Name** | `hehedownloader` (or any name) |
   | **Region** | Choose nearest to you |
   | **Root Directory** | Leave empty |
   | **Environment** | **Docker** |
   | **Plan** | Free |

4. **Deploy**  
   Click **Create Web Service**. Render will build the Docker image (installs Python, ffmpeg, yt-dlp, Flask) and start the app.

5. **Use it**  
   When the build finishes, you’ll get a URL like `https://hehedownloader.onrender.com`. Open it, paste a video URL, and download. The file is sent to your browser.

**Note (free tier):** The service may spin down after ~15 min of no use. The first request after that can take 30–60 seconds to wake up.

---

## Option 2: Deploy on Railway

1. **Push your code to GitHub** (same as above).

2. **Sign up** at [railway.app](https://railway.app) and connect GitHub.

3. **New project**  
   - **New Project** → **Deploy from GitHub repo**  
   - Select this project’s repo.

4. **Use Docker**  
   Railway will detect the `Dockerfile` and build it. If it picks “Python” instead, in **Settings** set **Build** to use the Dockerfile.

5. **Generate domain**  
   In the service → **Settings** → **Networking** → **Generate Domain**. You’ll get a URL like `https://your-app.up.railway.app`.

6. **Use it**  
   Open that URL and use the app as usual.

---

## What’s in this repo for deploy

- **`app.py`** – Flask app: web UI and `/download` that runs yt-dlp and streams the file back.
- **`requirements.txt`** – Python deps (Flask, yt-dlp, gunicorn).
- **`Dockerfile`** – Installs ffmpeg and runs the app with gunicorn so it works on Render/Railway.

The app uses the **PORT** environment variable (set by Render/Railway), so you don’t need to change any code for deploy.

---

## Run it locally

```bash
pip install -r requirements.txt
# Install ffmpeg: https://ffmpeg.org/download.html (or e.g. winget install ffmpeg on Windows)
python app.py
```

Then open **http://localhost:10000**.

---

## Troubleshooting

- **“Merge failed” or “ffmpeg not found”**  
  Deploy must use the **Dockerfile** so ffmpeg is installed. On Render, set Environment to **Docker**. On Railway, ensure the service builds from the Dockerfile.

- **Request timeout**  
  Long or large videos can hit the host’s request timeout (e.g. 5 min on Render). For very long videos, consider a VPS (e.g. DigitalOcean) where you control the timeout.

- **Out of memory**  
  Big 4K/long videos can use a lot of RAM. Free tiers have limits; upgrading or using a VPS gives more headroom.
