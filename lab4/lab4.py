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
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if line.endswith(';'):
                line += " "
            items = line.split(';')
            items = [item.strip() if item.strip() != "" or i == 0 else "-" for i, item in enumerate(items)]
            input_table.append(items)
    return input_table

def write_table(output_file, output_table):
    with open(output_file, 'w', encoding='utf-8') as f:
        for row in output_table:
            f.write(";".join(row) + "\n")

def is_in_vector(all_states_vector, new_vector, ecloses):
    new_tuple = tuple(sorted(new_vector))
    return new_tuple in all_states_vector

def create_transitions(ecloses, input_table, line, column, output_state):
    if not output_state.transitions:
        for i in range(2, len(input_table) - 1):
            str_vector = []
            if input_table[i][column] == "-":
                output_state.transitions.append(str_vector)
                output_state.transitionsName.append("")
                continue

            items = input_table[i][column].split(',')
            output_state.transitionsName.append("")
            for item in items:
                item = item.strip()
                if item and item not in str_vector:
                    str_vector.append(item)
                    output_state.transitionsName[-1] += item
            output_state.transitions.append(str_vector)

def create_state(ecloses, input_table, line, column, output_state, visited=None):
    if visited is None:
        visited = set()
    
    new_state = input_table[line][column].strip()
    if not new_state or new_state == "-":
        return
    if new_state in output_state.arrOfStates:
        return
    
    state_key = (new_state, column)
    if state_key in visited:
        return
    visited.add(state_key)

    output_state.arrOfStates.append(new_state)
    output_state.name += new_state
    if new_state in ecloses and ecloses[new_state].fin:
        output_state.fin = True

    create_transitions(ecloses, input_table, line, column, output_state)

    if new_state not in ecloses or not ecloses[new_state].eStates:
        return

    for e_state in ecloses[new_state].eStates:
        if e_state in ecloses:
            create_state(ecloses, input_table, 1, ecloses[e_state].column, output_state, visited)

def create_all_states(ecloses, input_table):
    all_states = []
    all_states_vector = {}
    
    # Создаём начальное состояние
    initial_state = State()
    create_state(ecloses, input_table, 1, 1, initial_state)
    all_states.append(initial_state)
    all_states_vector[tuple(sorted(initial_state.arrOfStates))] = "S0"

    i = 0
    max_iterations = 100  # Защита от бесконечного цикла
    while i < len(all_states) and i < max_iterations:
        current_state = all_states[i]
        
        for j in range(len(current_state.transitions)):
            transition = current_state.transitions[j]
            if not transition:
                continue

            transition_tuple = tuple(sorted(transition))
            
            if transition_tuple not in all_states_vector:
                new_state = State()
                visited = set()
                for state in transition:
                    if state in ecloses:
                        column = ecloses[state].column
                        create_state(ecloses, input_table, 1, column, new_state, visited)

                if new_state.arrOfStates:  # Если состояние не пустое
                    state_name = "S" + str(len(all_states_vector))
                    all_states_vector[tuple(sorted(new_state.arrOfStates))] = state_name
                    all_states.append(new_state)

        i += 1

    return all_states, all_states_vector

def handle_machine(ecloses, input_table):
    output_table = []
    output_table.append([""])
    output_table.append([""])

    for i in range(2, len(input_table) - 1):
        output_table.append([input_table[i][0]])

    all_states, all_states_vector = create_all_states(ecloses, input_table)

    # Заполняем заголовки состояний
    for state in all_states:
        state_tuple = tuple(sorted(state.arrOfStates))
        output_table[1].append(all_states_vector[state_tuple])

    output_table[0] = [""] * len(output_table[1])

    # Заполняем переходы
    for state in all_states:
        state_tuple = tuple(sorted(state.arrOfStates))
        for i in range(2, len(output_table)):
            if not state.transitionsName[i - 2]:
                output_table[i].append("")
            else:
                transition_tuple = tuple(sorted(state.transitions[i - 2]))
                if transition_tuple in all_states_vector:
                    output_table[i].append(all_states_vector[transition_tuple])
                else:
                    output_table[i].append("")

    # Помечаем конечные состояния
    for state in all_states:
        if state.fin:
            state_tuple = tuple(sorted(state.arrOfStates))
            try:
                col_index = output_table[1].index(all_states_vector[state_tuple])
                output_table[0][col_index] = "F"
            except ValueError:
                pass

    return output_table

def create_ecloses(input_table):
    ecloses = {}
    e_str = -1
    
    # Находим строку с ε-переходами
    for i in range(len(input_table)):
        if input_table[i][0].strip().lower() in ("ε", "e"):
            e_str = i
            break

    if e_str == -1:
        print("Error: No ε-line found in the input table.")
        return None

    # Обрабатываем каждое состояние
    for i in range(1, len(input_table[1])):
        state_name = input_table[1][i].strip()
        if not state_name or state_name == "-":
            continue

        fin = (input_table[0][i].strip() == "F") if i < len(input_table[0]) else False
        eclose = Eclose()
        eclose.state = state_name
        eclose.column = i
        eclose.fin = fin

        # Обрабатываем ε-переходы
        if e_str < len(input_table) and i < len(input_table[e_str]):
            epsilon_transitions = input_table[e_str][i].strip()
            if epsilon_transitions and epsilon_transitions != "-":
                items = [x.strip() for x in epsilon_transitions.split(',') if x.strip()]
                eclose.eStates.extend(items)

        ecloses[eclose.state] = eclose

    return ecloses, e_str

def main():
    if len(sys.argv) != 3:
        print("Usage: python lab4.py <input_file> <output_file>")
        return

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        input_table = read_table(input_file)
    except Exception as e:
        print(f"Error opening input file: {e}")
        return

    ecloses = create_ecloses(input_table)
    if ecloses is None:
        return
    ecloses, e_str = ecloses

    output_table = handle_machine(ecloses, input_table)

    try:
        write_table(output_file, output_table)
        print("Successfully wrote output to", output_file)
    except Exception as e:
        print(f"Error writing to output file: {e}")
        return

if __name__ == "__main__":
    main()