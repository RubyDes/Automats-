#ifndef MOORE_MACHINE_TABLE_H
#define MOORE_MACHINE_TABLE_H

#include "pch.h"
#include "MealyMachineTable.h"

class MooreMachineTable
{
public:
	friend class MealyMachineTable;

	void ReadFromCsvFile(const std::string& fileName, const char sep = ';');

	void PrintToCsvFile(const std::string& fileName, const char sep = ';') const;

	template <typename Mealy>
	Mealy ConvertToMealy(const char stateSymbol = 's') const
	{
		Mealy mealyTable;

		std::unordered_map<std::string, std::string> mooreStateToMealyState;
		size_t count = 0;
		for (auto& state : m_mooreTable)
		{
			mooreStateToMealyState[state.first] = stateSymbol + std::to_string(count);
			count++;
		}

		for (auto& state : m_mooreTable)
		{
			std::string stateId = mooreStateToMealyState.at(state.first);

			std::map<std::string, typename Mealy::MealyTransition> mealyTransitions;
			for (auto& mooreTransition : state.second.transitions)
			{
				mealyTransitions[mooreTransition.first] = {
					mooreStateToMealyState[mooreTransition.second],
					m_mooreTable.at(mooreTransition.second).outputSignal
				};
			}

			mealyTable.m_mealyTable[stateId].transitions = mealyTransitions;
		}

		mealyTable.m_inputSignalIds = m_inputSignalIds;

		return mealyTable;
	}

private:
	struct MooreState
	{
		std::string outputSignal;
		std::map<std::string, std::string> transitions;
	};

	std::map<std::string, MooreMachineTable::MooreState> m_mooreTable;

	std::vector<std::string> m_inputSignalIds;
};

#endif // !MOORE_MACHINE_TABLE_H
