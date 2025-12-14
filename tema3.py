#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generator tabele ACTION/GOTO (tabele de funcționare APD) pentru gramatici LR(1)
și export un singur fișier CSV numit `result.csv` (în loc de afișare în consolă).

Rulare:
  python3 lr1_table_generator_csv.py --file gram.txt

Dacă nu se dă --file, se folosește gramatică exemplu.
"""
from collections import defaultdict, deque
import csv
import argparse
import pprint

ENDMARK = '$'
EPS = 'ε'  # simbol folosit intern pentru epsilon


def parse_grammar(text):
    G = defaultdict(list)
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '->' not in line:
            raise ValueError(f"Lipsea '->' pe linia: {line}")
        left, right = line.split('->', 1)
        A = left.strip()
        alts = [alt.strip() for alt in right.split('|')]
        for alt in alts:
            if alt == '' or alt in ('ε', 'eps', 'empty'):
                rhs = []
            else:
                rhs = alt.split()
            G[A].append(rhs)
    return dict(G)


def compute_terminals_and_nonterminals(G):
    nonterms = set(G.keys())
    terms = set()
    for A, prods in G.items():
        for rhs in prods:
            for sym in rhs:
                if sym == EPS:
                    continue
                if sym not in nonterms:
                    terms.add(sym)
    return terms, nonterms


def compute_first_sets(G, terminals, nonterms):
    FIRST = {t: {t} for t in terminals}
    for N in nonterms:
        FIRST[N] = set()
    FIRST[EPS] = {EPS}

    changed = True
    while changed:
        changed = False
        for A, prods in G.items():
            for rhs in prods:
                if not rhs:
                    if EPS not in FIRST[A]:
                        FIRST[A].add(EPS)
                        changed = True
                    continue
                add_eps = True
                for sym in rhs:
                    before = len(FIRST[A])
                    if sym not in FIRST:
                        FIRST[sym] = {sym}
                    FIRST[A].update(x for x in FIRST[sym] if x != EPS)
                    after = len(FIRST[A])
                    if after > before:
                        changed = True
                    if EPS in FIRST[sym]:
                        add_eps = True
                        continue
                    else:
                        add_eps = False
                        break
                if add_eps:
                    if EPS not in FIRST[A]:
                        FIRST[A].add(EPS)
                        changed = True
    return FIRST


def first_of_sequence(seq, FIRST):
    if not seq:
        return {EPS}
    res = set()
    for sym in seq:
        if sym not in FIRST:
            res.add(sym)
            return res
        res.update(x for x in FIRST[sym] if x != EPS)
        if EPS in FIRST[sym]:
            continue
        else:
            break
    else:
        res.add(EPS)
    return res


def make_item(A, rhs, dot, la):
    return (A, tuple(rhs), dot, la)


def closure(items, G, FIRST):
    I = set(items)
    added = True
    while added:
        added = False
        new_items = set()
        for item in I:
            A, rhs, dot, la = item
            if dot < len(rhs):
                B = rhs[dot]
                if B in G:
                    beta = list(rhs[dot+1:])
                    for prod in G[B]:
                        seq = beta + [la]
                        first_seq = first_of_sequence(seq, FIRST)
                        for b in first_seq:
                            if b == EPS:
                                continue
                            new_item = make_item(B, prod, 0, b)
                            if new_item not in I:
                                new_items.add(new_item)
        if new_items:
            I |= new_items
            added = True
    return frozenset(I)


def goto(I, X, G, FIRST):
    moved = set()
    for item in I:
        A, rhs, dot, la = item
        if dot < len(rhs) and rhs[dot] == X:
            moved.add(make_item(A, list(rhs), dot+1, la))
    if not moved:
        return frozenset()
    return closure(moved, G, FIRST)


def canonical_LR1_collection(G):
    starts = list(G.keys())
    if not starts:
        raise RuntimeError("Gramatică goală")
    start = starts[0]
    G_aug = {k: [list(p) for p in v] for k, v in G.items()}
    S_prime = start + "'"
    i = 1
    while S_prime in G_aug:
        S_prime = f"{start}'{i}"
        i += 1
    G_aug[S_prime] = [[start]]

    terminals, nonterms = compute_terminals_and_nonterminals(G_aug)
    FIRST = compute_first_sets(G_aug, terminals, set(G_aug.keys()))

    init_item = make_item(S_prime, [start], 0, ENDMARK)
    I0 = closure({init_item}, G_aug, FIRST)
    states = [I0]
    state_ids = {I0: 0}
    transitions = dict()

    q = deque([I0])
    while q:
        I = q.popleft()
        sid = state_ids[I]
        symbols = set()
        for item in I:
            A, rhs, dot, la = item
            if dot < len(rhs):
                symbols.add(rhs[dot])
        for X in symbols:
            J = goto(I, X, G_aug, FIRST)
            if not J:
                continue
            if J not in state_ids:
                state_ids[J] = len(states)
                states.append(J)
                q.append(J)
            transitions[(sid, X)] = state_ids[J]
    return states, transitions, G_aug, S_prime, FIRST


def build_parsing_table(states, transitions, G_aug, S_prime, FIRST):
    ACTION = dict()
    GOTO = dict()
    conflicts = []

    prods = []
    for A, plist in G_aug.items():
        for rhs in plist:
            prods.append((A, tuple(rhs)))

    terminals, nonterms = compute_terminals_and_nonterminals(G_aug)
    terminals = set(terminals)
    nonterms = set(G_aug.keys())

    for sid, I in enumerate(states):
        for item in I:
            A, rhs, dot, la = item
            if dot < len(rhs):
                a = rhs[dot]
                if a not in nonterms:
                    if (sid, a) in transitions:
                        t = transitions[(sid, a)]
                        key = (sid, a)
                        entry = ("shift", t)
                        if key in ACTION and ACTION[key] != entry:
                            conflicts.append(("conflict", sid, a, ACTION[key], entry))
                        else:
                            ACTION[key] = entry
            else:
                if A == S_prime:
                    if la == ENDMARK:
                        ACTION[(sid, ENDMARK)] = ("accept",)
                else:
                    key = (sid, la)
                    entry = ("reduce", (A, tuple(rhs)))
                    if key in ACTION and ACTION[key] != entry:
                        conflicts.append(("conflict", sid, la, ACTION[key], entry))
                    else:
                        ACTION[key] = entry
        for B in nonterms:
            if (sid, B) in transitions:
                GOTO[(sid, B)] = transitions[(sid, B)]
    return ACTION, GOTO, conflicts


def format_action_cell(v):
    if not v:
        return ""
    if v[0] == "shift":
        return f"s{v[1]}"
    elif v[0] == "reduce":
        A, rhs = v[1]
        rhs_s = " ".join(rhs) if rhs else EPS
        return f"r[{A}->{rhs_s}]"
    elif v[0] == "accept":
        return "acc"
    else:
        return str(v)


def export_result_csv(action, goto, terminals, nonterms, num_states, filename="result.csv"):
    ter_list = sorted(list(terminals) + [ENDMARK])
    non_list = sorted(list(nonterms))
    header = ["state"] + ter_list + non_list
    with open(filename, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for s in range(num_states):
            row = [s]
            for t in ter_list:
                row.append(format_action_cell(action.get((s, t), "")))
            for N in non_list:
                row.append(goto.get((s, N), ""))
            writer.writerow(row)
    print(f"Am creat fișierul: {filename}")


def example_grammar_text():
    return """
