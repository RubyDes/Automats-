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

    with open(input_file, 'r') as f:

        for line in f:

            line = line.strip()

            if line.endswith(';'):

                line += " "

            items = line.split(';')

            items = [item.strip() if item.strip() != "" or i == 0 else "-" for i, item in enumerate(items)]

            input_table.append(items)

    return input_table



def write_table(output_file, output_table):

    with open(output_file, 'w') as f:

        for row in output_table:

            f.write(";".join(row) + "\n")



def is_in_vector(all_states_vector, new_vector, ecloses, name):

    if not all_states_vector:

        return False



    i = 0

    while i < len(new_vector):

        if new_vector[i] == "-":

            del new_vector[i]

            continue

        if new_vector[i] not in ecloses:

            i += 1

            continue

        for e_state in ecloses[new_vector[i]].eStates:

            if e_state not in new_vector:

                new_vector.append(e_state)

                name += e_state

        i += 1



    for states, state_name in all_states_vector.items():

        if len(states) == len(new_vector) and sorted(states) == sorted(new_vector):

            new_vector.clear()

            new_vector.extend(states)

            return True



    return False



def create_transitions(ecloses, input_table, output_table, e_str, line, column, output_state):

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

                if item not in str_vector:

                    str_vector.append(item)

                    output_state.transitionsName[-1] += item

            output_state.transitions.append(str_vector)

    else:

        for i in range(2, len(input_table) - 1):

            if input_table[i][column] == "-":

                continue

            items = input_table[i][column].split(',')

            for item in items:

                if item not in output_state.transitions[i - 2]:

                    output_state.transitions[i - 2].append(item)

                    output_state.transitionsName[i - 2] += item



def create_state(ecloses, input_table, output_table, e_str, line, column, output_state):

    new_state = input_table[line][column]

    if new_state in output_state.arrOfStates:

        return

    output_state.arrOfStates.append(new_state)

    output_state.name += new_state

    if ecloses[new_state].fin:

        output_state.fin = True



    create_transitions(ecloses, input_table, output_table, e_str, line, column, output_state)



    if not ecloses[new_state].eStates:

        return



    for e_state in ecloses[new_state].eStates:

        create_state(ecloses, input_table, output_table, e_str, 1, ecloses[e_state].column, output_state)



def create_all_states(ecloses, input_table, output_table, e_str, all_states, all_states_vector):

    output_state = State()

    output_state.fin = False

    create_state(ecloses, input_table, output_table, e_str, 1, 1, output_state)

    all_states.append(output_state)

    all_states_vector[tuple(output_state.arrOfStates)] = "S" + str(len(all_states_vector))



    i = 0

    while i < len(all_states):

        for j in range(len(all_states[i].transitions)):

            new_vector = all_states[i].transitions[j].copy()

            name = all_states[i].transitionsName[j]

            if not is_in_vector(all_states_vector, new_vector, ecloses, name) and new_vector:

                new_state = State()

                new_state.fin = False



                for state in new_vector:

                    column = ecloses[state].column

                    create_state(ecloses, input_table, output_table, e_str, 1, column, new_state)



                all_states_vector[tuple(new_state.arrOfStates)] = "S" + str(len(all_states_vector))

                all_states.append(new_state)

        i += 1



    for states, name in all_states_vector.items():

        print(" ".join(states), "-", name)



def handle_machine(ecloses, input_table, output_table, e_str):

    output_table.append([""])

    output_table.append([""])



    for i in range(2, len(input_table) - 1):

        output_table.append([input_table[i][0]])



    all_states = []

    all_states_vector = {}

    create_all_states(ecloses, input_table, output_table, e_str, all_states, all_states_vector)



    for state in all_states:

        output_table[1].append(all_states_vector[tuple(state.arrOfStates)])



    output_table[0] = [""] * len(output_table[1])



    for state in all_states:

        for i in range(2, len(output_table)):

            if not state.transitionsName[i - 2]:

                output_table[i].append("")

            else:

                output_table[i].append(all_states_vector[tuple(state.transitions[i - 2])])



    is_f_added = False

    for state in all_states:

        if state.fin and not is_f_added:

            try:

                col_index = output_table[1].index(all_states_vector[tuple(state.arrOfStates)])

                if col_index == len(output_table[0]) - 1:

                    output_table[0][col_index] = "F"

                    is_f_added = True

            except ValueError:

                pass



def create_ecloses(ecloses, input_table, e_str):

    if input_table[-1][0] == "e":

        e_str = len(input_table) - 1

    else:

        return False



    for i in range(1, len(input_table[1])):

        fin = input_table[0][i] == "F"

        eclose = Eclose()

        eclose.state = input_table[1][i]

        eclose.column = i

        eclose.fin = fin



        if input_table[e_str][i] not in ["", "-"]:

            items = input_table[e_str][i].split(',')

            eclose.eStates.extend(items)



        ecloses[eclose.state] = eclose



    return True



def main():

    if len(sys.argv) != 3:

        print("Invalid input format")

        return



    input_file = sys.argv[1]

    output_file = sys.argv[2]



    try:

        input_table = read_table(input_file)

    except:

        print("Error opening input file")

        return



    ecloses = {}

    e_str = 0

    if not create_ecloses(ecloses, input_table, e_str):

        print("Error file format. There isn't empty symbols!")

        return



    output_table = []

    handle_machine(ecloses, input_table, output_table, e_str)



    try:

        write_table(output_file, output_table)

    except:

        print("Error writing to output file")

        return



if __name__ == "__main__":

    main()