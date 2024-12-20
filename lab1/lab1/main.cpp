// converter.cpp : Defines the entry point for the application.
//

#include "ArgsParser.h"
#include "MealyMachineTable.h"

int main(int argc, char** argv)
try
{
	ArgsParser argsParser(argc, argv);

	argsParser.Parse();

	switch (argsParser.GetConversionMode())
	{
	case ConversionMode::MealyToMoore:
		{
			MealyMachineTable mealy;
			mealy.ReadFromCsvFile(argsParser.GetInputFileName());
			MooreMachineTable moore = mealy.ConvertToMoore<MooreMachineTable>();
			moore.PrintToCsvFile(argsParser.GetOutputFileName());
		}
		break;
	case ConversionMode::MooreToMealy:
		{
			MooreMachineTable moore;
			moore.ReadFromCsvFile(argsParser.GetInputFileName());
			MealyMachineTable mealy = moore.ConvertToMealy<MealyMachineTable>();
			mealy.PrintToCsvFile(argsParser.GetOutputFileName());
		}
		break;
	default:
			throw std::logic_error("Unknown conversion mode.");
	}

	return 0;
}
catch (const std::runtime_error& e)
{
	std::cout << "Error: " << e.what() << std::endl;
	std::cout << Constants::USAGE_HELP_MESSAGE << std::endl;
	return 1;
}
