#ifndef CONSTANTS_H
#define CONSTANTS_H

#include <string>

namespace Constants
{
const std::string MEALY_TO_MOORE_MODE = "mealy-to-moore";
const std::string MOORE_TO_MEALY_MODE = "moore-to-mealy";
const std::string USAGE_HELP_MESSAGE = "\tUsage: convert.exe mealy-to-moore|moore-to-mealy input_file_name output_file_name";
const size_t ARGS_COUNT = 4;
}; // namespace Constants

#endif // !CONSTANTS_H
