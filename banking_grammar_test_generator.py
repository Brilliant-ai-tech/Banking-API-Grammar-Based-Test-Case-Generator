"""
=====================================================================
 Banking API Grammar-Based Test Case Generator
 Group 5 — Question 11
=====================================================================

This program:
  1. Defines a Context-Free Grammar (CFG) for 5 classes of banking
     API requests (TRANSFER, BALANCE, STATEMENT, FREEZE, WITHDRAW).
  2. Generates >= 30 VALID test cases from the grammar.
  3. Generates >= 15 INVALID test cases by mutating grammar structure.
  4. Parses generated sentences with an NLTK CFG parser and prints
     parse trees for demonstration.
  5. Prints a short evaluation summary of coverage.

---------------------------------------------------------------------
FORMAL GRAMMAR (mathematical / BNF notation)
---------------------------------------------------------------------

G = (N, T, P, S)

N (non-terminals) = { S, TransferReq, BalanceReq, StatementReq,
                       FreezeReq, WithdrawReq,
                       Account, Amount, Month, Reason, Branch, Digit }

T (terminals) = { TRANSFER, BALANCE, STATEMENT, FREEZE, WITHDRAW,
                   amount, from, to, account, for, month, reason, at,
                   ACC, ';', 0-9, January..December,
                   fraud_alert, court_order, kyc_pending,
                   suspicious_activity, aml_flag,
                   Nairobi_CBD, Mombasa_Road, Kisumu, Eldoret, Nakuru }

S (start symbol) = S

P (production rules):

  S               -> TransferReq ';'
                   |  BalanceReq ';'
                   |  StatementReq ';'
                   |  FreezeReq ';'
                   |  WithdrawReq ';'

  TransferReq     -> TRANSFER amount Amount from Account to Account
  BalanceReq      -> BALANCE account Account
  StatementReq    -> STATEMENT account Account for month Month
  FreezeReq       -> FREEZE account Account reason Reason
  WithdrawReq     -> WITHDRAW amount Amount from Account at Branch

  Account         -> ACC Digit Digit Digit
  Amount          -> Digit Digit Digit Digit
                   |  Digit Digit Digit Digit Digit
  Digit           -> 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9

  Month           -> January | February | March | April | May | June
                   |  July | August | September | October | November
                   |  December

  Reason          -> fraud_alert | court_order | kyc_pending
                   |  suspicious_activity | aml_flag

  Branch          -> Nairobi_CBD | Mombasa_Road | Kisumu | Eldoret
                   |  Nakuru

This grammar is unambiguous, right-recursion-free and finite-branching
per class, which keeps generation and chart-parsing tractable.
For PARSING (Section 3) we abstract Digit-strings into two lexical
categories, NUM and ACCOUNT, produced by a small lexer/tokenizer --
this is standard practice (lexer + CFG parser) because a pure CFG
that spells out every digit string is impractical to parse directly
with a general chart parser (unbounded terminal alphabet).
---------------------------------------------------------------------
"""

import random
import string
import nltk
from nltk import CFG
from nltk.parse import ChartParser

random.seed()  # non-deterministic runs; set an int for reproducibility

# ---------------------------------------------------------------------
# 1. NLTK CFG USED FOR PARSING (tokenised / lexed form)
#    NUM      stands for any numeric literal (amounts)
#    ACCOUNT  stands for any ACCxxx literal
# ---------------------------------------------------------------------
NLTK_GRAMMAR = CFG.fromstring("""
    S -> TRANSFER_REQ | BALANCE_REQ | STATEMENT_REQ | FREEZE_REQ | WITHDRAW_REQ

    TRANSFER_REQ  -> 'TRANSFER' 'amount' 'NUM' 'from' 'ACCOUNT' 'to' 'ACCOUNT'
    BALANCE_REQ   -> 'BALANCE' 'account' 'ACCOUNT'
    STATEMENT_REQ -> 'STATEMENT' 'account' 'ACCOUNT' 'for' 'month' MONTH
    FREEZE_REQ    -> 'FREEZE' 'account' 'ACCOUNT' 'reason' REASON
    WITHDRAW_REQ  -> 'WITHDRAW' 'amount' 'NUM' 'from' 'ACCOUNT' 'at' BRANCH

    MONTH  -> 'January' | 'February' | 'March' | 'April' | 'May' | 'June' | 'July' | 'August' | 'September' | 'October' | 'November' | 'December'

    REASON -> 'fraud_alert' | 'court_order' | 'kyc_pending' | 'suspicious_activity' | 'aml_flag'

    BRANCH -> 'Nairobi_CBD' | 'Mombasa_Road' | 'Kisumu' | 'Eldoret' | 'Nakuru'
""")

