#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <optional>
#include <map>
#include <set>
#include <algorithm>
#include <iterator>
#include <sstream>
#include <stdexcept>

enum class MachineType
{
    Mealy,
    Moore
};

struct MachineState
{
    std::string state;
    std::optional<std::string> outputData = std::nullopt;

    bool operator==(const MachineState& machineState) const
    {
        return this->state == machineState.state && this->outputData == machineState.outputData;
    }
};

struct Machine
{
    std::vector<std::string> inputData;
    std::vector<std::string> states;
    std::vector<std::vector<MachineState>> machineStates;
    std::vector<std::string> outputData;
};

struct Args
{
    MachineType machineType;
    std::string inputFile;
    std::string outputFile;
};

class ArgsParser
{
public:
    static std::optional<Args> ParseArgs(int argc, char* argv[])
    {
        Args args = {};
        const std::string MEALY_MOORE_COMMAND = "mealy";
        const std::string MOORE_MEALY_COMMAND = "moore";

        if (argc != 4)
        {
            return std::nullopt;
        }

        if (argv[1] == MEALY_MOORE_COMMAND)
        {
            args.machineType = MachineType::Mealy;
        }
        else if (argv[1] == MOORE_MEALY_COMMAND)
        {
            args.machineType = MachineType::Moore;
        }
        else
        {
            return std::nullopt;
        }

        args.inputFile = argv[2];
        args.outputFile = argv[3];
        return args;
    }
};

char GetAlternateLetter(const char letter)
{
    const char FIRST_TO_USE_LETTER = 'S';
    const char SECOND_TO_USE_LETTER = 'Q';
    return letter == FIRST_TO_USE_LETTER ? SECOND_TO_USE_LETTER : FIRST_TO_USE_LETTER;
}

namespace
{
    using StateToTransition = std::map<std::string, std::string>;

    struct MachineWithEquivalentStates : public Machine
    {
        StateToTransition equivalentStates;
    };

    StateToTransition GenerateNewEquivalentStates(const StateToTransition& transitionsForEquivalentStates, const StateToTransition& oldEquivalentStates)
    {
        auto newEquivalentStates = transitionsForEquivalentStates;
        std::string newStateName = { GetAlternateLetter(newEquivalentStates.begin()->second.at(0)) };

        auto index = 0;
        for (auto transition = newEquivalentStates.begin(); transition != newEquivalentStates.end(); transition++)
        {
            if (transition->second.at(0) == newStateName.at(0))
            {
                continue;
            }

            auto replacementTransition = transition->second;
            transition->second = newStateName + std::to_string(index);
            index++;

            auto equivalentStateOfInitiator = oldEquivalentStates.find(transition->first);

            for (auto sameTransition = transition; sameTransition != newEquivalentStates.end(); sameTransition++)
            {
                auto equivalentStateOfCurrent = oldEquivalentStates.find(sameTransition->first);

                if (sameTransition->second == replacementTransition && (equivalentStateOfInitiator == oldEquivalentStates.end()
                    || equivalentStateOfInitiator->second == equivalentStateOfCurrent->second))
                {
                    sameTransition->second = transition->second;
                }
            }
        }

        return newEquivalentStates;
    }

    StateToTransition ExtractTransitionsToStates(const MachineWithEquivalentStates& machine)
    {
        StateToTransition transitionsForEquivalentStates;
        int inputsCount = machine.inputData.size();
        int statesCount = machine.states.size();

        for (auto indexI = 0; indexI < statesCount; indexI++)
        {
            std::string states;
            for (auto indexJ = 0; indexJ < inputsCount; indexJ++)
            {
                states += machine.machineStates.at(indexJ).at(indexI).state;
            }
            transitionsForEquivalentStates.emplace(std::pair<std::string, std::string>{machine.states.at(indexI), states});
        }

        return transitionsForEquivalentStates;
    }

    std::set<std::string> ExtractEquivalentStates(const MachineWithEquivalentStates& machine)
    {
        std::set<std::string> equivalentStates;
        for (const auto& equivalentState : machine.equivalentStates)
        {
            equivalentStates.insert(equivalentState.second);
        }

        return equivalentStates;
    }
}

class MachineMinimizator
{
public:
    static Machine MinimizeMealyMachine(const Machine& machine)
    {
        MachineWithEquivalentStates newMachine = { machine.inputData, machine.states, machine.machineStates, machine.outputData };
        StateToTransition transitionsForEquivalentStates;
        int inputsCount = newMachine.inputData.size();
        int statesCount = newMachine.states.size();

        for (auto indexI = 0; indexI < statesCount; indexI++)
        {
            std::string states;
            for (auto indexJ = 0; indexJ < inputsCount; indexJ++)
            {
                states += *machine.machineStates.at(indexJ).at(indexI).outputData;
            }
            transitionsForEquivalentStates.emplace(std::pair<std::string, std::string>{newMachine.states.at(indexI), states});
        }

        newMachine.equivalentStates = GenerateNewEquivalentStates(transitionsForEquivalentStates, newMachine.equivalentStates);

        UpdateTransitionsWithNewEquivalentStates(newMachine, machine);

        return MinimizeMachine(newMachine, machine);
    }

