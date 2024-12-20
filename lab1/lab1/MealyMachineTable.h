#ifndef MEALY_MACHINE_TABLE_H
#define MEALY_MACHINE_TABLE_H

#include "pch.h"
#include "MooreMachineTable.h"

class MealyMachineTable
{
public:
	friend class MooreMachineTable;

	void ReadFromCsvFile(const std::string& fileName, const char sep = ';');

	template<typename Moore>
	Moore ConvertToMoore(const char stateSymbol = 's') const
	{
		Moore mooreTable;

		std::unordered_map<struct MealyTransition, std::string, MealyTransitionHash> mealyTransToMooreStates;

		std::unordered_map<std::string, std::string> mooreStatesToMealyStates;

		int count = 0;
		for (const auto& stateTransitions : m_mealyTable)
		{
			for(auto& transition : stateTransitions.second.transitions)
			{
				if (mealyTransToMooreStates.find(transition.second) == mealyTransToMooreStates.end())
				{
					std::string stateName = stateSymbol + std::to_string(count);

					mealyTransToMooreStates[transition.second] = stateName;
					mooreStatesToMealyStates[stateName] = transition.second.nextState;
					mooreTable.m_mooreTable[stateName] = { transition.second.outputSignal, {} };

					count++;
				}
			}
		}

		for (auto& mooreState : mooreTable.m_mooreTable)
		{
			auto mealyState = mooreStatesToMealyStates[mooreState.first];

			std::map<std::string, std::string> mooreTransitions;

			for (auto& mealyTransition : m_mealyTable.at(mealyState).transitions)
			{
				mooreTransitions[mealyTransition.first] = mealyTransToMooreStates[mealyTransition.second];
			}

			mooreTable.m_mooreTable[mooreState.first].transitions = mooreTransitions;
		}

		mooreTable.m_inputSignalIds = m_inputSignalIds;

		return mooreTable;
	}

	void PrintToCsvFile(const std::string& fileName, const char sep = ';') const;

private:
	struct MealyTransition
	{
		std::string nextState;
		std::string outputSignal;

		bool operator==(const MealyTransition& other) const
		{
			return nextState == other.nextState && outputSignal == other.outputSignal;
		}
	};

	struct MealyTransitionHash
	{
		std::size_t operator()(const MealyTransition& object) const noexcept
		{
			std::size_t h1 = std::hash<std::string>{}(object.nextState);
			std::size_t h2 = std::hash<std::string>{}(object.outputSignal);
			return h1 ^ (h2 << 1);
		}
	};

	struct MealyState
	{
		std::map<std::string, MealyMachineTable::MealyTransition> transitions;
	};
	
	std::map<std::string, MealyMachineTable::MealyState> m_mealyTable;

	std::vector<std::string> m_inputSignalIds;

	static MealyTransition ParseMealyTransition(const std::string& str);
};

#endif
