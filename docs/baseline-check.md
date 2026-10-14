# CampusFlow Baseline Check

## 1. Audited commit

- Candidate commit: `f96b7d9677613f98f004d3ba3fdb571914b1ae73`
- Commit message: `Update Engineer B's name in README.md`
- Commit date: `2026-10-11 20:08:56 +0100`
- Confirmation that this is the mentor-designated audited commit: **Pending**.
- Branch used for this documentation work: `docs/20-baseline-check`

> The tests below were observed on the currently checked-out code. Confirm that this code is the audited baseline before treating these results as verified results for the audited commit.

## 2. Automated test baseline

- Command: `python3 -m unittest discover -s tests -v`
- Observed result: **PASS**
- Output summary: `Ran 59 tests in 0.017s` and `OK`.

## 3. Manual tests

### Test 1 — Decimal affected_users

- Input: `affected_users = 2.5` when creating a ticket.
- Expected: Reject a non-whole number and do not create a ticket.
- Actual: Rejected with `ValueError: Affected users must be a positive whole number.`
- Additional observation: `Tickets created: 0`.
- Result: **Expected behaviour observed**.

### Test 2 — Unassigned ticket moved to in_progress

- Input: Attempt to move an unassigned ticket from `open` to `in_progress`.
- Expected: Reject the transition and leave the ticket unchanged.
- Actual: Rejected with `ValueError: Cannot start an unassigned ticket. Assign it first.`
- Additional observation: Final status remained `open`.
- Result: **Expected behaviour observed**.

### Test 3 — Corrupted tickets JSON

- Input: A temporary JSON file containing `{invalid json`.
- Expected: Raise `StorageError` and do not silently replace or reset the data.
- Actual: `load_tickets` raised `StorageError`, reported that the file was not valid JSON, and stated that the file had not been changed.
- Safety: Used a temporary file, not the project's real ticket data.
- Result: **Expected error handling observed**.

## 4. Specification checks from source inspection

| Check | Observed behaviour | Assessment |
|---|---|---|
| `affected_users` validation | Accepts digit-only strings after trimming whitespace; rejects decimal values and booleans; requires a positive whole number. | Confirm against the exact specification and audited commit. |
| Work queue statuses | `work_queue` includes tickets with status `open` and `in_progress`. | The claim that the queue only shows `open` was not supported by the inspected current code. |
| `notes` field | `create_ticket` constructs a ticket without a `notes` field. | Absence observed in the ticket-construction code; confirm the specification requires this field. |
| Loader strictness | `load_tickets` rejects malformed JSON and rejects data unless it is a list of dictionaries. | These checks are present; full ticket-field validation has not been established by this inspection alone. |

## 5. Audit feedback and reproduction status

No original audit feedback was provided for this baseline check. Therefore, there are no audit claims to classify at this stage. This does not mean that no issues exist. If feedback is supplied later, add each claim verbatim and assess it against observed evidence:

- **Reproduced** — include the exact steps and observed result.
- **Could not reproduce** — include the exact checks performed and observed result.
- **Not yet tested** — use when there is insufficient evidence to classify the claim.

Do not classify a peer-reported issue as confirmed without reproducing it.

## 6. Outstanding items

- [ ] Confirm the mentor-designated audited commit SHA.
- [ ] Verify the manual and automated results against that exact commit.\n- [x] Rerun the automated test suite on the current branch: 59 tests passed (`OK`).
- [ ] Copy the original audit feedback into this report and classify each claim using observed evidence.
- [ ] Obtain the other engineer's contribution and review before merging through a pull request.