    static Machine MinimizeMooreMachine(const Machine& machine)
    {
        MachineWithEquivalentStates newMachine = { machine.inputData, machine.states, machine.machineStates, machine.outputData };

        StateToTransition transitionsForEquivalentStates;

        for (auto indexI = 0; indexI < machine.states.size(); indexI++)
        {
            transitionsForEquivalentStates.emplace(std::pair<std::string, std::string>{machine.states.at(indexI), machine.outputData.at(indexI)});
        }

        newMachine.equivalentStates = GenerateNewEquivalentStates(transitionsForEquivalentStates, newMachine.equivalentStates);
        UpdateTransitionsWithNewEquivalentStates(newMachine, machine);
        return MinimizeMachine(newMachine, machine);
    }

private:
    static Machine MinimizeMachine(MachineWithEquivalentStates& machine, const Machine& originMachine)
    {
        int countOfEquivalentStates = 0;
        int currentCountOfEquivalentStates = ExtractEquivalentStates(machine).size();
        while (countOfEquivalentStates != currentCountOfEquivalentStates && currentCountOfEquivalentStates != machine.states.size())
        {
            auto transitionsForEquivalentStates = ExtractTransitionsToStates(machine);
            machine.equivalentStates = GenerateNewEquivalentStates(transitionsForEquivalentStates, machine.equivalentStates);
            UpdateTransitionsWithNewEquivalentStates(machine, originMachine);
            countOfEquivalentStates = currentCountOfEquivalentStates;
            currentCountOfEquivalentStates = ExtractEquivalentStates(machine).size();
        }

        return GenerateNewMachineFromEquivalentStates(machine, originMachine);
    }

    static void UpdateTransitionsWithNewEquivalentStates(MachineWithEquivalentStates& machine, const Machine& originMachine)
    {
        int inputsCount = machine.inputData.size();
        int statesCount = machine.states.size();

        for (auto indexJ = 0; indexJ < statesCount; indexJ++)
        {
            auto currentState = machine.states.at(indexJ);

            for (auto indexI = 0; indexI < inputsCount; indexI++)
            {
                auto originState = originMachine.machineStates.at(indexI).at(indexJ).state;
                auto it = machine.equivalentStates.find(originState);

                if (it == machine.equivalentStates.end())
                {
                    throw std::runtime_error("");
                }

                machine.machineStates.at(indexI).at(indexJ).state = it->second;
                machine.machineStates.at(indexI).at(indexJ).outputData = originMachine.machineStates.at(indexI).at(indexJ).outputData;
            }
        }
    }

    static Machine GenerateNewMachineFromEquivalentStates(MachineWithEquivalentStates& machine, const Machine& originMachine)
    {
        Machine newMachine;
        newMachine.inputData = machine.inputData;
        auto setNewStates = ExtractEquivalentStates(machine);
        newMachine.states = std::vector<std::string>(setNewStates.size());
        std::copy(setNewStates.begin(), setNewStates.end(), newMachine.states.begin());
        std::sort(newMachine.states.begin(), newMachine.states.end());

        int inputsCount = newMachine.inputData.size();
        int statesCount = newMachine.states.size();

        if (!std::empty(originMachine.outputData))
        {
            for (auto index = 0; index < statesCount; index++)
            {
                auto it = std::find_if(machine.equivalentStates.begin(), machine.equivalentStates.end(), [=](const std::pair<std::string, std::string>& element) {
                    return element.second == newMachine.states.at(index);
                    });
                auto distance = std::distance(originMachine.states.begin(), std::find(originMachine.states.begin(), originMachine.states.end(), it->first));
                newMachine.outputData.push_back(originMachine.outputData.at(distance));
            }
        }

        for (auto index = 0; index < inputsCount; index++)
        {
            newMachine.machineStates.emplace_back(std::vector<MachineState>(statesCount, MachineState()));
        }

        for (auto indexJ = 0; indexJ < statesCount; indexJ++)
        {
            auto currentState = newMachine.states.at(indexJ);
            auto originState = std::find_if(machine.equivalentStates.begin(), machine.equivalentStates.end(), [=](const std::pair<std::string, std::string>& element) {
                return element.second == currentState;
                });
            auto it = std::find(originMachine.states.begin(), originMachine.states.end(), originState->first);
            auto distance = std::distance(originMachine.states.begin(), it);

            for (auto indexI = 0; indexI < inputsCount; indexI++)
            {
                MachineState oldState = originMachine.machineStates.at(indexI).at(distance);
                auto newState = machine.equivalentStates.find(oldState.state);

                newMachine.machineStates.at(indexI).at(indexJ).state = newState->second;
                newMachine.machineStates.at(indexI).at(indexJ).outputData = oldState.outputData;
            }
        }

        return newMachine;
    }
};

class MachineSaver
{
public:
    void static SaveMealyMachine(std::ostream& output, const Machine& machine)
    {
        SaveSingleStates(output, machine.states, true);
        SaveStateTransitions(output, machine, true);
    }

