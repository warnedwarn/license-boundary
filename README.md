# License Boundary

## Distribution manifest

A bundle can contain perfectly ordinary components whose obligations do not fit the way the bundle will be shipped. License Boundary makes that mismatch visible before distribution.

The owner registers two to eight public license texts and a closed set of distribution commitments. GenLayer validators independently read every source and return one bounded status plus a canonical obligation set. The contract, not the model, unions those obligations and compares them with the frozen commitments.

The terminal state is:

- `COMPATIBLE` when every source permits redistribution and every extracted obligation is covered;
- `CONFLICT` when redistribution is forbidden or at least one obligation is missing;
- `INCONCLUSIVE` when a source is ambiguous.

Each component keeps its exact URL, source index, SHA-256 digest, status, and obligation list. Duplicate review IDs and duplicate source slots are rejected. An open review can be cancelled only by its owner, and a terminal review cannot be evaluated again.

## Obligation vocabulary

`ATTRIBUTION`, `PRESERVE_NOTICE`, `PUBLISH_SOURCE`, `SHARE_ALIKE`, `NONCOMMERCIAL_ONLY`, and `PATENT_NOTICE`.

The vocabulary is intentionally closed. The model cannot invent requirements, decide compatibility, or alter the promised distribution profile.

## Local verification

```text
python -m pytest -q
set PYTHONUTF8=1
genvm-lint contracts/contract.py
```

The direct suite covers compatible and conflicting bundles, ambiguous and non-redistributable sources, duplicate IDs and slots, unknown obligations, cancellation authorization, replay, and forged validator output.
