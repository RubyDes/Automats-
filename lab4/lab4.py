import sys
from collections import defaultdict

class Eclose:
    def __init__(self):
        self.state = ""
        self.eStates = []
        self.fin = False
        self.column = 0

class State:
    def __init__(self):
        self.name = ""
        self.transitionsName = []
        self.arrOfStates = []
        self.fin = False
        self.transitions = []

def read_table(input_file):
    input_table = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.endswith(';'):
                line += " "
            items = line.split(';')
            items = [item.strip() if item.strip() != "" or i == 0 else "" for i, item in enumerate(items)]
            input_table.append(items)
    return input_table

def write_table(output_file, output_table):
    with open(output_file, 'w', encoding='utf-8') as f:
        for row in output_table:
            f.write(";".join(row) + "\n")

def is_in_vector(all_states_vector, new_vector, ecloses, name):
    if not all_states_vector:
        return False

    temp_vector = new_vector.copy()
    i = 0
    while i < len(temp_vector):
        if temp_vector[i] == "":
            del temp_vector[i]
            continue
        if temp_vector[i] not in ecloses:
            i += 1
            continue
        for e_state in ecloses[temp_vector[i]].eStates:
            if e_state not in temp_vector:
                temp_vector.append(e_state)
                name += e_state
        i += 1

    for states, state_name in all_states_vector.items():
        if set(states) == set(temp_vector):
            new_vector.clear()
            new_vector.extend(temp_vector)
            return True

    return False

def create_transitions(ecloses, input_table, output_table, e_str, line, column, output_state):
    if not output_state.transitions:
        for _ in range(len(input_table)-2):
            output_state.transitions.append([])
            output_state.transitionsName.append("")

    for i in range(2, len(input_table)):
        symbol = input_table[i][0]
        target = input_table[i][column]
        
        if target == "":
            continue
            
        items = target.split(',')
        for item in items:
            if item not in output_state.transitions[i-2]:
                output_state.transitions[i-2].append(item)
                output_state.transitionsName[i-2] += item

def create_state(ecloses, input_table, output_table, e_str, line, column, output_state):
    new_state = input_table[line][column]
    if new_state in output_state.arrOfStates or new_state == "":
        return
        
    output_state.arrOfStates.append(new_state)
    output_state.name += new_state
    
    if ecloses[new_state].fin:
        output_state.fin = True

    create_transitions(ecloses, input_table, output_table, e_str, line, column, output_state)

    for e_state in ecloses[new_state].eStates:
        if e_state not in output_state.arrOfStates:
            create_state(ecloses, input_table, output_table, e_str, 1, ecloses[e_state].column, output_state)

def create_all_states(ecloses, input_table, output_table, e_str, all_states, all_states_vector):
    initial_state = State()
    create_state(ecloses, input_table, output_table, e_str, 1, 1, initial_state)
    all_states.append(initial_state)
    all_states_vector[tuple(sorted(initial_state.arrOfStates))] = "S0"

    i = 0
    while i < len(all_states):
        current_state = all_states[i]
        
        for j in range(len(current_state.transitions)):
            new_vector = current_state.transitions[j].copy()
            name = current_state.transitionsName[j]
            
            if not new_vector:
                continue
                
            temp_vector = new_vector.copy()
            for state in new_vector:
                if state in ecloses:
                    for e_state in ecloses[state].eStates:
                        if e_state not in temp_vector:
                            temp_vector.append(e_state)
            
            found = False
            for states, state_name in all_states_vector.items():
                if set(states) == set(temp_vector):
                    current_state.transitionsName[j] = state_name
                    found = True
                    break
                    
            if not found and temp_vector:
                new_state = State()
                for state in temp_vector:
                    create_state(ecloses, input_table, output_table, e_str, 1, ecloses[state].column, new_state)
                
                state_key = tuple(sorted(new_state.arrOfStates))
                if state_key not in all_states_vector:
                    new_state_name = f"S{len(all_states_vector)}"
                    all_states_vector[state_key] = new_state_name
                    all_states.append(new_state)
                    current_state.transitionsName[j] = new_state_name
        i += 1

def handle_machine(ecloses, input_table, output_table, e_str):
    output_table.append([""])
    output_table.append([""])
    
    for i in range(2, len(input_table)):
        output_table.append([input_table[i][0]])

    all_states = []
    all_states_vector = {}
    create_all_states(ecloses, input_table, output_table, e_str, all_states, all_states_vector)

    for state_key, state_name in sorted(all_states_vector.items(), key=lambda x: x[1]):
        output_table[1].append(state_name)
        if any(s in ecloses and ecloses[s].fin for s in state_key):
            output_table[0].append("F")
        else:
            output_table[0].append("")

    for state_key, state_name in sorted(all_states_vector.items(), key=lambda x: x[1]):
        state = next(s for s in all_states if tuple(sorted(s.arrOfStates)) == state_key)
        
        for i in range(2, len(output_table)):
            if i-2 < len(state.transitionsName) and state.transitionsName[i-2]:
                output_table[i].append(state.transitionsName[i-2])
            else:
                output_table[i].append("")

def create_ecloses(ecloses, input_table):
    e_str = -1
    for i in range(len(input_table)):
        if input_table[i][0].lower() in ("e", "ε"):
            e_str = i
            break
    
    # Если нет ε-переходов, создаем пустые ε-замыкания
    if e_str == -1:
        for col in range(1, len(input_table[1])):
            state_name = input_table[1][col]
            if state_name == "":
                continue
                
            eclose = Eclose()
            eclose.state = state_name
            eclose.column = col
            eclose.fin = (input_table[0][col] == "F")
            ecloses[eclose.state] = eclose
        return True

    for col in range(1, len(input_table[1])):
        state_name = input_table[1][col]
        if state_name == "":
            continue
            
        eclose = Eclose()
        eclose.state = state_name
        eclose.column = col
        eclose.fin = (input_table[0][col] == "F")

        if input_table[e_str][col] not in ["", "-"]:
            items = input_table[e_str][col].split(',')
            eclose.eStates.extend([item.strip() for item in items if item.strip()])

        ecloses[eclose.state] = eclose

    return True

def main():
    if len(sys.argv) != 3:
        print("Usage: python lab4.py <input_file> <output_file>")
        return

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        input_table = read_table(input_file)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    ecloses = {}
    if not create_ecloses(ecloses, input_table):
        print("Warning: No ε-transitions found, processing as regular NFA")

    output_table = []
    handle_machine(ecloses, input_table, output_table, -1)

    try:
        write_table(output_file, output_table)
    except Exception as e:
        print(f"Error writing output file: {e}")
        return

if __name__ == "__main__":
    main()