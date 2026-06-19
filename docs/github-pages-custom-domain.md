# Migrating a domain (Cloudflare DNS) to a GitHub Pages site

A repeatable runbook for moving a custom domain from old hosting (e.g. Namecheap)
to a GitHub Pages site, while keeping DNS managed in Cloudflare.

**Starting state this assumes:**

- Domain registered / DNS managed in **Cloudflare**, currently pointing at old
  hosting (Namecheap).
- A working GitHub Pages site serving at `https://<USER>.github.io/<REPO>/`.
- You want it to serve at the apex domain `https://<DOMAIN>` instead.

**Fill in these placeholders as you go:**

| Placeholder | Meaning | Example |
|---|---|---|
| `<DOMAIN>` | apex domain | `cryb.org` |
| `<USER>` | GitHub username | `crybx` |
| `<REPO>` | repo name | `cryborg` |

---

## 1. Set the custom domain in the repo

GitHub repo → **Settings → Pages → Custom domain** → enter `<DOMAIN>` → **Save**.

This tells GitHub to route the domain to this repo's content. It does **not**, by
itself, change DNS — that's Step 3.

## 2. Make sure a `CNAME` file lands in the published site

GitHub needs a file named `CNAME` (containing just `<DOMAIN>`) at the **root of
the published site**. How you do this depends on the deploy method:

- **Deploy from a branch** (plain HTML in the repo): Step 1 commits the `CNAME`
  file for you. Nothing more to do — just confirm it exists in the branch.

- **Deploy via GitHub Actions / a static-site generator** (Pelican, Jekyll
  custom builds, Hugo, etc.): the build output is regenerated each deploy, so a
  committed `CNAME` gets wiped. You must make the **build** emit it. For
  **Pelican**, add a `CNAME` file under `content/` and map it to the output root
  in `pelicanconf.py`:

  ```python
  STATIC_PATHS = ['images', 'robots.txt', 'favicon.ico', 'CNAME']
  EXTRA_PATH_METADATA = {
      'robots.txt': {'path': 'robots.txt'},
      'favicon.ico': {'path': 'favicon.ico'},
      'CNAME': {'path': 'CNAME'},
  }
  ```

  The `CNAME` file just contains one line:

  ```
  <DOMAIN>
  ```

  (Generic alternative for any Actions workflow: add a step before the
  pages-artifact upload — `- run: echo '<DOMAIN>' > output/CNAME`.)

## 3. Point the static-site generator at the new URL

If your site uses **absolute URLs** (Pelican with `RELATIVE_URLS = False`, which
is the default for production), every internal link is built from `SITEURL`. If
it still says `<USER>.github.io/<REPO>`, the live site's navigation will link
back to the old path. Update the production config (`publishconf.py` for
Pelican):

```python
SITEURL = 'https://<DOMAIN>'
```

Commit Steps 2–3 and let the deploy run.

## 4. Repoint DNS in Cloudflare

Cloudflare dashboard for `<DOMAIN>` → **DNS → Records**.

1. **Delete** the existing A / CNAME records pointing at the old host (Namecheap).
2. **Add four A records** for the apex, each name `@`, all **DNS only (grey
   cloud)**:

   ```
   185.199.108.153
   185.199.109.153
   185.199.110.153
   185.199.111.153
   ```

3. *(Optional)* add the four AAAA (IPv6) records, also grey cloud:

   ```
   2606:50c0:8000::153
   2606:50c0:8001::153
   2606:50c0:8002::153
   2606:50c0:8003::153
   ```

4. **Add a CNAME** for `www` → `<USER>.github.io` (the bare user domain, **no**
   `/<REPO>` path — CNAMEs can't contain paths; GitHub resolves the repo
   internally). Grey cloud.

> **Grey cloud (DNS only) is the single most important setting.** It lets GitHub
> provision and renew its TLS certificate. Orange cloud at this stage causes
> cert-provisioning failures and redirect loops. You can switch to orange later
> (Step 8).

## 5. Set Cloudflare SSL/TLS mode

**SSL/TLS → Overview → Full** (or **Full (strict)**). Never "Flexible" — it
causes infinite redirect loops with Pages.

## 6. Wait for DNS propagation + cert provisioning

Anywhere from a few minutes to ~24h. During this window the browser may show
`ERR_CERT_COMMON_NAME_INVALID` because GitHub temporarily serves its
`*.github.io` fallback cert — this is normal and clears once GitHub issues the
cert for `<DOMAIN>`.

## 7. Verify

Check DNS resolves to GitHub (not the old host, not Cloudflare proxy IPs):

```bash
getent ahostsv4 <DOMAIN>          # expect 185.199.108-111.153
```

Check which TLS cert is being served:

```bash
echo | openssl s_client -connect <DOMAIN>:443 -servername <DOMAIN> 2>/dev/null \
  | openssl x509 -noout -subject
```

- `subject=CN = *.github.io` → still provisioning, keep waiting.
- `subject=CN = <DOMAIN>` → done.

In **Settings → Pages**, GitHub shows "DNS check successful" once records are
correct.

## 8. Enable HTTPS enforcement

Once the cert shows `CN = <DOMAIN>` and the site loads over `https://<DOMAIN>`,
tick **Settings → Pages → Enforce HTTPS**. This 301-redirects all `http://`
traffic to `https://`.

## 9. (Optional) Turn on the Cloudflare proxy for analytics

Leaving everything **grey cloud is a valid permanent state** and the site is
fully done at this point. Only enable the orange cloud if you want Cloudflare's
proxy features.

For **basic, tracker-free traffic analytics** (requests, visitors, top paths,
countries, bandwidth — server-side at the edge, no JS/cookies):

1. Confirm Enforce HTTPS (Step 8) is on and the site works.
2. Confirm **SSL/TLS → Full (strict)** (Step 5).
3. Flip the apex A records (and `www`) to **orange cloud (Proxied)**.
4. View under Cloudflare **Analytics → Traffic**. (This is *not* "Web
   Analytics", which injects a JS beacon — you don't need that.)

**Caveat — cert renewal:** GitHub auto-renews its cert ~every 90 days via an
HTTP challenge to the origin. Proxying can rarely interfere. If a cert warning
appears months later, set the records back to grey cloud for ~1 hour to let
renewal complete, then re-proxy.

**Caveat — stale content:** the proxy caches. After a deploy, purge via
Cloudflare **Caching → Configuration → Purge Everything** if you see old content.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ERR_CERT_COMMON_NAME_INVALID`, cert is `*.github.io` | GitHub cert not issued yet | Wait (up to 24h); ensure DNS is grey cloud |
| Redirect loop (`ERR_TOO_MANY_REDIRECTS`) | Cloudflare SSL set to "Flexible" | Set SSL/TLS to Full (strict) |
| Custom domain setting keeps resetting | `CNAME` file missing from published output | Step 2 — make the build emit it |
| Site loads but internal links point to `*.github.io/<REPO>` | `SITEURL` not updated | Step 3 |
| Settings → Pages "DNS check unsuccessful" | A records wrong / proxied | Use the four GitHub IPs, grey cloud |
| `dig`/`getent` shows `104.x` or `172.67.x` | Cloudflare proxy (orange) is on | Grey-cloud it until cert provisions |
| Cert warning months after setup | Renewal blocked by proxy | Grey cloud ~1h, then re-proxy |
