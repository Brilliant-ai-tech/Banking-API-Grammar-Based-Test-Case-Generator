# Grammar-Based Test Case Generation for a Banking API Gateway
### Group 5 — Question 11

## 1. Industry Problem Analysis

A Kenyan bank's API gateway sits between mobile apps, USSD/*234# menus, agency
banking terminals, and core banking systems (e.g. Finacle, T24, or an
in-house core). Every request that reaches this gateway must be parsed,
validated, authorised and logged before it touches a ledger. Manually
writing test cases for every request shape does not scale: QA teams have a
combinatorial number of request classes (transfer, balance, statement,
freeze, withdrawal, and more that will be added over time), each with
several fields, each field with its own valid/invalid ranges. A **grammar**
gives QA a single, precise, machine-readable specification of "what a
request is allowed to look like," from which both correct and incorrect
examples can be generated automatically and repeatably. This directly
supports regression testing, CI pipelines, and onboarding of new testers who
can read the grammar instead of tribal knowledge.

## 2. Formal CFG Design

The five request classes chosen — **TRANSFER, BALANCE, STATEMENT, FREEZE,
WITHDRAW** — cover the core categories a retail/agency banking API exposes:
moving money, reading a balance, reading history, a compliance/security
action, and a cash-out action. The full grammar in BNF is given at the top
of `banking_grammar_test_generator.py`; the key design decisions are:

- **One top-level rule per request class**, so the grammar is easy to
  extend (adding `DEPOSIT` or `LOAN_APPLY` later is a one-line change).
- **Digits are abstracted at parse time** into `NUM` and `ACCOUNT` lexical
  categories. A pure CFG that spells out every digit string is
  representationally correct but impossible to chart-parse efficiently
  (unbounded terminal vocabulary); using a small lexer + finite CFG is
  standard practice (comparable to how real parsers separate lexing from
  parsing) and keeps the grammar decidable and fast with NLTK's
  `ChartParser`.
- **Enumerated fields** (Month, Reason, Branch) are closed terminal sets,
  which lets us generate *and* mutate them cheaply and lets the parser
  reject unknown values it hasn't been told about (e.g. `Blursday`).
- The grammar is **unambiguous** by construction: each request class has a
  unique leading keyword, so the parser is deterministic in practice
  (verified — every valid case produced exactly one parse tree).

## 3. Implementation

`banking_grammar_test_generator.py` implements:

1. An `nltk.CFG` definition (`NLTK_GRAMMAR`) used for parsing/verification.
2. Per-class **surface generators** (`build_transfer`, `build_balance`, …)
   that produce realistic Kenyan-context values — KES amounts in the
   thousands, `ACCxxx` account numbers, real bank branch names
   (Nairobi CBD, Mombasa Road, Kisumu, Eldoret, Nakuru), and compliance
   reasons (`fraud_alert`, `court_order`, `kyc_pending`, `aml_flag`).
3. `generate_valid_cases(n=30)` — round-robins the 5 classes so coverage is
   even, then generates exactly 30 (or more) valid requests.
4. **Fifteen distinct mutation functions** (`mutate_drop_keyword` …
   `mutate_wrong_field_type`), each representing one *class* of grammar
   violation rather than 15 arbitrary random strings — this is deliberately
   designed so each invalid case teaches the parser/tester something
   different (missing token, wrong order, wrong lexical category, unknown
   enum value, injection payload, overflow, etc.).
5. A `lex()` tokenizer + `try_parse()` helper that runs every generated
   string through the real `ChartParser`, so acceptance/rejection is
   evidence-based, not just asserted.

Running the script (see `run_output.txt` for a captured run) prints:

- 30 valid cases, one per generated request (6 per class).
- Two full parse trees (a `TRANSFER` and a `FREEZE` example), shown both as
  bracketed trees and as ASCII-art trees via `pretty_print()`.
- Confirmation that **30/30 valid cases parse successfully**.
- 15 invalid cases, each labelled with its mutation type.
- A parser sweep over the invalid cases showing **13/15 rejected by the
  grammar alone**, and 2 that a pure syntax parser cannot catch
  (`missing_semicolon`, `overflow_amount`) — discussed under Limitations.

### Sample parse tree (TRANSFER)
```
Input: TRANSFER amount 2015 from ACC397 to ACC036;
(S (TRANSFER_REQ TRANSFER amount NUM from ACCOUNT to ACCOUNT))
                         S
                         |
                    TRANSFER_REQ
    _____________________|______________________
TRANSFER amount NUM     from     ACCOUNT  to ACCOUNT
```

### Sample parse tree (FREEZE)
```
Input: FREEZE account ACC970 reason kyc_pending;
(S (FREEZE_REQ FREEZE account ACCOUNT reason (REASON kyc_pending)))
                   S
                   |
               FREEZE_REQ
   ________________|__________________
  |       |        |        |       REASON
  |       |        |        |         |
FREEZE account  ACCOUNT   reason kyc_pending
```

## 4. How the Test Cases Support Three Kinds of Testing

**Parser testing.** The valid set exercises every production rule at least
once (all 5 classes, all enum branches over enough runs); the invalid set
exercises the parser's *rejection* path — the thing manual test suites
usually under-test. A parser that silently accepts `TRANSFER ACC123 amount
to 5000` (fields swapped) has a defect that would otherwise only surface in
production.

