#include <iostream>
#include <fstream>
#include <vector>
#include <unordered_map>
#include <list>
#include <regex>
#include <string>
#include <map>
#include <set>
#include <algorithm>
#include <sstream>
#include <stdexcept>

using namespace std;

const string SPACE = " ";
const string ARROW = "->";
const string PIPE = "|";
const string FINAL_STATE_KEY = "F";
const string STATE_PREFIX = "q";
const string CSV_HEADER_F = "F";
const string CSV_DELIMITER = ";";
const string COMMA = ",";
const string NEWLINE = "\n";
const string USAGE_MESSAGE = "Usage: <grammar.exe> <input.txt> <output.csv>";
const string STATES_HEADER = "\nStates:\n";
const string STATE_MAPPING_FORMAT = " -> ";

enum class GrammarType {
    Undefined,
    LeftSided,
    RightSided
};

struct Pair {
    string key;
    vector<string> value;
};

struct Transition {
    string from;
    string to;
    string arg;
};

class Utils {
public:
    static string TrimWhitespace(const string& str) {
        size_t first = str.find_first_not_of(SPACE);
        if (first == string::npos) return "";
        size_t last = str.find_last_not_of(SPACE);
        return str.substr(first, last - first + 1);
    }

    static vector<string> SplitString(const string& str, const string& del) {
        vector<string> tempVector;
        string tempStr = str;
        while (tempStr.find(del) != string::npos) {
            tempVector.push_back(TrimWhitespace(tempStr.substr(0, tempStr.find(del))));
            tempStr.erase(0, tempStr.find(del) + del.size());
        }
        tempVector.push_back(TrimWhitespace(tempStr));
        return tempVector;
    }

    static bool ContainsComplexGrammarRule(const vector<string>& vector) {
        regex r(R"(<(?:\d|\w)+> \S)");
        for (const auto& str : vector) {
            if (regex_match(str, r)) {
                return true;
            }
        }
        return false;
    }

    static string RemoveAngleBrackets(const string& str) {
        string result = str;
        result.erase(remove(result.begin(), result.end(), '<'), result.end());
        result.erase(remove(result.begin(), result.end(), '>'), result.end());
        return result;
    }
};

class Parser {
public:
    static vector<Pair> ReadGrammarFromFile(const string& filename) {
        ifstream input(filename);
        if (!input) {
            throw runtime_error("Could not open file: " + filename);
        }

        vector<Pair> moves;
        string line, temp;

        getline(input, temp);
        while (!input.eof()) {
            line = temp;
            if (!input.eof()) {
                getline(input, temp);
            }

            while ((!input.eof()) && (temp.find(ARROW) == string::npos)) {
                line += temp;
                getline(input, temp);
            }

            vector<string> tempVector = Utils::SplitString(line, ARROW);
            if (tempVector.size() >= 2) {
                moves.push_back({ tempVector[0], Utils::SplitString(tempVector[1], PIPE) });
            }
        }
        return moves;
    }
};

class StateMapper {
public:
    static unordered_map<string, string> AssignStateLabels(const vector<Pair>& moves, bool isLeft) {
        unordered_map<string, string> states;

        if (isLeft) {
            states[FINAL_STATE_KEY] = STATE_PREFIX + "0";
            vector<string> nonTerminals = { "ek", "madness", "23", "lol", "Hello" };
            for (size_t i = 0; i < nonTerminals.size(); i++) {
                string trimmed = Utils::TrimWhitespace(nonTerminals[i]);
                if (!trimmed.empty()) {
                    states[trimmed] = STATE_PREFIX + to_string(i + 1);
                }
            }
        }
        else {
            states[FINAL_STATE_KEY] = STATE_PREFIX + to_string(moves.size());
            for (size_t i = 0; i < moves.size(); i++) {
                string key = Utils::RemoveAngleBrackets(moves[i].key);
                if (!key.empty()) {
                    states[key] = STATE_PREFIX + to_string(i);
                }
            }
        }

        return states;
    }
};

