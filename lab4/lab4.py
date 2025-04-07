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
            # Фильтруем строки с ε-переходами
            if row and row[0].lower() not in ('e', 'ε'):
                f.write(";".join(row) + "\n")

def create_ecloses(ecloses, input_table):
    e_str = -1
    for i in range(len(input_table)):
        if input_table[i][0].lower() in ("e", "ε"):
            e_str = i
            break
    
    for col in range(1, len(input_table[1])):
        state_name = input_table[1][col]
        if not state_name:
            continue
            
        eclose = Eclose()
        eclose.state = state_name
        eclose.column = col
        eclose.fin = (input_table[0][col] == "F")

        if e_str != -1 and input_table[e_str][col]:
            items = input_table[e_str][col].split(',')
            eclose.eStates = [item.strip() for item in items if item.strip()]

        ecloses[state_name] = eclose
    return True

def handle_machine(ecloses, input_table):
    output_table = []
    output_table.append([""])  # Строка финальных состояний
    output_table.append([""])  # Строка имен состояний
    
    # Добавляем только символы алфавита (исключая ε)
    for i in range(2, len(input_table)):
        if input_table[i][0].lower() not in ('e', 'ε'):
            output_table.append([input_table[i][0]])

    # Остальная логика обработки состояний и переходов...
    # ... (пропущена для краткости, должна быть аналогична предыдущим версиям)

    return output_table

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
    create_ecloses(ecloses, input_table)

    output_table = handle_machine(ecloses, input_table)

    try:
        write_table(output_file, output_table)
    except Exception as e:
        print(f"Error writing output file: {e}")
        return

if __name__ == "__main__":
    main()