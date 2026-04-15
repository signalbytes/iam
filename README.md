# SignalBytes

> Technology, decoded in small bites.

**Live site:** [signalbytes.in](https://signalbytes.in)

---

## Repository Structure

```
signalbytes.in/
├── index.html        ← Homepage (Everyday Tech section)
├── 404.html          ← Custom 404 page
├── _config.yml       ← GitHub Pages config
├── .nojekyll         ← Prevents Jekyll processing
└── README.md
```

## Deploying to GitHub Pages

1. Push all files to the `main` branch (root of repo)
2. Go to **Settings → Pages**
3. Source: **Deploy from a branch**
4. Branch: `main` / `/ (root)`
5. Save — site will be live at `signalbytes.in` within ~2 minutes

## Custom Domain Setup

In your repo root, create a file called `CNAME` containing:
```
signalbytes.in
```

Then in your domain registrar (e.g. Namecheap, GoDaddy), add these DNS records:

| Type  | Host | Value                |
|-------|------|----------------------|
| A     | @    | 185.199.108.153      |
| A     | @    | 185.199.109.153      |
| A     | @    | 185.199.110.153      |
| A     | @    | 185.199.111.153      |
| CNAME | www  | signalbytes.github.io |

DNS propagation can take up to 24 hours.

---

Built with plain HTML/CSS/JS — no build tools, no dependencies, no framework.
