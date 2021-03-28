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

#include "Module/Interrupteur/Interrupteur.hpp"

namespace aff3ct
{
	namespace module
	{

		template <typename B, typename R>
		Interrupteur<B, R>::
			Interrupteur(const int N)
			: Module(), N(N)
		{
			const std::string name = "Switch";
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

		template <typename B, typename R>
		void Interrupteur<B, R>::
		init_processes()
		{
			auto &p1 = this->create_task("select");
			auto p1s_X_N1 = this->template create_socket_in<R>(p1, "X_N", this->N);
			auto p1s_bln = this->template create_socket_in<B>(p1, "bln",1);

			auto p1s_Y_N2 = this->template create_socket_out<R>(p1, "Y_N", this->N);
			this->create_codelet(p1, [p1s_X_N1, p1s_bln ,p1s_Y_N2](Module &m, Task &t, const size_t frame_id) -> int {
				static_cast<Interrupteur<B,R> &>(m)._select(static_cast<R *>(t[p1s_X_N1].get_dataptr()),
														  static_cast<B *>(t[p1s_bln].get_dataptr()),
														  static_cast<R *>(t[p1s_Y_N2].get_dataptr()),
														  frame_id);

				return 0;
			});
		}

		template <typename B, typename R>
		int Interrupteur<B, R>::
			get_N() const
		{
			return this->N;
		}

		template <typename B, typename R>
		Interrupteur<B,R> *Interrupteur<B,R>::clone() const
		{
			auto m = new Interrupteur(*this);
			m->deep_copy(*this);
			return m;
		}

		template <typename B, typename R>
		void Interrupteur<B,R>::
			_select(const R *X_N, const B *bln, R *Y_N, const int frame_id)
		{
			if (*bln == 0)
				std::copy(X_N, X_N + this->N, Y_N);
			else
				throw tools::processing_aborted(__FILE__, __LINE__, __func__);
		}

	}
}

// ==================================================================================== explicit template instantiation
template class aff3ct::module::Interrupteur<int, float>;
template class aff3ct::module::Interrupteur<int, double>;
// ==================================================================================== explicit template instantiation
