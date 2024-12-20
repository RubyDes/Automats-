#include "ArgsParser.h"

ArgsParser::ArgsParser(int argc, char** argv)
	: m_argc(argc)
	, m_argv(argv)
{
}

const ConversionMode ArgsParser::GetConversionMode() const
{
	return m_conversionMode;
}

const std::string& ArgsParser::GetInputFileName() const
{
	return m_inFileName;
}

const std::string& ArgsParser::GetOutputFileName() const
{
	return m_outFileName;
}

void ArgsParser::Parse()
{
	if (m_argc != Constants::ARGS_COUNT)
	{
		throw std::runtime_error("Invalid number of arguments.");
	}

	if (m_argv[1] == Constants::MEALY_TO_MOORE_MODE)
	{
		m_conversionMode = ConversionMode::MealyToMoore;
	}
	else if (m_argv[1] == Constants::MOORE_TO_MEALY_MODE)
	{
		m_conversionMode = ConversionMode::MooreToMealy;
	}
	else
	{
		throw std::runtime_error("Invalid conversion mode string.");
	}

	m_inFileName = m_argv[2];
	m_outFileName = m_argv[3];
}
