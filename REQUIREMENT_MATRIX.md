# Requirement matrix

| Requirement | Code path | Targeted proof | Status |
|---|---|---|---|
| Unique normalized review IDs | `ident`, `open_review` | duplicate-ID test | PASS |
| Bounded distinct HTTPS slots | `https_url`, `open_review` | duplicate-slot test | PASS |
| Every license independently fetched | `_inspect` | strict web mocks and digest assertions | PASS |
| Complete bounded extraction | `_inspect` | malformed and forged row coverage | PASS |
| Compatibility derived outside the model | `evaluate` | compatible and missing-commitment tests | PASS |
| Every decision field validator-bound | strict equality over rows and digests | forged obligation and digest test | PASS |
| Replay and unauthorized cancellation rejected | `evaluate`, `cancel_open` | authorization and replay test | PASS |
| Live deployment and transaction | `deployment.json`, `evidence/deployment-verification.json` | finalized deployment plus open and evaluate receipts | PASS |
