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
const string FINAL_STATE_KEY = "finalState";
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

class Grammar {
public:
    GrammarType Type = GrammarType::Undefined;
    string FinalState;
    unordered_map<string, map<string, vector<string>>> Productions;
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
        return str.substr(str.find_first_not_of(SPACE), str.find_last_not_of(SPACE) - str.find_first_not_of(SPACE) + 1);
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
        for (const auto& str : vector)
            if (regex_match(str, r))
                return true;
        return false;
    }
};

class Parser {
public:
    static vector<Pair> ReadGrammarFromFile(const string& filename) {
        ifstream input(filename);
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
            moves.push_back({ tempVector[0], Utils::SplitString(tempVector[1], PIPE) });
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
            for (size_t i = 1; i < moves.size(); i++)
                states[moves[i].key] = STATE_PREFIX + to_string(i);
            states[moves[0].key] = STATE_PREFIX + to_string(states.size());
        }
        else {
            for (size_t i = 0; i < moves.size(); i++)
                states[moves[i].key] = STATE_PREFIX + to_string(i);
            states[FINAL_STATE_KEY] = STATE_PREFIX + to_string(states.size());
        }

        return states;
    }
};

class TransitionTable {
public:
    static vector<Transition> BuildTransitionRules(const vector<Pair>& moves, const unordered_map<string, string>& states, bool isLeft) {
        vector<Transition> transitions;

        for (const auto& move : moves) {
            for (const auto& transition : move.value) {
                vector<string> splitTransition = Utils::SplitString(transition, SPACE);
                Transition transit;
                if (splitTransition.size() == 1) {
                    transit.arg = splitTransition[0];
                    if (isLeft) {
                        transit.from = states.at(FINAL_STATE_KEY);
                        transit.to = states.at(move.key);
                    }
                    else {
                        transit.from = states.at(move.key);
                        transit.to = states.at(FINAL_STATE_KEY);
                    }
                }
                else {
                    if (isLeft) {
                        transit.from = states.at(splitTransition[0]);
                        transit.to = states.at(move.key);
                        transit.arg = splitTransition[1];
                    }
                    else {
                        transit.from = states.at(move.key);
                        transit.to = states.at(splitTransition[1]);
                        transit.arg = splitTransition[0];
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
        list<string> tempList;

        for (const auto& s : states)
            tempList.push_back(s.second);
        tempList.sort();
        output << CSV_HEADER_F << NEWLINE;

        output << CSV_DELIMITER;
        for (const auto& s : tempList)
            output << s << CSV_DELIMITER;
        output << NEWLINE;

        for (const auto& arg : ExtractUniqueSymbols(transitions)) {
            output << arg << CSV_DELIMITER;
            for (const auto& from : tempList) {
                string temp;
                for (const auto& trans : transitions) {
                    if (trans.from == from && trans.arg == arg)
                        temp += trans.to + COMMA;
                }
                if (!temp.empty())
                    temp = temp.substr(0, temp.size() - 1);
                output << temp << CSV_DELIMITER;
            }
            output << NEWLINE;
        }
    }

private:
    static list<string> ExtractUniqueSymbols(const vector<Transition>& transitions) {
        list<string> args;
        for (const auto& trans : transitions)
            args.push_back(trans.arg);
        args.sort();
        args.unique();
        return args;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 3) {
        cout << USAGE_MESSAGE << endl;
        return 1;
    }

    vector<Pair> moves = Parser::ReadGrammarFromFile(argv[1]);
    bool isLeft = Utils::ContainsComplexGrammarRule(moves[0].value);
    unordered_map<string, string> states = StateMapper::AssignStateLabels(moves, isLeft);
    vector<Transition> transitions = TransitionTable::BuildTransitionRules(moves, states, isLeft);

    FileHandler::ExportTransitionTableToCSV(argv[2], states, transitions);

    return 0;
}