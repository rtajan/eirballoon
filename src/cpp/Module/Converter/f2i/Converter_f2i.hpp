/*!
 * \file
 * \brief Filters a signal.
 *
 * \section LICENSE
 * This file is under MIT license (https://opensource.org/licenses/MIT).
 */
#ifndef CONVERTER_F2I_HPP_
#define CONVERTER_F2I_HPP_

#include <vector>

#include "Module/Converter/Converter.hpp"

namespace aff3ct
{
namespace module
{

/*!
 * \class Converter_f2i
 *
 * \brief Convert the signal type.
 *
 * \tparam R: type of the reals (floating-point representation) of the filtering process.
 * \tparam R: type of the reals (floating-point representation) of the filtering process.
 *
 * Please use Converter_f2i for inheritance (instead of Converter_f2i)
 */
class Converter_f2i : public Converter<float, int8_t>
{
public:
	/*!
	 * \brief Constructor.
	 *
	 * \param N:        size of one frame (= number of samples in one frame).
	 */
	Converter_f2i(const int N);

	/*!
	 * \brief Destructor.
	 */
	virtual ~Converter_f2i() = default;

protected:
	virtual void _convert(const float *X_N,  int8_t *Y_N, const int frame_id);

};
}
}

#endif /* CONVERTER_F2I_HPP_ */
