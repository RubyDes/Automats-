#include <map>
#include <algorithm>
#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>

using namespace std;

struct Eclose {
    string state;
    vector<string> eStates;
    bool fin;
    int column;
};

struct State {
    string name;
    vector<string> transitionsName;
    vector<string> arrOfStates;
    bool fin;
    vector<vector<string>> transitions;
};

void ReadTable(ifstream& input, vector<vector<string>>& inputTable) {
    string str;
    int indexStr = 0;
    while (getline(input, str)) {
        indexStr += 1;
        vector<string> arr;
        std::string item;
        if (str[str.size() - 1] == ';') 
            str = str + " ";
        std::istringstream strStream(str);
        while (getline(strStream, item, ';')) {
            if (item == "" || item == " " && indexStr != 1)
                item = "-";
            arr.push_back(item);
        }
        inputTable.push_back(arr);
    }
}

void WriteTable(ofstream& output, vector<vector<string>>& outputTable) {
    for (auto i = 0; i < outputTable.size(); i++) {
        for (auto j = 0; j < outputTable[i].size(); j++) {
            output << outputTable[i][j];
            if (j + 1 != outputTable[i].size())
                output << ";";
        }
        output << "\n";
    }
}

bool IsInVector(map<vector<string>, string>& allStatesVector, vector<string>& newVector, map<string, Eclose>& ecloses, string& name) {
    if (allStatesVector.empty())
        return false;

    for (auto i = 0; i < newVector.size(); i++) {
        if (newVector[i] == "-") {
            newVector.erase(newVector.begin() + i + 1);
            i -= 1;
            continue;
        }
        if (ecloses.find(newVector[i]) == ecloses.end())
            continue;
        for (auto j = 0; j < ecloses[newVector[i]].eStates.size(); j++)
            if (std::find(newVector.begin(), newVector.end(), ecloses[newVector[i]].eStates[j]) == newVector.end()) {
                newVector.push_back(ecloses[newVector[i]].eStates[j]);
                name = name + ecloses[newVector[i]].eStates[j];
            }
    }

    for (auto& item : allStatesVector)
        if (item.first.size() == newVector.size() && is_permutation(item.first.begin(), item.first.end(), newVector.begin())) {
            newVector.clear();
            newVector = item.first;
            return true;
        }

    return false;
}

void CreateTransitions(map<string, Eclose>& ecloses, vector<vector<string>>& inputTable,
    vector<vector<string>>& outputTable, int eStr, int line, int column, State& outputState) {
    if (outputState.transitions.empty())
        for (auto i = 2; i < inputTable.size() - 1; i++) {
            vector<string> strVector;
            if (inputTable[i][column] == "-") {
                outputState.transitions.push_back(strVector);
                outputState.transitionsName.push_back("");
                continue;
            }

            string item;
            istringstream strStream(inputTable[i][column]);
            outputState.transitionsName.push_back("");

            while (getline(strStream, item, ','))
                if ((find(strVector.begin(), strVector.end(), item) == strVector.end())) {
                    strVector.push_back(item);
                    outputState.transitionsName[i - 2] = outputState.transitionsName[i - 2] + item;
                }
            outputState.transitions.push_back(strVector);
        }
    else
        for (auto i = 2; i < inputTable.size() - 1; i++) {
            if (inputTable[i][column] == "-")
                continue;
            string item;
            istringstream strStream(inputTable[i][column]);
            while (getline(strStream, item, ','))
                if ((find(outputState.transitions[i - 2].begin(), outputState.transitions[i - 2].end(), item) == outputState.transitions[i - 2].end())) {
                    outputState.transitions[i - 2].push_back(item);
                    outputState.transitionsName[i - 2] = outputState.transitionsName[i - 2] + item;
                }
        }
}

void CreateState(map<string, Eclose>& ecloses, vector<vector<string>>& inputTable,
    vector<vector<string>>& outputTable, int eStr, int line, int column, State& outputState) {
    string newState = inputTable[line][column];
    if (std::count(outputState.arrOfStates.begin(), outputState.arrOfStates.end(), newState))
        return;
    outputState.arrOfStates.push_back(newState);
    outputState.name = outputState.name + newState;
    if (ecloses[newState].fin)
        outputState.fin = true;

    CreateTransitions(ecloses, inputTable, outputTable, eStr, line, column, outputState);

    if (ecloses[newState].eStates.empty())
        return;

    for (auto i = 0; i < ecloses[newState].eStates.size(); i++)
        CreateState(ecloses, inputTable, outputTable, eStr, 1, ecloses[ecloses[newState].eStates[i]].column, outputState);

    return;
}

