# Cloudflare Frontend Deploy

Atman's unified frontend is a dynamic Next.js app. Deploy it to Cloudflare Workers with OpenNext, not static Pages export, because dashboard and Qwen pages fetch backend data at request time.

## App

- Worker name: `swabodh-atman`
- Domain: `atman.swabodh.in`
- App directory: `apps/atman`
- Config: `apps/atman/wrangler.toml`

## Required production variables

Set these in Cloudflare Workers before deploy/build:

```text
NEXT_PUBLIC_API_BASE_URL=https://api.swabodh.in
```

Use the real public API origin if it is different. Do not leave this as `127.0.0.1` or `localhost` in production.

## Commands

```powershell
cd apps\atman
$env:NODE_OPTIONS="--use-system-ca"
npm.cmd run build
npm.cmd run preview:cloudflare
npm.cmd run deploy:cloudflare
```

`preview:cloudflare` runs the app in the Cloudflare Worker runtime locally. `deploy:cloudflare` builds and deploys the Worker, then attaches the `atman.swabodh.in` custom domain if the Cloudflare zone is available on the logged-in account.

## Cloudflare notes

- `swabodh.in` must be an active Cloudflare zone.
- Keep root `swabodh.in` free for the public website.
- The public website's Atman tab should link to `https://atman.swabodh.in`.
- The custom domain cannot already have a conflicting CNAME record.
- `www.swabodh.in` is not covered by this Atman console config. Use it for the public website or a website redirect.