    void static SaveMooreMachine(std::ostream& output, const Machine& machine)
    {
        SaveSingleStates(output, machine.outputData, true);
        SaveSingleStates(output, machine.states, true);
        SaveStateTransitions(output, machine);
    }

private:
    void static SaveSingleStates(std::ostream& output, const std::vector<std::string>& states, bool needToSkipFirstValue = false)
    {
        if (needToSkipFirstValue)
        {
            output << m_separator;
        }

        std::copy(states.begin(), states.end() - 1, std::ostream_iterator<std::string>(output, m_separator));
        output << states.at(states.size() - 1) << std::endl;
    }

    void static SaveStateTransitions(std::ostream& output, const Machine& machine, bool needToShowOutputWithState = false)
    {
        int inputsCount = machine.inputData.size();
        int statesCount = machine.states.size();

        for (auto indexI = 0; indexI < inputsCount; indexI++)
        {
            output << machine.inputData.at(indexI);

            for (auto indexJ = 0; indexJ < statesCount; indexJ++)
            {
                output << m_separator;
                auto currentState = machine.machineStates.at(indexI).at(indexJ);
                output << currentState.state;
                if (needToShowOutputWithState)
                {
                    output << m_stateSeparator << *currentState.outputData;
                }
            }

            output << std::endl;
        }
    }

    static inline auto m_separator = ";";
    static inline auto m_stateSeparator = "/";
};

namespace
{
    constexpr auto EMPTY_OUTPUT_SYMBOL = "empty";
}

class CSVTextParser
{
public:
    static Machine ParseMealy(std::istream& istream)
    {
        Machine machine = {};

        ParseTypicalMachineInputData(istream, machine);

        return machine;
    }

    static Machine ParseMoore(std::istream& istream)
    {
        Machine machine = {};

        ParseSpecificMachineInputData(istream, machine);
        ParseTypicalMachineInputData(istream, machine);

        return machine;
    }

private:
    void static ParseTypicalMachineInputData(std::istream& istream, Machine& machine)
    {
        std::string line;
        std::getline(istream, line);
        std::vector<std::string> parsedLine;
        SplitLine(line, parsedLine);
        parsedLine.erase(parsedLine.begin());
        machine.states = parsedLine;

        while (std::getline(istream, line))
        {
            std::vector<std::string> values;
            SplitLine(line, values);
            machine.inputData.push_back(values.at(0));
            values.erase(values.begin());
            PopulateMachineStateTransitions(machine, values);
        }
    }

    void static ParseSpecificMachineInputData(std::istream& istream, Machine& machine)
    {
        std::string line;
        std::getline(istream, line);
        std::vector<std::string> parsedLine;
        SplitLine(line, parsedLine);
        parsedLine.erase(parsedLine.begin());
        machine.outputData = parsedLine;
    }

    void static PopulateMachineStateTransitions(Machine& machine, std::vector<std::string>& transitions)
    {
        std::vector<MachineState> machineStates;

        for (const auto& transition : transitions)
        {
            MachineState state;
            auto index = transition.find("/");
            if (index != std::string::npos)
            {
                state.state = transition.substr(0, index);
                state.outputData = transition.substr(index + 1, transition.length());
            }
            else
            {
                auto it = std::find(machine.states.begin(), machine.states.end(), transition);
                state.state = transition;
                state.outputData = machine.outputData.at(std::distance(machine.states.begin(), it));
            }
            machineStates.push_back(state);
        }

        machine.machineStates.push_back(machineStates);
    }

    void static SplitLine(std::string& line, std::vector<std::string>& states)
    {
        std::string state;
        std::istringstream ss(line);

        while (std::getline(ss, state, ';'))
        {
            if (state.empty())
            {
                state = EMPTY_OUTPUT_SYMBOL;
            }
            states.push_back(state);
        }
    }
};

bool InitializeStreams(std::ifstream& input, std::ofstream& output, const Args& args)
{
    input.open(args.inputFile);

    if (!input.is_open())
    {
        std::cout << "Input file couldn't be opened" << std::endl;
        return false;
    }

    output.open(args.outputFile);

    if (!output.is_open())
    {
        std::cout << "Output file couldn't be opened" << std::endl;
        return false;
    }

    return true;
}

int main(int argc, char* argv[])
{
    auto args = ArgsParser::ParseArgs(argc, argv);
    if (!args)
    {
        std::cout << "Usage: min.exe mealy|moore input.csv output.csv" << std::endl;
        return 1;
    }

    std::ifstream input;
    std::ofstream output;
    if (!InitializeStreams(input, output, *args))
    {
        return 1;
    }

    Machine machine;
    if (args->machineType == MachineType::Mealy)
    {
        machine = CSVTextParser::ParseMealy(input);
        MachineSaver::SaveMealyMachine(output, MachineMinimizator::MinimizeMealyMachine(machine));
    }
    else
    {
        machine = CSVTextParser::ParseMoore(input);
        MachineSaver::SaveMooreMachine(output, MachineMinimizator::MinimizeMooreMachine(machine));
    }

    return 0;
}