void CreateAllStates(map<string, Eclose>& ecloses, vector<vector<string>>& inputTable,
    vector<vector<string>>& outputTable, int eStr, vector<State>& allStates, map<vector<string>, string>& allStatesVector) {
    State outputState = {};
    outputState.fin = false;
    CreateState(ecloses, inputTable, outputTable, eStr, 1, 1, outputState);
    allStates.push_back(outputState);
    allStatesVector.insert(make_pair(outputState.arrOfStates, "S" + to_string(allStatesVector.size())));

    for (auto i = 0; i < allStates.size(); i++)
        for (auto j = 0; j < allStates[i].transitions.size(); j++)
            if (IsInVector(allStatesVector, allStates[i].transitions[j], ecloses, allStates[i].transitionsName[j]) == false && !allStates[i].transitions[j].empty()) {
                State newState;
                newState.fin = false;

                for (auto z = 0; z < allStates[i].transitions[j].size(); z++) {
                    int column = ecloses[allStates[i].transitions[j][z]].column;
                    CreateState(ecloses, inputTable, outputTable, eStr, 1, column, newState);
                }
                allStatesVector.insert(make_pair(newState.arrOfStates, "S" + to_string(allStatesVector.size())));

                allStates.push_back(newState);
            }

    for (auto item : allStatesVector) {
        for (auto j = 0; j < item.first.size(); j++)
            std::cout << item.first[j] << " ";
        std::cout << "-" << item.second << "\n";
    }
}

void HandleMachine(map<string, Eclose>& ecloses, vector<vector<string>>& inputTable, vector<vector<string>>& outputTable, int eStr) {
    vector<string> line;
    line.push_back("");
    outputTable.push_back(line);
    outputTable.push_back(line);

    for (size_t i = 2; i < inputTable.size() - 1; i++) {
        line.pop_back();
        line.push_back(inputTable[i][0]);
        outputTable.push_back(line);
    }

    vector<State> allStates;
    map<vector<string>, string> allStatesVector;
    CreateAllStates(ecloses, inputTable, outputTable, eStr, allStates, allStatesVector);

    for (size_t st = 0; st < allStates.size(); st++) {
        outputTable[1].push_back(allStatesVector[allStates[st].arrOfStates]);
    }

    outputTable[0].resize(outputTable[1].size(), "");

    for (size_t st = 0; st < allStates.size(); st++) {
        for (size_t i = 2; i < outputTable.size(); i++) {
            if (allStates[st].transitionsName[i - 2].empty())
                outputTable[i].push_back("");
            else
                outputTable[i].push_back(allStatesVector[allStates[st].transitions[i - 2]]);
        }
    }

    bool isFAdded = false;
    for (size_t st = 0; st < allStates.size(); st++) {
        if (allStates[st].fin && !isFAdded) {
            auto it = find(outputTable[1].begin(), outputTable[1].end(), allStatesVector[allStates[st].arrOfStates]);
            if (it != outputTable[1].end()) {
                int colIndex = distance(outputTable[1].begin(), it);
                if (colIndex < outputTable[0].size()) {
                    if (colIndex == outputTable[0].size() - 1) {
                        outputTable[0][colIndex] = "F";
                        isFAdded = true;
                    }
                }
            }
        }
    }
}
bool CreateEcloses(map<string, Eclose>& ecloses, vector<vector<string>>& inputTable, int eStr) {
    if (inputTable[inputTable.size() - 1][0] == "e")
        eStr = inputTable.size() - 1;
    else
        return false;
    for (auto i = 1; i < inputTable[1].size(); i++) {
        bool fin = false;
        if (inputTable[0][i] == "F")
            fin = true;
        Eclose eclose = {};
        eclose.state = inputTable[1][i];
        eclose.column = i;
        eclose.fin = fin;

        if (inputTable[eStr][i] != "" && inputTable[eStr][i] != "-") {
            std::string item;
            std::istringstream strStream(inputTable[eStr][i]);
            while (getline(strStream, item, ','))
                eclose.eStates.push_back(item);
        }
        ecloses.insert(make_pair(inputTable[1][i], eclose));
    }

    return true;
}

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cout << "Invalid input format";
        return 0;
    }

    std::string file = argv[1];
    std::ifstream input;
    input.open(file);
    file = argv[2];
    std::ofstream output;
    output.open(file);

    if (!(input.is_open() && output.is_open())) {
        cerr << "Error open files!\n";
        return 1;
    }
    int eStr = 0;
    vector<vector<string>> inputTable;
    vector<vector<string>> outputTable;
    map<string, Eclose> ecloses;
    ReadTable(input, inputTable);
    if (!CreateEcloses(ecloses, inputTable, eStr)) {
        cerr << "Error file format. There isn't empty sybols!\n";
        return 1;
    };
    HandleMachine(ecloses, inputTable, outputTable, eStr);
    WriteTable(output, outputTable);

    input.close();
    output.close();

    return 0;
}