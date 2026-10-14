# CampusFlow Historical Baseline Check

This report preserves observations from an earlier baseline review. The candidate SHA was recorded, but the exact checked-out SHA for every observation was not captured. These findings are historical and do not describe the current feature-complete `main` branch.

## 1. Audited commit

- Candidate commit: `f96b7d9677613f98f004d3ba3fdb571914b1ae73`
- Commit message: `Update Engineer B's name in README.md`
- Commit date: `2026-10-11 20:08:56 +0100`
- Mentor designation: **Not recorded in the materials available for this report.** Do not treat the candidate SHA as mentor-designated unless the mentor confirms it.
- Branch used for this documentation work: `docs/20-baseline-check`

The candidate SHA below was proposed for audit, but the report does not establish that the observed test run and source inspection were performed at that exact SHA. The mentor-designated audited SHA was not recorded.

## 2. Automated test baseline

- Command: `python3 -m unittest discover -s tests -v`
- Observed result during the baseline review: **PASS**
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
| Work queue statuses | The source inspected during the baseline review included tickets with status `open` and `in_progress`. | Historical observation; later integration changes set the Open Work Queue to include only `open` tickets. |
| `notes` field | The `create_ticket` implementation inspected during the baseline review did not construct a `notes` field. | Historical observation; the merged notes feature adds `notes` to new tickets and supports legacy files without the field. |
| Loader strictness | `load_tickets` rejects malformed JSON and rejects data unless it is a list of dictionaries. | These checks are present; full ticket-field validation has not been established by this inspection alone. |

## 5. Audit feedback and reproduction status

No original audit feedback was provided for this baseline check. Therefore, there are no audit claims to classify at this stage. This does not mean that no issues exist. If feedback is supplied later, add each claim verbatim and assess it against observed evidence:

- **Reproduced** — include the exact steps and observed result.
- **Could not reproduce** — include the exact checks performed and observed result.
- **Not yet tested** — use when there is insufficient evidence to classify the claim.

Do not classify a peer-reported issue as confirmed without reproducing it.

## 6. Scope and limits

- The mentor-designated baseline SHA was not included in the materials available when this report was written. The candidate SHA above is retained for traceability, not represented as confirmed.
- The 59-test result and manual observations are historical and must not be used as evidence for the later merged feature set. The current integration run is recorded in [`integration-checklist.md`](integration-checklist.md) and [`test-output.txt`](test-output.txt).
- No original audit feedback was supplied with this report, so it contains no claim-by-claim reproduction assessment.
