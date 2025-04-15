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
    epsilon_row = -1
    for i, row in enumerate(input_table):
        if row and row[0].lower() in ('ε', 'e'):
            epsilon_row = i
            break
    
    states = {}
    header = input_table[1]
    for col in range(1, len(header)):
        state_name = header[col].strip()
        if not state_name:
            continue
            
        state = State()
        state.name = state_name
        state.is_final = (input_table[0][col].strip() == 'F') if col < len(input_table[0]) else False
        
        if epsilon_row != -1 and col < len(input_table[epsilon_row]):
            epsilons = input_table[epsilon_row][col].strip()
            if epsilons and epsilons != '-':
                state.epsilon = [s.strip() for s in epsilons.split(',') if s.strip()]
        
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
        
    if not states[start_state].epsilon:
        return frozenset([start_state])
        
    closure = set()
    queue = deque([start_state])
    
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
    
    initial_state = next(iter(nfa_states))
    initial_closure = epsilon_closure(nfa_states, initial_state) or frozenset([initial_state])
    
    dfa_states = {}
    state_queue = deque([initial_closure])
    dfa_states[initial_closure] = {
        'name': 'S0',
        'transitions': {},
        'is_final': any(nfa_states[s].is_final for s in initial_closure)
    }
    
    symbol_set = set()
    for state in nfa_states.values():
        symbol_set.update(state.transitions.keys())
    
    while state_queue:
        current_closure = state_queue.popleft()
        
        for symbol in symbol_set:
            move_set = set()
            for state in current_closure:
                move_set.update(nfa_states[state].transitions.get(symbol, []))
            
            if not move_set:
                continue
                
            new_closure = set()
            for state in move_set:
                closure = epsilon_closure(nfa_states, state) or {state}
                new_closure.update(closure)
            
            new_closure = frozenset(new_closure)
            
            if new_closure not in dfa_states:
                state_name = f'S{len(dfa_states)}'
                dfa_states[new_closure] = {
                    'name': state_name,
                    'transitions': {},
                    'is_final': any(nfa_states[s].is_final for s in new_closure)
                }
                state_queue.append(new_closure)
            
            dfa_states[current_closure]['transitions'][symbol] = dfa_states[new_closure]['name']
    
    return dfa_states

def minimize_dfa(dfa_states):
    if not dfa_states:
        return {}
    
    # Initial partition
    partitions = []
    final_states = set()
    non_final_states = set()
    
    for closure, state in dfa_states.items():
        if state['is_final']:
            final_states.add(frozenset([state['name']]))
        else:
            non_final_states.add(frozenset([state['name']]))
    
    if final_states:
        partitions.append(frozenset(final_states))
    if non_final_states:
        partitions.append(frozenset(non_final_states))
    
    # Refine partitions
    changed = True
    while changed:
        changed = False
        new_partitions = []
        
        for partition in partitions:
            if len(partition) == 1:
                new_partitions.append(partition)
                continue
            
            split_dict = defaultdict(list)
            for state_name_set in partition:
                state_name = next(iter(state_name_set))
                state = next(s for s in dfa_states.values() if s['name'] == state_name)
                
                key = tuple()
                symbols = sorted({sym for s in dfa_states.values() for sym in s['transitions']})
                for symbol in symbols:
                    target = state['transitions'].get(symbol, '')
                    if target:
                        for p_idx, p in enumerate(partitions):
                            if any(target in s for s in p):
                                key += (p_idx,)
                                break
                
                split_dict[key].append(state_name_set)
            
            if len(split_dict) > 1:
                changed = True
                for group in split_dict.values():
                    new_partitions.append(frozenset(group))
            else:
                new_partitions.append(partition)
        
        partitions = new_partitions
    
    # Create minimized DFA
    minimized_dfa = {}
    state_mapping = {}
    
    for i, partition in enumerate(partitions):
        representative = next(iter(next(iter(partition))))
        state_name = f'X{i+1}'
        for state_name_set in partition:
            for name in state_name_set:
                state_mapping[name] = state_name
        
        original_state = next(s for s in dfa_states.values() if s['name'] == representative)
        minimized_dfa[state_name] = {
            'name': state_name,
            'transitions': {},
            'is_final': original_state['is_final']
        }
    
    # Build transitions
    for state in minimized_dfa.values():
        original_name = next(k for k, v in state_mapping.items() if v == state['name'])
        original_state = next(s for s in dfa_states.values() if s['name'] == original_name)
        
        for symbol, target in original_state['transitions'].items():
            if target in state_mapping:
                state['transitions'][symbol] = state_mapping[target]
    
    return minimized_dfa

def create_output_table(dfa_states, symbols):
    output = [[''], ['']]
    
    # Sort states as X1, X2, X3, etc.
    sorted_states = sorted(dfa_states.values(), key=lambda x: int(x['name'][1:]))
    
    for state in sorted_states:
        output[0].append('F' if state['is_final'] else '')
        output[1].append(state['name'])
    
    for symbol in sorted(symbols):
        row = [symbol]
        for state in sorted_states:
            row.append(state['transitions'].get(symbol, ''))
        output.append(row)
    
    return output

def main():
    if len(sys.argv) != 3:
        print("Usage: python lab4.py <input_file> <output_file>")
        return
    
    try:
        input_table = read_table(sys.argv[1])
        nfa_states = parse_automaton(input_table)
        dfa_states = build_dfa(nfa_states)
        minimized_dfa = minimize_dfa(dfa_states)
        
        symbols = set()
        for row in input_table[2:]:
            if row and row[0].lower() not in ('ε', 'e'):
                symbols.add(row[0])
        
        output_table = create_output_table(minimized_dfa, symbols)
        write_table(sys.argv[2], output_table)
        print("Conversion completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()