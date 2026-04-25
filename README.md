# 📸 InstaFlow — Free Instagram Scheduler

> Post and schedule Instagram photos & Reels for free using GitHub Pages + GitHub Actions + Instagram Graph API.

**Total cost: ₹0 / $0**

---

## 📁 Repository Structure

```
your-repo/
├── index.html              ← The web app (open in browser)
├── post_scheduler.py       ← GitHub Actions scheduler script
├── queue.json              ← Your scheduled posts (auto-updated)
└── .github/
    └── workflows/
        └── auto-post.yml   ← GitHub Actions workflow
```

---

## 🚀 Quick Setup (15 minutes)

### Step 1 — Fork or Create Repo

1. Go to [github.com/new](https://github.com/new)
2. Create a **public** repository (e.g., `instaflow`)
3. Upload all files from this folder to the root

### Step 2 — Enable GitHub Pages

1. Go to your repo → **Settings → Pages**
2. Source: **Deploy from a branch**
3. Branch: **main**, Folder: **/ (root)**
4. Click **Save**
5. Your site: `https://yourusername.github.io/instaflow`

### Step 3 — Get Instagram API Credentials (Free)

**A. Convert Instagram to Business/Creator:**
- Instagram App → Settings → Account → Switch to Professional Account

**B. Create Facebook Developer App:**
- Go to [developers.facebook.com/apps/create](https://developers.facebook.com/apps/create/)
- Select "Business" → Fill details → Create App
- Add Product: **Instagram Graph API**

**C. Get Access Token:**
- Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
- Select your App
- Add permissions: `instagram_basic`, `instagram_content_publish`
- Generate Token → Copy it

**D. Convert to Long-Lived Token (valid 60 days):**
```
https://graph.facebook.com/oauth/access_token
  ?grant_type=fb_exchange_token
  &client_id={app-id}
  &client_secret={app-secret}
  &fb_exchange_token={short-lived-token}
```

**E. Get Instagram Business Account ID:**
- In Graph API Explorer: query `me/accounts`
- Get the Page ID, then query: `{page-id}?fields=instagram_business_account`
- Copy the `id` from `instagram_business_account`

### Step 4 — Add GitHub Secrets

1. Go to your repo → **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Add:
   - `INSTAGRAM_ACCESS_TOKEN` → your long-lived token
   - `INSTAGRAM_ACCOUNT_ID` → your Instagram business account ID

### Step 5 — Use the App!

1. Visit your GitHub Pages URL
2. Go to **Setup tab** → enter credentials → click **Test Connection**
3. Go to **Create Post** → add media URL + caption → Post Now or Schedule
4. GitHub Actions runs every 15 minutes and auto-posts anything due!

---

## 🖼️ Free Media Hosting

Instagram needs publicly accessible URLs for media.

| Type | Service | How |
|------|---------|-----|
| Images | [ImgBB](https://imgbb.com) | Upload → copy "Direct link" |
| Images | [Cloudinary](https://cloudinary.com) | Free 10GB |
| Videos | Cloudinary free tier | Upload → copy URL |
| Videos | GitHub itself | Commit to repo → use raw URL |

---

## ⚠️ Limitations

- **Token expires every 60 days** — refresh it in the Setup tab or manually
- **Reels** must be MP4, H.264, max 15 minutes, min 3 seconds
- **Images** must be JPEG, min 320px, max 1440px
- Instagram API limits: 50 posts per 24 hours per account
- GitHub Actions free: 2000 minutes/month (15-min checks ≈ ~96 checks/day ≈ ~1440 min/month — fits!)

---

## 📄 License

MIT — free to use, modify, and share.
