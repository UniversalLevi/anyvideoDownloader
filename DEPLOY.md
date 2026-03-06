# Deploy anyvideoDownloader so you can use it anytime

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
   | **Name** | `anyvideoDownloader` (or any name) |
   | **Region** | Choose nearest to you |
   | **Root Directory** | Leave empty |
   | **Environment** | **Docker** |
   | **Plan** | Free |

4. **Deploy**  
   Click **Create Web Service**. Render will build the Docker image (installs Python, ffmpeg, yt-dlp, Flask) and start the app.

5. **Use it**  
   When the build finishes, you’ll get a URL like `https://anyvideodownloader.onrender.com`. Open it, paste a video URL, and download. The file is sent to your browser.

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

## Instagram / private content (cookies)

Instagram (and some other sites) often require login cookies when the request comes from a server (e.g. Render). You have two options:

### Option A: Paste cookies each time
Use the **Cookies** textarea on the page. Paste your cookies in **Netscape format** (a `cookies.txt` file). To get it:
- Install a browser extension like [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) (Chrome) or [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/) (Firefox).
- Log in to Instagram in that browser, go to instagram.com, then use the extension to export “Netscape” or “cookies.txt” and paste the content into the app.

### Option B: Set cookies once on the server (recommended for Instagram)
So the app always uses your Instagram session without pasting every time:

1. Export your Instagram cookies in Netscape format (same as above).
2. On **Render**: your service → **Environment** → **Add Environment Variable**.
   - **Key:** `COOKIES_TXT`
   - **Value:** paste the **entire** contents of your cookies.txt (multiple lines). Render allows multiline values.
3. Save. Render will redeploy. After that, Instagram (and other sites that need cookies) will use this cookie for every request.

**Security:** Treat `COOKIES_TXT` like a password. Anyone with access to your Render env can use the session. Don’t share the repo or env; use a dedicated Instagram account if you prefer.

---

## Troubleshooting

- **Instagram: “login required” or “rate-limit reached”**  
  Add cookies: either paste them in the **Cookies** field on the page, or set the **COOKIES_TXT** env var on Render with your cookies.txt content (see “Instagram / private content” above).

- **“Merge failed” or “ffmpeg not found”**  
  Deploy must use the **Dockerfile** so ffmpeg is installed. On Render, set Environment to **Docker**. On Railway, ensure the service builds from the Dockerfile.

- **Request timeout**  
  Long or large videos can hit the host’s request timeout (e.g. 5 min on Render). For very long videos, consider a VPS (e.g. DigitalOcean) where you control the timeout.

- **Out of memory**  
  Big 4K/long videos can use a lot of RAM. Free tiers have limits; upgrading or using a VPS gives more headroom.