**API/functional testing.** Each generated string is a ready-made HTTP/USSD
payload. Feeding the 30 valid cases at the API layer checks that the
gateway's business logic (not just its grammar) handles every class
correctly — e.g. that a `WITHDRAW` at a named branch actually debits the
right account. Feeding the 15 invalid cases checks that the gateway returns
a proper 4xx/validation error rather than a 500, a silent no-op, or, worse,
processing a malformed request.

**Security testing.** Several mutators are deliberately security-flavoured:
`mutate_sql_injection` appends `; DROP TABLE transactions;` and `' OR
'1'='1` style payloads; `mutate_oversized_amount` checks for
integer-overflow / buffer handling; `mutate_extra_token` checks that
unexpected fields are not silently trusted. These map directly onto
OWASP API Security Top 10 concerns (injection, improper input validation,
excessive data exposure) and give a security tester a starting corpus
without hand-crafting exploit strings.

## 5. Coverage Evaluation

**Included:** all 5 request classes; both realistic and boundary numeric
values; every enumerated value (month/reason/branch) reachable over
repeated runs; 15 distinct structural failure modes (deletion, reordering,
duplication, wrong lexical category, unknown keyword, case corruption,
truncation, injection, overflow, field-type swap).

**Partially covered / missing:**
- **Concurrency and idempotency** (e.g. replaying the same TRANSFER twice)
  are not representable in a request-shape grammar — they are a *sequence*
  property, not a *sentence* property.
- **Cross-field business rules** (e.g. "amount must not exceed daily
  limit", "cannot freeze an already-frozen account") are semantic, not
  syntactic, and by design fall outside a CFG — the run output shows this
  explicitly (`overflow_amount`, and any true business-rule violation would
  also parse fine).
- **Encoding/protocol-level issues** (missing terminator, wrong character
  encoding, malformed JSON/XML wrapper if the real API isn't plain text)
  are only partially captured; `missing_semicolon` is included specifically
  to demonstrate that a pure CFG cannot enforce lexical/protocol
  well-formedness on its own.
- **Authentication/authorisation** (who is allowed to FREEZE an account,
  token validity) is entirely out of scope for a request-grammar and needs
  separate test design.

## 6. Critical Discussion — Grammar-Based Testing in Kenya's Banking Sector

Kenya's banking and mobile-money ecosystem (M-Pesa, agency banking, bank
APIs feeding into the Central Bank's Kenya Credit Reference Bureau checks,
and CBK-mandated fraud-monitoring obligations) processes an extremely high
volume of small, structurally simple transactions. Grammar-based testing is
well suited here because:

- It gives **repeatable, auditable evidence** of parser correctness — useful
  for CBK/PCI-DSS style audits, where a bank must show it systematically
  tests input validation, not just "we tried a few examples."
- It scales test-case volume cheaply, which matters for institutions with
  small QA teams relative to transaction volume — a common constraint at
  Kenyan tier-2/tier-3 banks and fintech partners integrating with banks'
  APIs.
- It documents the *specification* of the API as a living artifact (the
  grammar itself), reducing ambiguity between the bank's API team and
  third-party integrators (a frequent pain point in Kenya's open banking
  and fintech-partnership environment).

**However, a CFG alone is not sufficient**, and should be combined with:

1. **Fuzzing** — for cases a grammar cannot anticipate: malformed encodings,
   extremely long strings, non-UTF8 bytes, timing attacks, and anything
   an attacker might try that isn't a "near-miss" of a valid sentence.
   Grammar-based generation finds *known* failure classes; fuzzing finds
   *unknown* ones.
2. **Domain/business-rule engines** — daily transaction limits, KYC tier
   restrictions, anti-money-laundering thresholds (CBK requires reporting
   for transactions above certain amounts), and account-state machines
   (a frozen account cannot transfer) must be tested with a rules-based or
   model-based approach layered on top of grammar-valid inputs, since these
   are semantic, not syntactic, properties.
3. **Property-based / stateful testing** — for idempotency, concurrency,
   and multi-step flows (e.g. reversing a transfer), which a single-sentence
   grammar cannot express.

**In short:** grammar-based testing is an excellent, cheap, high-coverage
first line of defence for *input validation and parser correctness* — it
should be the QA team's baseline — but it must be paired with fuzzing for
unanticipated malformed input, and with domain-rule/business-logic testing
for anything that depends on account state, limits, or sequences of
requests, before the gateway can be considered production-ready for a
regulated Kenyan banking environment.

## 7. Deliverables Summary

| Deliverable | Location |
|---|---|
| Formal CFG (BNF) | Docstring at top of `banking_grammar_test_generator.py`, and NLTK `CFG.fromstring` grammar in the same file |
| Python/NLTK source | `banking_grammar_test_generator.py` |
| Evidence of generation & parsing | `run_output.txt` (captured run: 30 valid, 15 invalid, parser results) |
| Parse trees | Sections "Sample parse tree (TRANSFER)" and "(FREEZE)" above, and reproduced live by running the script |
| Critical report | This document |