PARSER = ChartParser(NLTK_GRAMMAR)

MONTHS  = ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"]
REASONS = ["fraud_alert", "court_order", "kyc_pending",
           "suspicious_activity", "aml_flag"]
BRANCHES = ["Nairobi_CBD", "Mombasa_Road", "Kisumu", "Eldoret", "Nakuru"]

REQUEST_CLASSES = ["TRANSFER", "BALANCE", "STATEMENT", "FREEZE", "WITHDRAW"]


# ---------------------------------------------------------------------
# 2. TERMINAL / LEXICAL GENERATORS
# ---------------------------------------------------------------------
def gen_account():
    """Account -> ACC Digit Digit Digit  (extended to 3-4 digits for realism)"""
    return "ACC" + "".join(random.choice(string.digits) for _ in range(3))


def gen_amount():
    """Amount -> 4 or 5 digit numeral (KES 1,000 - 99,999 range)"""
    n_digits = random.choice([4, 5])
    first = random.choice("123456789")
    rest = "".join(random.choice(string.digits) for _ in range(n_digits - 1))
    return first + rest


def gen_month():
    return random.choice(MONTHS)


def gen_reason():
    return random.choice(REASONS)


def gen_branch():
    return random.choice(BRANCHES)


# ---------------------------------------------------------------------
# 3. VALID TEST CASE GENERATOR  (>= 30 required)
# ---------------------------------------------------------------------
def build_transfer():
    amt = gen_amount()
    src = gen_account()
    dst = gen_account()
    surface = f"TRANSFER amount {amt} from {src} to {dst};"
    tokens = ["TRANSFER", "amount", "NUM", "from", "ACCOUNT", "to", "ACCOUNT"]
    return surface, tokens


def build_balance():
    acc = gen_account()
    surface = f"BALANCE account {acc};"
    tokens = ["BALANCE", "account", "ACCOUNT"]
    return surface, tokens


def build_statement():
    acc = gen_account()
    month = gen_month()
    surface = f"STATEMENT account {acc} for month {month};"
    tokens = ["STATEMENT", "account", "ACCOUNT", "for", "month", month]
    return surface, tokens


def build_freeze():
    acc = gen_account()
    reason = gen_reason()
    surface = f"FREEZE account {acc} reason {reason};"
    tokens = ["FREEZE", "account", "ACCOUNT", "reason", reason]
    return surface, tokens


def build_withdraw():
    amt = gen_amount()
    acc = gen_account()
    branch = gen_branch()
    surface = f"WITHDRAW amount {amt} from {acc} at {branch};"
    tokens = ["WITHDRAW", "amount", "NUM", "from", "ACCOUNT", "at", branch]
    return surface, tokens


BUILDERS = {
    "TRANSFER": build_transfer,
    "BALANCE": build_balance,
    "STATEMENT": build_statement,
    "FREEZE": build_freeze,
    "WITHDRAW": build_withdraw,
}


