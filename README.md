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

## StudioNet record

- Contract: [`0xdA51b0D5a423CF227237E7756796da74Af9B8275`](https://explorer-studio.genlayer.com/address/0xdA51b0D5a423CF227237E7756796da74Af9B8275)
- Reviewed source: [`ad672f7`](https://github.com/warnedwarn/license-boundary/tree/ad672f7f2a98cfcd5bc812da5d7fd382f9c61c3d)
- Deployment: [`0x105e...f2b5`](https://explorer-studio.genlayer.com/transactions/0x105ebe985813f75b0b21ececc3d5d98027e032233574b2d8cfa6553817abf2b5)
- Open review: [`0x9368...eab8`](https://explorer-studio.genlayer.com/transactions/0x9368d1869a076d32bd6e3f43d3dd04ce1f53fbae3c39aa40e1fb4188b9dceab8)
- Evaluate: [`0x4401...6d7e`](https://explorer-studio.genlayer.com/transactions/0x44014bb6d6a45c651f9e68c574730e934cb362ad3f75b631d959b8edb51e6d7e)
- Live record: `LICENSE-1792287461`, terminal state `COMPATIBLE`

The deployment and both workflow transactions reached `FINALIZED / MAJORITY_AGREE / SUCCESS`. The deployed contract bytes match the reviewed source SHA-256. The three public license pages are operator-authored fixtures and are not legal advice or independent authorities.
