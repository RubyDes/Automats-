import csv
import sys
import os
from collections import defaultdict

class State:
    def __init__(self, name):
        self.name = name
        self.is_final = False
        self.transitions = defaultdict(list)

class NFA:
    def __init__(self, start, end):
        self.start = start
        self.end = end

def regex_to_nfa(regex):
    stack = []
    i = 0
    n = len(regex)
    
    while i < n:
        char = regex[i]
        
        if char == '\\':
            i += 1
            if i >= n:
                raise ValueError("Invalid escape sequence")
            char = regex[i]
            s1 = State(char)
            s2 = State(char)
            s1.transitions[char].append(s2)
            stack.append(NFA(s1, s2))
            i += 1
            continue
            
        if char == '(':
            stack.append(char)
        elif char == ')':
            nfas = []
            while stack and stack[-1] != '(':
                nfas.append(stack.pop())
            if not stack:
                raise ValueError("Mismatched parentheses")
            stack.pop()  # Remove '('
            
            # Handle concatenation
            while len(nfas) > 1:
                nfa2 = nfas.pop()
                nfa1 = nfas.pop()
                nfa1.end.transitions['ε'].append(nfa2.start)
                nfas.append(NFA(nfa1.start, nfa2.end))
            
            if not nfas:
                raise ValueError("Empty parentheses")
                
            stack.append(nfas[0])
        elif char == '|':
            stack.append(char)
        elif char in ['*', '+', '?']:
            if not stack or isinstance(stack[-1], str):
                raise ValueError(f"Invalid operator {char}")
            nfa = stack.pop()
            
            new_start = State('ε')
            new_end = State('ε')
            
            if char == '*':
                new_start.transitions['ε'].append(nfa.start)
                new_start.transitions['ε'].append(new_end)
                nfa.end.transitions['ε'].append(nfa.start)
                nfa.end.transitions['ε'].append(new_end)
            elif char == '+':
                new_start.transitions['ε'].append(nfa.start)
                nfa.end.transitions['ε'].append(nfa.start)
                nfa.end.transitions['ε'].append(new_end)
            elif char == '?':
                new_start.transitions['ε'].append(nfa.start)
                new_start.transitions['ε'].append(new_end)
                nfa.end.transitions['ε'].append(new_end)
                
            stack.append(NFA(new_start, new_end))
        else:
            s1 = State(char)
            s2 = State(char)
            s1.transitions[char].append(s2)
            stack.append(NFA(s1, s2))
        
        i += 1
    
    # Process remaining concatenations
    while len(stack) > 1:
        top = stack.pop()
        if isinstance(top, str):
            raise ValueError("Invalid regex pattern")
        next_top = stack.pop()
        if isinstance(next_top, str):
            raise ValueError("Invalid regex pattern")
        
        next_top.end.transitions['ε'].append(top.start)
        stack.append(NFA(next_top.start, top.end))
    
    if not stack or isinstance(stack[-1], str):
        raise ValueError("Invalid regex pattern")
    
    final_nfa = stack[-1]
    final_nfa.end.is_final = True
    return final_nfa

def nfa_to_dfa(nfa):
    def epsilon_closure(states):
        closure = set(states)
        stack = list(states)
        
        while stack:
            state = stack.pop()
            for next_state in state.transitions.get('ε', []):
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        
        return frozenset(closure)
    
    initial_closure = epsilon_closure({nfa.start})
    dfa_states = []
    state_queue = [initial_closure]
    state_map = {initial_closure: 'S0'}
    
    dfa_states.append({
        'name': 'S0',
        'states': initial_closure,
        'is_final': any(s.is_final for s in initial_closure),
        'transitions': {}
    })
    
    while state_queue:
        current_states = state_queue.pop(0)
        current_name = state_map[current_states]
        
        # Find all unique symbols (excluding ε)
        symbols = set()
        for state in current_states:
            symbols.update(state.transitions.keys())
        symbols.discard('ε')
        
        for symbol in sorted(symbols):
            # Move to next states on this symbol
            next_states = set()
            for state in current_states:
                if symbol in state.transitions:
                    next_states.update(state.transitions[symbol])
            
            if not next_states:
                continue
                
            closure = epsilon_closure(next_states)
            
            if closure not in state_map:
                new_name = f'S{len(state_map)}'
                state_map[closure] = new_name
                dfa_states.append({
                    'name': new_name,
                    'states': closure,
                    'is_final': any(s.is_final for s in closure),
                    'transitions': {}
                })
                state_queue.append(closure)
            
            # Find the current state in dfa_states
            for state in dfa_states:
                if state['name'] == current_name:
                    state['transitions'][symbol] = state_map[closure]
                    break
    
    return dfa_states

def save_dfa_to_csv(dfa_states, filename):
    # Get all unique symbols
    symbols = set()
    for state in dfa_states:
        symbols.update(state['transitions'].keys())
    symbols = sorted(symbols)
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        
        # Write header
        writer.writerow(['State'] + symbols + ['Final'])
        
        # Write each state
        for state in dfa_states:
            row = [state['name']]
            for symbol in symbols:
                row.append(state['transitions'].get(symbol, '-'))
            row.append('F' if state['is_final'] else '')
            writer.writerow(row)

def main():
    if len(sys.argv) < 2:
        print("Usage: python regex_to_dfa.py <regex_pattern> [output_file]")
        return 1
    
    regex = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else '_tmp/output.csv'
    
    try:
        nfa = regex_to_nfa(regex)
        dfa_states = nfa_to_dfa(nfa)
        save_dfa_to_csv(dfa_states, output_file)
        print(f"DFA saved to {output_file}")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())