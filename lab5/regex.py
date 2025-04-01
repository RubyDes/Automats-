import sys
import csv
import os
from collections import defaultdict, OrderedDict

class State:
    _counter = 0
    
    def __init__(self):
        self.name = f"S{State._counter}"
        State._counter += 1
        self.transitions = defaultdict(list)
        self.is_final = False

class NFA:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.end.is_final = True

def parse_regex(regex):
    stack = []
    i = 0
    
    while i < len(regex):
        c = regex[i]
        
        if c == '\\':
            i += 1
            if i >= len(regex):
                raise ValueError("Invalid escape sequence")
            c = regex[i]
            s1 = State()
            s2 = State()
            s1.transitions[c].append(s2)
            stack.append(NFA(s1, s2))
        elif c == '(':
            stack.append(c)
        elif c == ')':
            # Process until matching '('
            nfas = []
            while stack and stack[-1] != '(':
                nfas.append(stack.pop())
            if not stack:
                raise ValueError("Mismatched parentheses")
            stack.pop()  # Remove '('
            
            # Handle empty parentheses ()
            if not nfas:
                empty = State()
                stack.append(NFA(empty, empty))
                i += 1
                continue
                
            # Handle concatenation
            while len(nfas) > 1:
                nfa2 = nfas.pop()
                nfa1 = nfas.pop()
                nfa1.end.transitions['ε'].append(nfa2.start)
                nfas.append(NFA(nfa1.start, nfa2.end))
            
            stack.append(nfas[0])
        elif c == '|':
            stack.append(c)
        elif c in ['*', '+', '?']:
            if not stack or stack[-1] == '(' or stack[-1] == '|':
                raise ValueError(f"Nothing to repeat with '{c}'")
            nfa = stack.pop()
            
            new_start = State()
            new_end = State()
            
            if c == '*':
                new_start.transitions['ε'].append(nfa.start)
                new_start.transitions['ε'].append(new_end)
                nfa.end.transitions['ε'].append(nfa.start)
                nfa.end.transitions['ε'].append(new_end)
            elif c == '+':
                new_start.transitions['ε'].append(nfa.start)
                nfa.end.transitions['ε'].append(nfa.start)
                nfa.end.transitions['ε'].append(new_end)
            elif c == '?':
                new_start.transitions['ε'].append(nfa.start)
                new_start.transitions['ε'].append(new_end)
                nfa.end.transitions['ε'].append(new_end)
            
            nfa.end.is_final = False
            stack.append(NFA(new_start, new_end))
        else:
            s1 = State()
            s2 = State()
            s1.transitions[c].append(s2)
            stack.append(NFA(s1, s2))
        
        i += 1
    
    # Process remaining concatenations and alternations
    while len(stack) > 1:
        top = stack.pop()
        if top == '|':
            # Handle alternation
            if len(stack) < 2:
                raise ValueError("Invalid alternation")
            right = stack.pop()
            stack.pop()  # Remove '|'
            left = stack.pop()
            
            new_start = State()
            new_end = State()
            new_start.transitions['ε'].append(left.start)
            new_start.transitions['ε'].append(right.start)
            left.end.transitions['ε'].append(new_end)
            right.end.transitions['ε'].append(new_end)
            left.end.is_final = False
            right.end.is_final = False
            
            stack.append(NFA(new_start, new_end))
        else:
            # Handle concatenation
            next_top = stack.pop()
            next_top.end.transitions['ε'].append(top.start)
            stack.append(NFA(next_top.start, top.end))
    
    if not stack or stack[-1] == '|':
        raise ValueError("Invalid regular expression")
    
    return stack[-1]

def save_nfa_to_csv(nfa, filename):
    # Collect all states with BFS
    visited = OrderedDict()
    queue = [nfa.start]
    
    while queue:
        state = queue.pop(0)
        if state in visited:
            continue
        visited[state] = True
        
        for _, targets in state.transitions.items():
            for target in targets:
                if target not in visited:
                    queue.append(target)
    
    # Get all unique symbols (excluding ε)
    symbols = set()
    for state in visited:
        symbols.update(state.transitions.keys())
    symbols.discard('ε')
    symbols = sorted(symbols)
    
    # Create transition map
    transition_map = {}
    for state in visited:
        trans = {}
        for symbol in symbols:
            targets = state.transitions.get(symbol, [])
            trans[symbol] = ",".join(sorted(t.name for t in targets)) if targets else "-"
        transition_map[state.name] = trans
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        
        # Write header
        writer.writerow(['State'] + symbols + ['Final'])
        
        # Write states in order they were visited
        for state in visited:
            row = [state.name]
            for symbol in symbols:
                row.append(transition_map[state.name][symbol])
            row.append('F' if state.is_final else '')
            writer.writerow(row)

def main():
    if len(sys.argv) < 3:
        print("Usage: python regexToNFA.py output.csv \"regex_pattern\"")
        sys.exit(1)
    
    output_file = sys.argv[1]
    regex_pattern = sys.argv[2]
    
    try:
        # Reset state counter for each run
        State._counter = 0
        
        nfa = parse_regex(regex_pattern)
        save_nfa_to_csv(nfa, output_file)
        print(f"NFA saved to {output_file}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()