def generate_valid_cases(n=30):
    """Round-robins across the 5 request classes so every class is covered
    roughly equally, then tops up randomly to reach n."""
    cases = []
    classes_cycle = REQUEST_CLASSES * (n // len(REQUEST_CLASSES) + 1)
    for cls in classes_cycle[:n]:
        surface, tokens = BUILDERS[cls]()
        cases.append({"class": cls, "text": surface, "tokens": tokens})
    return cases


# ---------------------------------------------------------------------
# 4. INVALID TEST CASE GENERATOR (>= 15 required)
#    Each mutator represents a distinct grammar-structure violation.
# ---------------------------------------------------------------------
def mutate_drop_keyword(case):
    """Remove a required keyword token (structural deletion)."""
    words = case["text"].rstrip(";").split()
    if len(words) > 2:
        idx = random.randint(1, len(words) - 2)
        del words[idx]
    return " ".join(words) + ";", "missing_keyword"


def mutate_swap_prepositions(case):
    """Swap 'from'/'to' or 'for'/'at' to break directional semantics."""
    text = case["text"]
    if "from" in text and "to" in text:
        text = text.replace("from", "TMP").replace("to", "from").replace("TMP", "to")
    elif "for" in text:
        text = text.replace("for", "at")
    return text, "swapped_preposition"


def mutate_unknown_verb(case):
    """Replace the leading transaction keyword with an undefined one."""
    words = case["text"].split()
    words[0] = random.choice(["TRANSFR", "PAY", "TOPUP", "CANCEL", "REVERSE"])
    return " ".join(words), "unknown_transaction_type"


def mutate_duplicate_clause(case):
    """Duplicate a clause fragment (structural repetition)."""
    words = case["text"].rstrip(";").split()
    if len(words) >= 4:
        frag = words[-2:]
        words = words + frag
    return " ".join(words) + ";", "duplicated_clause"


def mutate_malformed_account(case):
    """Break the Account -> ACC Digit Digit Digit rule."""
    text = case["text"]
    bad_variants = ["ACC12", "ACCXYZ", "12345", "ACC-123", "acc123"]
    if "ACC" in text:
        import re
        text = re.sub(r"ACC\d+", lambda m: random.choice(bad_variants), text, count=1)
    return text, "malformed_account_number"


def mutate_malformed_amount(case):
    """Break the Amount -> Digit+ rule (non-numeric / negative / words)."""
    text = case["text"]
    if "amount" in text:
        words = text.split()
        idx = words.index("amount") + 1
        words[idx] = random.choice(["-5000", "five_thousand", "5000.00KES", "NaN"])
        text = " ".join(words)
    return text, "malformed_amount"


def mutate_case_corruption(case):
    """Lowercase the keyword to violate the terminal's exact lexical form."""
    words = case["text"].split()
    words[0] = words[0].lower()
    return " ".join(words), "wrong_case_keyword"


def mutate_missing_terminator(case):
    """Drop the trailing ';' (protocol/lexical-level violation)."""
    return case["text"].rstrip(";"), "missing_semicolon"


def mutate_reordered_tokens(case):
    """Shuffle all tokens — total structural collapse."""
    words = case["text"].rstrip(";").split()
    random.shuffle(words)
    return " ".join(words) + ";", "reordered_tokens"


def mutate_truncated(case):
    """Cut the request short mid-way (incomplete request)."""
    words = case["text"].rstrip(";").split()
    cut = max(1, len(words) // 2)
    return " ".join(words[:cut]), "truncated_request"


def mutate_invalid_enum(case):
    """Replace an enumerated terminal (Month/Reason/Branch) with junk."""
    text = case["text"]
    for bad in ["Blursday", "unknown_reason_xyz", "Mars_Base_Branch"]:
        pass
    for real in MONTHS + REASONS + BRANCHES:
        if real in text:
            text = text.replace(real, random.choice(
                ["Blursday", "unknown_reason_xyz", "Mars_Base_Branch"]))
            break
    return text, "invalid_enumerated_value"


def mutate_extra_token(case):
    """Insert an unexpected extra token not licensed by any production."""
    words = case["text"].rstrip(";").split()
    idx = random.randint(0, len(words))
    words.insert(idx, random.choice(["URGENT", "***", "DEBUG_MODE"]))
    return " ".join(words) + ";", "unexpected_extra_token"


def mutate_sql_injection(case):
    """Security-oriented mutation: append an injection-style payload."""
    payload = random.choice([
        "; DROP TABLE transactions;",
        "' OR '1'='1",
        "; SELECT * FROM accounts;",
    ])
    return case["text"] + payload, "injection_attempt"


def mutate_oversized_amount(case):
    """Boundary/overflow mutation: absurdly long numeral."""
    text = case["text"]
    if "amount" in text:
        words = text.split()
        idx = words.index("amount") + 1
        words[idx] = "9" * 25
        text = " ".join(words)
    return text, "overflow_amount"


def mutate_wrong_field_type(case):
    """Put an Account literal where an Amount is expected, and vice versa
    (matches the sample: 'TRANSFER ACC123 amount to 5000')."""
    if case["class"] == "TRANSFER":
        acc = gen_account()
        amt = gen_amount()
        text = f"TRANSFER {acc} amount to {amt};"
        return text, "swapped_field_types"
    words = case["text"].split()
    return " ".join(reversed(words)), "swapped_field_types"


MUTATORS = [
    mutate_drop_keyword, mutate_swap_prepositions, mutate_unknown_verb,
    mutate_duplicate_clause, mutate_malformed_account, mutate_malformed_amount,
    mutate_case_corruption, mutate_missing_terminator, mutate_reordered_tokens,
    mutate_truncated, mutate_invalid_enum, mutate_extra_token,
    mutate_sql_injection, mutate_oversized_amount, mutate_wrong_field_type,
]


def _pick_seed(valid_cases, allowed_classes=None):
    """Pick a random seed, optionally restricted to classes for which the
    mutator is guaranteed to have something to mutate."""
    pool = [c for c in valid_cases if c["class"] in allowed_classes] \
        if allowed_classes else valid_cases
    return random.choice(pool)


# Some mutators only make structural sense (i.e. are guaranteed to change
# something) for certain request classes -- e.g. swapping from/to only
# matters for TRANSFER, and enum-corruption only applies to classes that
# actually contain an enumerated field (STATEMENT/FREEZE/WITHDRAW).
MUTATOR_CLASS_RESTRICTIONS = {
    mutate_swap_prepositions: ["TRANSFER", "STATEMENT"],
    mutate_invalid_enum: ["STATEMENT", "FREEZE", "WITHDRAW"],
    mutate_malformed_amount: ["TRANSFER", "WITHDRAW"],
    mutate_oversized_amount: ["TRANSFER", "WITHDRAW"],
    mutate_wrong_field_type: ["TRANSFER"],
    mutate_duplicate_clause: ["TRANSFER", "STATEMENT", "FREEZE", "WITHDRAW"],
}


def generate_invalid_cases(valid_cases, n=15):
    """Applies each of the >=15 distinct mutators to a randomly chosen
    valid seed case, guaranteeing 15 DIFFERENT failure modes (not just
    15 random ones), which is far more useful for coverage analysis."""
    invalid_cases = []
    for mutator in MUTATORS[:n]:
        allowed = MUTATOR_CLASS_RESTRICTIONS.get(mutator)
        seed = _pick_seed(valid_cases, allowed)
        text, label = mutator(seed)
        invalid_cases.append({"seed_class": seed["class"], "text": text, "mutation": label})
    return invalid_cases


# ---------------------------------------------------------------------
# 5. TOKENIZER + PARSER DEMONSTRATION
# ---------------------------------------------------------------------
def lex(text):
    """Convert a raw surface string into the abstracted token stream
    expected by NLTK_GRAMMAR (digits -> NUM, ACCxxx -> ACCOUNT)."""
    text = text.rstrip(";").rstrip()
    raw_tokens = text.split()
    lexed = []
    for tok in raw_tokens:
        # Strict lexical rule: ACCOUNT = 'ACC' followed by EXACTLY 3 digits.
        # Anything that merely looks similar (wrong digit count, letters,
        # missing prefix, lowercase) is left as a raw literal, which will
        # not match any terminal in NLTK_GRAMMAR and will correctly cause
        # a parse failure -- this is what lets the malformed-account
        # mutation be detected by the parser.
        if tok.startswith("ACC") and len(tok) == 6 and tok[3:].isdigit():
            lexed.append("ACCOUNT")
        elif tok.isdigit():
            lexed.append("NUM")
        else:
            lexed.append(tok)
    return lexed


def try_parse(text, label=""):
    """Attempt to parse a request string; report success/failure."""
    tokens = lex(text)
    try:
        trees = list(PARSER.parse(tokens))
    except ValueError as e:
        # token not in grammar's terminal vocabulary at all
        print(f"  [REJECTED] {label or text!r} -> lexical error: {e}")
        return None
    if trees:
        print(f"  [ACCEPTED] {label or text!r} -> {len(trees)} parse tree(s)")
        return trees
    else:
        print(f"  [REJECTED] {label or text!r} -> no valid parse (syntax error)")
        return None


# ---------------------------------------------------------------------
# 6. MAIN DEMONSTRATION
# ---------------------------------------------------------------------
def main():
    print("=" * 70)
    print("PART A: VALID TEST CASE GENERATION (>=30 required)")
    print("=" * 70)
    valid_cases = generate_valid_cases(30)
    for i, c in enumerate(valid_cases, 1):
        print(f"V{i:02d} [{c['class']:>9}] {c['text']}")

    print("\n" + "=" * 70)
    print("PART B: PARSE TREE DEMONSTRATION (2+ required)")
    print("=" * 70)
    # Pick one TRANSFER and one FREEZE example explicitly for the report
    demo_transfer = next(c for c in valid_cases if c["class"] == "TRANSFER")
    demo_freeze = next(c for c in valid_cases if c["class"] == "FREEZE")
    for demo in (demo_transfer, demo_freeze):
        print(f"\nInput: {demo['text']}")
        tokens = lex(demo["text"])
        trees = list(PARSER.parse(tokens))
        for t in trees:
            print(t)
            t.pretty_print()

    print("\n" + "=" * 70)
    print("PART C: PARSING ALL VALID CASES (sanity check)")
    print("=" * 70)
    accepted, rejected = 0, 0
    for c in valid_cases:
        tokens = lex(c["text"])
        trees = list(PARSER.parse(tokens))
        if trees:
            accepted += 1
        else:
            rejected += 1
            print(f"  UNEXPECTED REJECTION: {c['text']}")
    print(f"Valid cases accepted by parser: {accepted}/{len(valid_cases)}")

    print("\n" + "=" * 70)
    print("PART D: INVALID TEST CASE GENERATION (>=15 required)")
    print("=" * 70)
    invalid_cases = generate_invalid_cases(valid_cases, n=15)
    for i, c in enumerate(invalid_cases, 1):
        print(f"I{i:02d} [{c['mutation']:<25}] {c['text']}")

    print("\n" + "=" * 70)
    print("PART E: CONFIRMING INVALID CASES ARE REJECTED (or flagged) BY PARSER")
    print("=" * 70)
    caught, missed = 0, 0
    for c in invalid_cases:
        tokens = lex(c["text"])
        try:
            trees = list(PARSER.parse(tokens))
        except ValueError:
            trees = []
        if trees:
            missed += 1
            print(f"  NOT CAUGHT by CFG parser (needs semantic/lexical rule): "
                  f"[{c['mutation']}] {c['text']}")
        else:
            caught += 1
    print(f"\nInvalid cases rejected by pure syntax parser: {caught}/{len(invalid_cases)}")
    print(f"Invalid cases that slipped past pure CFG parsing "
          f"(need extra lexical/semantic checks): {missed}/{len(invalid_cases)}")


if __name__ == "__main__":
    main()
