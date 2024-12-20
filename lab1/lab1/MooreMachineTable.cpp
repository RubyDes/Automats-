#include "MooreMachineTable.h"
#include "MealyMachineTable.h"

void MooreMachineTable::ReadFromCsvFile(const std::string& fileName, const char sep)
{
	std::ifstream file(fileName);

	if (!file.is_open())
	{
		throw std::runtime_error("File " + fileName + " not found.");
	}

	std::vector<std::istringstream> fileStrings;

	for (std::string line; std::getline(file, line);)
	{
		fileStrings.emplace_back(std::move(std::istringstream(line)));
	}

	while (!fileStrings[0].eof())
	{
		std::vector<std::string> column;
		std::string stateOutputSignal, stateName;

		for (size_t i = 0; i < fileStrings.size(); i++)
		{
			std::string item;
			std::getline(fileStrings[i], item, sep);

			if (i == 0)
				stateOutputSignal = item;
			else if (i == 1)
				stateName = item;
			else
				column.push_back(item);
		}

		if (stateOutputSignal.empty() && stateName.empty())
		{
			m_inputSignalIds = column;
		}
		else
		{
			std::map<std::string, std::string> transitions;

			size_t i = 0;
			for (const auto& transitionStr : column)
			{
				transitions[m_inputSignalIds[i]] = transitionStr;
				i++;
			}

			m_mooreTable[stateName] = { stateOutputSignal, transitions };
		}
	}
}

void MooreMachineTable::PrintToCsvFile(const std::string& fileName, const char sep) const
{
	std::ofstream file(fileName);

	if (!file.is_open())
	{
		throw std::runtime_error("File " + fileName + " not found.");
	}

	std::vector<std::string> strings({ {}, {} });

	for (auto& inputSignalId : m_inputSignalIds)
	{
		strings.push_back(inputSignalId);
	}

	for (auto& state : m_mooreTable)
	{
		strings[0].append(sep + state.second.outputSignal);
		strings[1].append(sep + state.first);

		size_t i = 2;
		for (auto& transition : state.second.transitions)
		{
			strings[i].append(sep + transition.second);
			i++;
		}
	}

	for (const auto& string : strings)
		file << string << std::endl;
}