S -> E
E -> E + T | T
T -> T * F | F
F -> ( E ) | id
""".strip()


def main():
    parser = argparse.ArgumentParser(description="Generator tabele LR(1) și export result.csv.")
    parser.add_argument("--file", "-f", help="Fișier text cu gramatica", default=None)
    args = parser.parse_args()

    if args.file:
        with open(args.file, encoding='utf-8') as fh:
            text = fh.read()
    else:
        print("Nu s-a dat fișier; folosesc exemplu clasic (E -> E + T ...).")
        text = example_grammar_text()

    G = parse_grammar(text)
    print("Gramatică parsată (sumar):")
    pprint.pprint(G)
    print()

    states, transitions, G_aug, S_prime, FIRST = canonical_LR1_collection(G)
    print(f"Gramatică augmentată start: {S_prime}")
    print(f"Număr stări: {len(states)}")

    ACTION, GOTO, conflicts = build_parsing_table(states, transitions, G_aug, S_prime, FIRST)

    # export într-un singur CSV (result.csv)
    terminals, nonterms = compute_terminals_and_nonterminals(G_aug)
    export_result_csv(ACTION, GOTO, terminals, nonterms, len(states), filename="result.csv")

    if conflicts:
        print("Conflicte detectate:")
        for c in conflicts:
            print(" ", c)
    else:
        print("Nicio conflict detectat (sau nu a fost raportat).")


if __name__ == "__main__":
    main()