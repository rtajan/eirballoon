/*!
 * \file
 * \brief Filters a signal.
 *
 * \section LICENSE
 * This file is under MIT license (https://opensource.org/licenses/MIT).
 */
#ifndef CONVERTER_HPP_
#define CONVERTER_HPP_

#include <vector>

#include "Module/Module.hpp"

namespace aff3ct
{
namespace module
{
	namespace cvt
	{
		enum class tsk : size_t { convert, SIZE };

		namespace sck
		{
			enum class convert : size_t { X_N, Y_N, status };
		}
	}

/*!
 * \class Converter
 *
 * \brief Convert the signal type.
 *
 * \tparam R: type of the reals (floating-point representation) of the filtering process.
 * \tparam R: type of the reals (floating-point representation) of the filtering process.
 *
 * Please use Converter for inheritance (instead of Converter)
 */
template <typename T1 = int8_t, typename T2 = float>
class Converter : public Module
{
public:
	inline Task&   operator[](const cvt::tsk          t) { return Module::operator[]((int)t);                        }
	inline Socket& operator[](const cvt::sck::convert s) { return Module::operator[]((int)cvt::tsk::convert)[(int)s];}

protected:
	const int N;     /*!< Size of one frame (= number of samples in one frame) */

public:
	/*!
	 * \brief Constructor.
	 *
	 * \param N:        size of one frame (= number of samples in one frame).
	 */
	Converter(const int N);

	void init_processes();

	/*!
	 * \brief Destructor.
	 */
	virtual ~Converter() = default;

	int get_N() const;

	virtual Converter<T1,T2>* clone() const;
protected:
	virtual void _convert(const T1 *X_N,  T2 *Y_N, const int frame_id);

};
}
}
#include "Converter.hxx"

#endif /* CONVERTER_HPP_ */
