# Analytics and Billing v1.0.5

## Dashboards

- chat sessions/messages,
- feedback distribution,
- canonical works/passages,
- quarantine snapshots,
- model input/output tokens,
- estimated model cost,
- publishing volume,
- acquisition jobs.

## Endpoints

```text
GET /analytics/overview
GET /analytics/readiness
GET /models/remote/usage
GET /models/remote/usage/summary
```

## Billing Boundary

v1.0.5 records estimated model usage cost. It does not yet integrate Razorpay/Stripe/subscription billing.
