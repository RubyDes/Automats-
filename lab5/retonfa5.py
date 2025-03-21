import re
import sys
import csv

class State:
    def __init__(self, name, is_final=False):
        self.name = name
        self.is_final = is_final
        self.transitions = {}

    def add_transition(self, symbol, state):
        if symbol not in self.transitions:
            self.transitions[symbol] = []
        self.transitions[symbol].append(state)

class NFA:
    def __init__(self, start_state, accept_state):
        self.start_state = start_state
        self.accept_state = accept_state

    def get_states(self):
        states = set()
        stack = [self.start_state]
        while stack:
            state = stack.pop()
            if state not in states:
                states.add(state)
                for symbol, next_states in state.transitions.items():
                    for next_state in next_states:
                        stack.append(next_state)
        return states

def regex_to_nfa(regex):
    stack = []
    state_counter = 0

    for char in regex:
        if char == '(':
            stack.append(char)
        elif char == ')':
            # Обработка закрывающей скобки
            nfa = None
            while stack[-1] != '(':
                nfa = stack.pop()
            stack.pop()  # Удаляем '('
            stack.append(nfa)
        elif char == '|':
            stack.append(char)
        elif char == '*':
            nfa = stack.pop()
            new_start = State(f'S{state_counter}')
            state_counter += 1
            new_accept = State(f'S{state_counter}', is_final=True)
            state_counter += 1

            new_start.add_transition('ε', nfa.start_state)
            new_start.add_transition('ε', new_accept)
            nfa.accept_state.add_transition('ε', nfa.start_state)
            nfa.accept_state.add_transition('ε', new_accept)
            nfa.accept_state.is_final = False

            stack.append(NFA(new_start, new_accept))
        elif char == '+':
            nfa = stack.pop()
            new_start = State(f'S{state_counter}')
            state_counter += 1
            new_accept = State(f'S{state_counter}', is_final=True)
            state_counter += 1

            new_start.add_transition('ε', nfa.start_state)
            nfa.accept_state.add_transition('ε', nfa.start_state)
            nfa.accept_state.add_transition('ε', new_accept)
            nfa.accept_state.is_final = False

            stack.append(NFA(new_start, new_accept))
        else:
            start = State(f'S{state_counter}')
            state_counter += 1
            accept = State(f'S{state_counter}', is_final=True)
            state_counter += 1
            start.add_transition(char, accept)
            stack.append(NFA(start, accept))

    # Объединение всех NFA в стеке
    while len(stack) > 1:
        nfa2 = stack.pop()
        op = stack.pop()
        nfa1 = stack.pop()

        if op == '|':
            new_start = State(f'S{state_counter}')
            state_counter += 1
            new_accept = State(f'S{state_counter}', is_final=True)
            state_counter += 1

            new_start.add_transition('ε', nfa1.start_state)
            new_start.add_transition('ε', nfa2.start_state)
            nfa1.accept_state.add_transition('ε', new_accept)
            nfa2.accept_state.add_transition('ε', new_accept)
            nfa1.accept_state.is_final = False
            nfa2.accept_state.is_final = False

            stack.append(NFA(new_start, new_accept))
        else:
            raise ValueError("Invalid operator")

    return stack[0]

def save_nfa_to_csv(nfa, filename):
    states = nfa.get_states()
    transitions = []

    for state in states:
        for symbol, next_states in state.transitions.items():
            for next_state in next_states:
                transitions.append((state.name, symbol, next_state.name))

    # Указываем кодировку utf-8 при открытии файла
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['From', 'Symbol', 'To'])
        for transition in transitions:
            writer.writerow(transition)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python regexToNFA.py <output.csv> <regex>")
        sys.exit(1)

    output_file = sys.argv[1]
    regex = sys.argv[2]

    nfa = regex_to_nfa(regex)
    save_nfa_to_csv(nfa, output_file)
    print(f"NFA saved to {output_file}")