import csv
import sys
from collections import defaultdict
import os

class RegexTreeNode:
    def __init__(self, val, l_child=None, r_child=None):
        self.val = val
        self.l_child = l_child
        self.r_child = r_child

    def __repr__(self):
        return f"RegexTreeNode({self.val})"

class AutomatonState:
    def __init__(self):
        self.symbol_transitions = {}
        self.epsilon_transitions = []

    def add_symbol_transition(self, symbol, target_state):
        if symbol not in self.symbol_transitions:
            self.symbol_transitions[symbol] = []
        self.symbol_transitions[symbol].append(target_state)

    def add_epsilon_transition(self, target_state):
        self.epsilon_transitions.append(target_state)

class FiniteAutomaton:
    def __init__(self, initial_state, final_state):
        self.initial_state = initial_state
        self.final_state = final_state

def is_regular_char(char):
    return char not in "+*()|"

def regex_to_tree(expression):
    def parse(tokens):
        def next_token():
            return tokens.pop(0) if tokens else None

        def parse_simple():
            token = next_token()
            if token == "\\":
                escaped = next_token()
                if is_regular_char(escaped):
                    tokens.insert(0, escaped)
                else:
                    return RegexTreeNode(escaped)
            if is_regular_char(token):
                return RegexTreeNode(token)
            elif token == "(":
                node = parse_expr()
                if next_token() != ")":
                    raise ValueError("Mismatched parentheses")
                return node
            raise ValueError(f"Unexpected token: {token}")

        def parse_element():
            node = parse_simple()
            while tokens and tokens[0] in ("*", "+"):
                op = "repeat" if next_token() == "*" else "plus"
                node = RegexTreeNode(op, l_child=node)
            return node

        def parse_sequence():
            node = parse_element()
            while tokens and tokens[0] and (is_regular_char(tokens[0]) or tokens[0] == "("):
                right = parse_element()
                node = RegexTreeNode("sequence", l_child=node, r_child=right)
            return node

        def parse_expr():
            node = parse_sequence()
            while tokens and tokens[0] == "|":
                next_token()
                right = parse_sequence()
                node = RegexTreeNode("choice", l_child=node, r_child=right)
            return node

        return parse_expr()

    tokens = []
    for char in expression:
        tokens.append(char)

    return parse(tokens)

def construct_automaton(node):
    if node is None:
        return None

    if node.val not in ("sequence", "choice", "plus", "repeat"):
        start = AutomatonState()
        accept = AutomatonState()
        start.add_symbol_transition(node.val, accept)
        return FiniteAutomaton(start, accept)
    elif node.val == "sequence":
        left_automaton = construct_automaton(node.l_child)
        right_automaton = construct_automaton(node.r_child)
        left_automaton.final_state.add_epsilon_transition(right_automaton.initial_state)
        return FiniteAutomaton(left_automaton.initial_state, right_automaton.final_state)
    elif node.val == "choice":
        start = AutomatonState()
        accept = AutomatonState()
        left_automaton = construct_automaton(node.l_child)
        right_automaton = construct_automaton(node.r_child)
        start.add_epsilon_transition(left_automaton.initial_state)
        start.add_epsilon_transition(right_automaton.initial_state)
        left_automaton.final_state.add_epsilon_transition(accept)
        right_automaton.final_state.add_epsilon_transition(accept)
        return FiniteAutomaton(start, accept)
    elif node.val == "repeat":
        start = AutomatonState()
        accept = AutomatonState()
        sub_automaton = construct_automaton(node.l_child)
        start.add_epsilon_transition(sub_automaton.initial_state)
        start.add_epsilon_transition(accept)
        sub_automaton.final_state.add_epsilon_transition(sub_automaton.initial_state)
        sub_automaton.final_state.add_epsilon_transition(accept)
        return FiniteAutomaton(start, accept)
    elif node.val == "plus":
        start = AutomatonState()
        accept = AutomatonState()
        sub_automaton = construct_automaton(node.l_child)
        start.add_epsilon_transition(sub_automaton.initial_state)
        sub_automaton.final_state.add_epsilon_transition(sub_automaton.initial_state)
        sub_automaton.final_state.add_epsilon_transition(accept)
        return FiniteAutomaton(start, accept)

    raise ValueError(f"Unexpected node value: {node.val}")

def epsilon_closure(state, visited=None):
    if visited is None:
        visited = set()
    
    if state in visited:
        return set()
    
    visited.add(state)
    closure = {state}
    
    for epsilon_state in state.epsilon_transitions:
        closure.update(epsilon_closure(epsilon_state, visited))
    
    return closure

def nfa_to_dfa(nfa):
    initial_closure = epsilon_closure(nfa.initial_state)
    dfa_states = []
    dfa_transitions = []
    unprocessed_states = [initial_closure]
    dfa_state_map = {frozenset(initial_closure): "S0"}
    
    is_final = any(state == nfa.final_state for state in initial_closure)
    dfa_states.append({
        "name": "S0",
        "is_final": is_final,
        "transitions": {}
    })
    
    while unprocessed_states:
        current_states = unprocessed_states.pop(0)
        current_state_name = dfa_state_map[frozenset(current_states)]

        symbols = set()
        for state in current_states:
            symbols.update(state.symbol_transitions.keys())
        
        for symbol in symbols:
            next_states = set()
            for state in current_states:
                if symbol in state.symbol_transitions:
                    for target in state.symbol_transitions[symbol]:
                        next_states.update(epsilon_closure(target))
            
            if not next_states:
                continue
            
            frozen_next = frozenset(next_states)
            if frozen_next not in dfa_state_map:
                new_state_name = f"S{len(dfa_state_map)}"
                dfa_state_map[frozen_next] = new_state_name
                is_final = any(state == nfa.final_state for state in next_states)
                dfa_states.append({
                    "name": new_state_name,
                    "is_final": is_final,
                    "transitions": {}
                })
                unprocessed_states.append(next_states)
            
            dfa_states[dfa_state_map[frozenset(current_states)]]["transitions"][symbol] = dfa_state_map[frozen_next]
    
    return dfa_states

def save_dfa_to_csv(dfa_states, output_file):
    # Create _tmp directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Collect all symbols
    symbols = set()
    for state in dfa_states:
        symbols.update(state["transitions"].keys())
    symbols = sorted(symbols)
    
    # Write CSV file
    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        
        # Write header
        writer.writerow(["State"] + symbols + ["Final"])
        
        # Write states
        for state in dfa_states:
            row = [state["name"]]
            for symbol in symbols:
                row.append(state["transitions"].get(symbol, "-"))
            row.append("F" if state["is_final"] else "")
            writer.writerow(row)

def main():
    if len(sys.argv) < 2:
        print("Usage: python regex.py <regex_pattern>")
        return 1

    regex_pattern = sys.argv[1]
    output_file = "_tmp/output.csv"  # Fixed output path

    try:
        tree = regex_to_tree(regex_pattern)
        nfa = construct_automaton(tree)
        dfa_states = nfa_to_dfa(nfa)
        save_dfa_to_csv(dfa_states, output_file)
        print(f"DFA saved to {output_file}")
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())