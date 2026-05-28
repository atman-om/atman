# Public App Route Map

| Route | Purpose | API dependency |
|---|---|---|
| `/` | public landing + runtime status | `/runtime/status` |
| `/ask` | Hindi-first question answering | `/public/ask` |
| `/sources` | public source explorer | `/public/sources` |
| `/shloka` | shloka explainer placeholder | future `/public/shloka/{locator}` |

## UX invariant

The public app must always show citations when available and must not hide safety flags in scholar/admin contexts.
