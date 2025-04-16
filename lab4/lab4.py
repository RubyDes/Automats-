import sys
from collections import defaultdict, deque

class State:
    def __init__(self):
        self.transitions = defaultdict(list)
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
    
    # Проверяем наличие строки с epsilon-переходами (e или ε)
    epsilon_row = -1
    for i, row in enumerate(input_table):
        if row and row[0].lower() in ('ε', 'e'):
            epsilon_row = i
            break
    
    # Парсим состояния из заголовка
    if len(input_table) < 2:
        return states
    
    for col in range(1, len(input_table[1])):
        state_name = input_table[1][col].strip()
        if not state_name:
            continue
            
        state = State()
        state.is_final = (col < len(input_table[0])) and (input_table[0][col].strip() == 'F')
        states[state_name] = state
    
    # Парсим обычные переходы (заменяем пустые на "-")
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
            if not state_name or state_name not in states:
                continue
                
            targets = input_table[row][col].strip()
            if targets:
                states[state_name].transitions[symbol] = [s.strip() for s in targets.split(',') if s.strip()]
            else:
                states[state_name].transitions[symbol] = ['-']  # Заменяем пустой переход
    
    return states

def build_dfa(nfa_states):
    if not nfa_states:
        return {}
    
    # Начальное состояние - первое в списке
    initial_state = next(iter(nfa_states))
    
    dfa_states = {}
    state_queue = deque()
    
    # Создаем первое состояние DFA
    dfa_states[frozenset([initial_state])] = {
        'name': 'S0',
        'transitions': {},
        'is_final': nfa_states[initial_state].is_final
    }
    state_queue.append(frozenset([initial_state]))
    
    # Собираем все символы алфавита (исключая epsilon)
    symbols = set()
    for state in nfa_states.values():
        for symbol in state.transitions:
            if symbol.lower() not in ('ε', 'e'):
                symbols.add(symbol)
    
    # Обрабатываем все состояния
    while state_queue:
        current_states = state_queue.popleft()
        
        for symbol in symbols:
            # Вычисляем move по символу
            move = set()
            for state_name in current_states:
                for target in nfa_states[state_name].transitions.get(symbol, []):
                    if target != '-':  # Игнорируем пустые переходы
                        move.add(target)
            
            if not move:
                continue
                
            new_state = frozenset(move)
            
            # Если такого состояния еще нет, добавляем
            if new_state not in dfa_states:
                state_name = f'S{len(dfa_states)}'
                is_final = any(nfa_states[s].is_final for s in new_state)
                
                dfa_states[new_state] = {
                    'name': state_name,
                    'transitions': {},
                    'is_final': is_final
                }
                state_queue.append(new_state)
            
            # Добавляем переход
            dfa_states[current_states]['transitions'][symbol] = dfa_states[new_state]['name']
    
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