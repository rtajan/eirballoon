/*!
 * \file
 * \brief Filters a signal.
 *
 * \section LICENSE
 * This file is under MIT license (https://opensource.org/licenses/MIT).
 */
#ifndef CONVERTER_HXX_
#define CONVERTER_HXX_

#include <string>
#include <memory>
#include <stdexcept>
#include <cmath>
#include <sstream>

#include "Tools/Exception/exception.hpp"

#include "Module/Converter/Converter.hpp"

namespace aff3ct
{
namespace module
{
template <typename T1, typename T2>
Converter<T1, T2>::
Converter(const int N)
: Module(), N(N)
{
	const std::string name = "Converter";
	this->set_name(name);
	this->set_short_name(name);
	this->set_single_wave(true);

	if (N <= 0)
	{
		std::stringstream message;
		message << "'N' has to be greater than 0 ('N' = " << N << ").";
		throw tools::invalid_argument(__FILE__, __LINE__, __func__, message.str());
	}

	this->init_processes();
}

template <typename T1, typename T2>
void Converter<T1,T2>::
init_processes()
{
	auto &p1 = this->create_task("convert");
	auto p1s_X_N = this->template create_socket_in <T1>(p1, "X_N", this->N);
	auto p1s_Y_N = this->template create_socket_out<T2>(p1, "Y_N", this->N);
	this->create_codelet(p1, [p1s_X_N, p1s_Y_N](Module &m, Task &t, const size_t frame_id) -> int
	{
		static_cast<Converter<T1,T2>&>(m)._convert(static_cast<T1*>(t[p1s_X_N].get_dataptr()),
		                                           static_cast<T2*>(t[p1s_Y_N].get_dataptr()),
										           frame_id);

		return 0;
	});

}

template <typename T1, typename T2>
int Converter<T1,T2>::
get_N() const
{
	return this->N;
}

template <typename T1, typename T2>
Converter<T1,T2>* Converter<T1,T2>
::clone() const
{
	auto m = new Converter(*this);
	m->deep_copy(*this);
	return m;
}

template <typename T1, typename T2>
void Converter<T1,T2>::
_convert(const T1 *X_N, T2 *Y_N, const int frame_id)
{
	throw tools::unimplemented_error(__FILE__, __LINE__, __func__);
}

}
}

#endif