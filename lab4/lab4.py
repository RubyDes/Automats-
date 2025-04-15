import sys
from collections import defaultdict, deque

class State:
    def __init__(self):
        self.name = ""
        self.transitions = defaultdict(list)
        self.epsilon = []
        self.is_final = False

def read_table(filename):
    with open(filename, 'r', encoding='utf-8-sig') as f:
        return [line.strip().split(';') for line in f]

def write_table(filename, table):
    with open(filename, 'w', encoding='utf-8') as f:
        for row in table:
            f.write(';'.join(row) + '\n')

def parse_automaton(input_table):
    # Try to find epsilon row (optional)
    epsilon_row = -1
    for i, row in enumerate(input_table):
        if row and row[0].lower() in ('ε', 'e'):
            epsilon_row = i
            break
    
    # Parse states
    states = {}
    header = input_table[1]
    for col in range(1, len(header)):
        state_name = header[col].strip()
        if not state_name:
            continue
            
        state = State()
        state.name = state_name
        state.is_final = (input_table[0][col].strip() == 'F') if col < len(input_table[0]) else False
        
        # Parse epsilon transitions if epsilon row exists
        if epsilon_row != -1 and col < len(input_table[epsilon_row]):
            epsilons = input_table[epsilon_row][col].strip()
            if epsilons and epsilons != '-':
                state.epsilon = [s.strip() for s in epsilons.split(',') if s.strip()]
        
        # Parse regular transitions
        for row in range(2, len(input_table)):
            if row == epsilon_row:
                continue
            if not input_table[row]:
                continue
                
            symbol = input_table[row][0].strip()
            if not symbol:
                continue
                
            if col < len(input_table[row]):
                targets = input_table[row][col].strip()
                if targets and targets != '-':
                    state.transitions[symbol] = [s.strip() for s in targets.split(',') if s.strip()]
        
        states[state_name] = state
    
    return states

def epsilon_closure(states, start_state):
    if start_state not in states:
        return frozenset()
        
    closure = set()
    queue = deque()
    queue.append(start_state)
    
    while queue:
        current = queue.popleft()
        if current in closure:
            continue
            
        closure.add(current)
        for neighbor in states[current].epsilon:
            if neighbor not in closure:
                queue.append(neighbor)
    
    return frozenset(closure)

def build_dfa(nfa_states):
    if not nfa_states:
        return {}
    
    # Get initial state(s) - handle both with and without epsilon transitions
    initial_state = next(iter(nfa_states))
    initial_closure = epsilon_closure(nfa_states, initial_state)
    
    if not initial_closure:  # No epsilon transitions case
        initial_closure = frozenset([initial_state])
    
    dfa_states = {}
    state_queue = deque()
    
    # Create initial DFA state
    dfa_states[initial_closure] = {
        'name': 'S0',
        'transitions': {},
        'is_final': any(nfa_states[s].is_final for s in initial_closure)
    }
    state_queue.append(initial_closure)
    
    # Get all symbols from the NFA
    symbol_set = set()
    for state in nfa_states.values():
        symbol_set.update(state.transitions.keys())
    
    # Process all states
    while state_queue:
        current_closure = state_queue.popleft()
        
        for symbol in symbol_set:
            # Move on symbol
            move_set = set()
            for state in current_closure:
                move_set.update(nfa_states[state].transitions.get(symbol, []))
            
            if not move_set:
                continue
                
            # Epsilon closure of move set (if any epsilon transitions exist)
            new_closure = set()
            for state in move_set:
                closure = epsilon_closure(nfa_states, state)
                if closure:
                    new_closure.update(closure)
                else:
                    new_closure.add(state)
            
            if not new_closure:
                continue
                
            new_closure = frozenset(new_closure)
            
            # Add new state if needed
            if new_closure not in dfa_states:
                state_name = f'S{len(dfa_states)}'
                dfa_states[new_closure] = {
                    'name': state_name,
                    'transitions': {},
                    'is_final': any(nfa_states[s].is_final for s in new_closure)
                }
                state_queue.append(new_closure)
            
            # Add transition
            dfa_states[current_closure]['transitions'][symbol] = dfa_states[new_closure]['name']
    
    return dfa_states

def create_output_table(dfa_states, symbols):
    # Prepare header
    output = [[''], ['']]
    
    # Add state names to header
    for state in dfa_states.values():
        output[0].append('F' if state['is_final'] else '')
        output[1].append(state['name'])
    
    # Add transitions for each symbol
    for symbol in sorted(symbols):
        row = [symbol]
        for state in dfa_states.values():
            row.append(state['transitions'].get(symbol, ''))
        output.append(row)
    
    return output

def main():
    if len(sys.argv) != 3:
        print("Usage: python lab4.py <input_file> <output_file>")
        return
    
    try:
        # Read and parse input
        input_table = read_table(sys.argv[1])
        nfa_states = parse_automaton(input_table)
        
        # Convert NFA to DFA
        dfa_states = build_dfa(nfa_states)
        
        if not dfa_states:
            print("Error: No valid states found in input")
            return
        
        # Get all symbols from input
        symbols = set()
        for row in input_table[2:]:
            if row and row[0].lower() not in ('ε', 'e'):
                symbols.add(row[0])
        
        # Create output table
        output_table = create_output_table(dfa_states, symbols)
        
        # Write output
        write_table(sys.argv[2], output_table)
        print("Conversion completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()