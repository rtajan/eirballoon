/*!
 * \file
 * \brief Filters a signal.
 *
 * \section LICENSE
 * This file is under MIT license (https://opensource.org/licenses/MIT).
 */
#include <string>
#include <memory>
#include <stdexcept>
#include <cmath>
#include <sstream>

#include "Tools/Exception/exception.hpp"

#include "Module/Converter/f2i/Converter_f2i.hpp"

namespace aff3ct
{
namespace module
{
Converter_f2i::
Converter_f2i(const int N)
: Converter<float,int8_t>(N)
{
}

void Converter_f2i::
_convert(const float *X_N, int8_t *Y_N, const int frame_id)
{
	for (int n=0; n<this->N; n++)
		Y_N[n] = (int8_t)(X_N[n]*127.0f);
}
}
}

