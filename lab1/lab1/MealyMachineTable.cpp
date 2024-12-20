#include "MealyMachineTable.h"

void MealyMachineTable::ReadFromCsvFile(const std::string& fileName, const char sep)
{
	std::ifstream file(fileName);

	if (!file.is_open())
	{
		throw std::runtime_error("File " + fileName + " not found.");
	}

	std::vector<std::istringstream> fileStrings;

	for (std::string line; std::getline(file, line); )
	{
		fileStrings.emplace_back(std::move(std::istringstream(line)));
	}

	while (!fileStrings[0].eof())
	{
		std::vector<std::string> column;
		std::string stateName;

		for (size_t i = 0; i < fileStrings.size(); i++)
		{
			std::string item;
			std::getline(fileStrings[i], item, sep);

			if (i == 0)
				stateName = item;
			else
				column.push_back(item);
		}

		if (stateName.empty() || stateName == " ")
		{
			m_inputSignalIds = column;
		}
		else
		{
			MealyState state;

			size_t i = 0;
			for (const auto& transitionStr : column)
			{
				MealyTransition transition = ParseMealyTransition(transitionStr);
				state.transitions[m_inputSignalIds[i]] = transition;
				i++;
			}

			m_mealyTable[stateName] = state;
		}
	}
}

void MealyMachineTable::PrintToCsvFile(const std::string& fileName, const char sep) const
{
	std::ofstream file(fileName);

	if (!file.is_open())
	{
		throw std::runtime_error("File " + fileName + " not found.");
	}

	std::vector<std::string> strings({ {} });

	for (auto& inputSignalId : m_inputSignalIds)
	{
		strings.push_back(inputSignalId);
	}

	for (auto& [stateName, state] : m_mealyTable)
	{
		strings[0].append(sep + stateName);

		size_t i = 1;
		for (auto& transition : state.transitions)
		{
			strings[i].append(sep + transition.second.nextState + '/' + transition.second.outputSignal);
			i++;
		}
	}

	for (const auto& string : strings)
		file << string << std::endl;
}

MealyMachineTable::MealyTransition MealyMachineTable::ParseMealyTransition(const std::string& str)
{
	size_t delimPos = str.find('/');

	return { str.substr(0, delimPos), str.substr(delimPos + 1) };
}
