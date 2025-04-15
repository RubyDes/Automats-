import sys
from collections import defaultdict, deque

class State:
    def __init__(self):
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
    states = {}
    epsilon_row = -1
    
    # Находим строку с epsilon-переходами
    for i, row in enumerate(input_table):
        if row and row[0].lower() in ('ε', 'e'):
            epsilon_row = i
            break
    
    # Парсим заголовок с именами состояний
    if len(input_table) < 2:
        return states
    
    for col in range(1, len(input_table[1])):
        state_name = input_table[1][col].strip()
        if not state_name:
            continue
            
        state = State()
        state.is_final = (col < len(input_table[0]) and (input_table[0][col].strip() == 'F'))
        
        # Парсим epsilon-переходы если есть
        if epsilon_row != -1 and col < len(input_table[epsilon_row]):
            epsilons = input_table[epsilon_row][col].strip()
            if epsilons:
                state.epsilon = [s.strip() for s in epsilons.split(',') if s.strip()]
        
        states[state_name] = state
    
    # Парсим обычные переходы
    for row in range(2, len(input_table)):
        if not input_table[row] or row == epsilon_row:
            continue
            
        symbol = input_table[row][0].strip()
        if not symbol:
            continue
            
        for col in range(1, len(input_table[row])):
            if col >= len(input_table[1]):
                continue
                
            state_name = input_table[1][col].strip()
            if not state_name:
                continue
                
            targets = input_table[row][col].strip()
            if targets:
                states[state_name].transitions[symbol] = [s.strip() for s in targets.split(',') if s.strip()]
    
    return states

def epsilon_closure(states, state_set):
    closure = set(state_set)
    queue = deque(state_set)
    
    while queue:
        current = queue.popleft()
        for neighbor in states[current].epsilon:
            if neighbor not in closure:
                closure.add(neighbor)
                queue.append(neighbor)
    
    return frozenset(closure)

def build_dfa(nfa_states):
    if not nfa_states:
        return {}
    
    # Находим начальное состояние (первое в списке)
    initial_state = next(iter(nfa_states))
    initial_closure = epsilon_closure(nfa_states, {initial_state})
    
    dfa_states = {}
    state_queue = deque()
    
    # Создаем первое состояние DFA
    dfa_states[initial_closure] = {
        'name': 'S0',
        'transitions': {},
        'is_final': any(nfa_states[s].is_final for s in initial_closure)
    }
    state_queue.append(initial_closure)
    
    # Собираем все символы алфавита
    symbols = set()
    for state in nfa_states.values():
        symbols.update(state.transitions.keys())
    
    # Обрабатываем все состояния
    while state_queue:
        current_closure = state_queue.popleft()
        
        for symbol in symbols:
            # Вычисляем move по символу
            move = set()
            for state in current_closure:
                move.update(nfa_states[state].transitions.get(symbol, []))
            
            if not move:
                continue
                
            # Вычисляем epsilon-замыкание
            new_closure = epsilon_closure(nfa_states, move)
            
            # Если такого состояния еще нет, добавляем
            if new_closure not in dfa_states:
                state_name = f'S{len(dfa_states)}'
                dfa_states[new_closure] = {
                    'name': state_name,
                    'transitions': {},
                    'is_final': any(nfa_states[s].is_final for s in new_closure)
                }
                state_queue.append(new_closure)
            
            # Добавляем переход
            dfa_states[current_closure]['transitions'][symbol] = dfa_states[new_closure]['name']
    
    return dfa_states

def create_output_table(dfa_states, symbols):
    output = [[''], ['']]
    
    # Заголовок с именами состояний
    for state in dfa_states.values():
        output[0].append('F' if state['is_final'] else '')
        output[1].append(state['name'])
    
    # Добавляем переходы для каждого символа
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
        input_table = read_table(sys.argv[1])
        nfa_states = parse_automaton(input_table)
        dfa_states = build_dfa(nfa_states)
        
        if not dfa_states:
            print("Error: No valid states found in input")
            return
        
        symbols = set()
        for row in input_table[2:]:
            if row and row[0].lower() not in ('ε', 'e'):
                symbols.add(row[0])
        
        output_table = create_output_table(dfa_states, symbols)
        write_table(sys.argv[2], output_table)
        print("Conversion completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()