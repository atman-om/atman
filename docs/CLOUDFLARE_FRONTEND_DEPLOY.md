# Cloudflare Frontend Deploy

Atman's unified frontend is a dynamic Next.js app. Deploy it to Cloudflare Workers with OpenNext, not static Pages export, because dashboard and Qwen pages fetch backend data at request time.

## App

- Worker name: `swabodh`
- Domain: `swabodh.in`
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

`preview:cloudflare` runs the app in the Cloudflare Worker runtime locally. `deploy:cloudflare` builds and deploys the Worker, then attaches the `swabodh.in` custom domain if the Cloudflare zone is available on the logged-in account.

## Cloudflare notes

- `swabodh.in` must be an active Cloudflare zone.
- The custom domain cannot already have a conflicting CNAME record.
- `www.swabodh.in` is not covered by the root-domain custom domain. Add a second custom domain or a Cloudflare redirect rule if `www` should work.