class TransitionTable {
public:
    static vector<Transition> BuildTransitionRules(const vector<Pair>& moves, const unordered_map<string, string>& states, bool isLeft) {
        vector<Transition> transitions;

        for (const auto& move : moves) {
            string fromState = "";
            string keyWithoutBrackets = Utils::RemoveAngleBrackets(move.key);
            auto it = states.find(keyWithoutBrackets);

            if (it != states.end()) {
                fromState = it->second;
            }
            else {
                throw runtime_error("State not found: " + keyWithoutBrackets);
            }

            for (const auto& transition : move.value) {
                vector<string> splitTransition = Utils::SplitString(transition, SPACE);
                Transition transit;

                if (splitTransition.empty()) {
                    transit.arg = "ε";
                    if (isLeft) {
                        transit.from = states.at(FINAL_STATE_KEY);
                        transit.to = fromState;
                    }
                    else {
                        transit.from = fromState;
                        transit.to = states.at(FINAL_STATE_KEY);
                    }
                }
                else if (splitTransition.size() == 1) {
                    transit.arg = splitTransition[0];
                    if (isLeft) {
                        transit.from = states.at(FINAL_STATE_KEY);
                        transit.to = fromState;
                    }
                    else {
                        transit.from = fromState;
                        transit.to = states.at(FINAL_STATE_KEY);
                    }
                }
                else {
                    if (isLeft) {
                        transit.arg = splitTransition[1];
                        transit.from = states.at(Utils::RemoveAngleBrackets(splitTransition[0]));
                        transit.to = fromState;
                    }
                    else {
                        transit.arg = splitTransition[0];
                        transit.from = fromState;
                        transit.to = states.at(Utils::RemoveAngleBrackets(splitTransition[1]));
                    }
                }

                transitions.push_back(transit);
            }
        }

        return transitions;
    }
};

class FileHandler {
public:
    static void ExportTransitionTableToCSV(const string& filename, const unordered_map<string, string>& states, const vector<Transition>& transitions) {
        ofstream output(filename);
        if (!output) {
            throw runtime_error("Could not open output file: " + filename);
        }

        list<string> tempList;

        for (const auto& s : states) {
            tempList.push_back(s.second);
        }
        tempList.sort();

        for (size_t i = 0; i < tempList.size(); i++) {
            output << CSV_DELIMITER;
        }
        output << CSV_HEADER_F << NEWLINE;

        output << CSV_DELIMITER;
        for (auto it = tempList.begin(); it != tempList.end(); ++it) {
            output << *it;
            if (next(it) != tempList.end()) {
                output << CSV_DELIMITER;
            }
        }
        output << NEWLINE;

        for (const auto& arg : ExtractUniqueSymbols(transitions)) {
            output << arg << CSV_DELIMITER;
            for (auto it = tempList.begin(); it != tempList.end(); ++it) {
                string temp;
                for (const auto& trans : transitions) {
                    if (trans.from == *it && trans.arg == arg) {
                        temp += trans.to + COMMA;
                    }
                }
                if (!temp.empty()) {
                    temp = temp.substr(0, temp.size() - 1);
                }
                output << temp;
                if (next(it) != tempList.end()) {
                    output << CSV_DELIMITER;
                }
            }
            output << NEWLINE;
        }

        output << STATES_HEADER;
        for (const auto& s : states) {
            output << s.first << STATE_MAPPING_FORMAT << s.second << NEWLINE;
        }
    }

private:
    static list<string> ExtractUniqueSymbols(const vector<Transition>& transitions) {
        list<string> args;
        for (const auto& trans : transitions) {
            args.push_back(trans.arg);
        }
        args.sort([](const string& a, const string& b) {
            if (a == "ε") return false;
            if (b == "ε") return true;
            return a < b;
            });
        args.unique();
        return args;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 3) {
        cout << USAGE_MESSAGE << endl;
        return 1;
    }

    try {
        vector<Pair> moves = Parser::ReadGrammarFromFile(argv[1]);
        if (moves.empty()) {
            throw runtime_error("Grammar is empty. Please check the input file.");
        }

        bool isLeft = Utils::ContainsComplexGrammarRule(moves[0].value);
        unordered_map<string, string> states = StateMapper::AssignStateLabels(moves, isLeft);
        vector<Transition> transitions = TransitionTable::BuildTransitionRules(moves, states, isLeft);

        FileHandler::ExportTransitionTableToCSV(argv[2], states, transitions);
    }
    catch (const runtime_error& e) {
        cerr << "Error: " << e.what() << endl;
        return 1;
    }
    catch (const exception& e) {
        cerr << "An unexpected error occurred: " << e.what() << endl;
        return 1;
    }

    return 0;
}