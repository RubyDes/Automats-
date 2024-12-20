#ifndef ARGS_PARSER_H
#define ARGS_PARSER_H
#include <stdexcept>

#include "Constants.h"
#include "ConversionMode.h"

class ArgsParser
{
public:
	ArgsParser(int argc, char** argv);

	const ConversionMode GetConversionMode() const;

	const std::string& GetInputFileName() const;

	const std::string& GetOutputFileName() const;

	void Parse();

private:
	ConversionMode m_conversionMode = ConversionMode::MealyToMoore;
	std::string m_inFileName;
	std::string m_outFileName;

	const int m_argc;
	char** m_argv;
};

#endif
