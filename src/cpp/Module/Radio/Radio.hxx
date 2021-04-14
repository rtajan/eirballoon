/*!
 * \file
 * \brief Sens or receive samples to or from a Radio
 *
 * \section LICENSE
 * This file is under MIT license (https://opensource.org/licenses/MIT).
 */
#ifndef RADIO_HXX_
#define RADIO_HXX_

#include <sstream>
#include <complex>
#include <csignal>

#include "Tools/Exception/exception.hpp"

#include "Module/Radio/Radio.hpp"

template<typename R>
bool aff3ct::module::Radio<R>::done_flag = false;

namespace aff3ct
{
namespace module
{

template <typename R>
Radio<R>
::Radio(const int N)
: Module(),
  N(N),
  ovf_flags(1, 0),
  seq_flags(1, 0),
  clt_flags(1, 0),
  tim_flags(1, 0)
{
	const std::string name = "Radio";
	this->set_name(name);
	this->set_short_name(name);
	signal(SIGINT, Radio<R>::signal_handler);

	if (N <= 0)
	{
		std::stringstream message;
		message << "'N' has to be greater than 0 ('N' = " << N << ").";
		throw tools::invalid_argument(__FILE__, __LINE__, __func__, message.str());
	}

	auto &p1 = this->create_task("send");
	auto p1s_X_N1 = this->template create_socket_in <R>(p1, "X_N1", 2 * N);
	this->create_codelet(p1, [p1s_X_N1](Module &m, Task &t, const size_t frame_id) -> int
	{
		static_cast<Radio<R>&>(m)._send(static_cast<R*>(t[p1s_X_N1].get_dataptr()), frame_id);
		return 0;
	});

	auto &p2 = this->create_task("receive");
	auto p2s_OVF  = this->template create_socket_out<int32_t>(p2, "OVF" , 1    );
	auto p2s_SEQ  = this->template create_socket_out<int32_t>(p2, "SEQ" , 1    );
	auto p2s_CLT  = this->template create_socket_out<int32_t>(p2, "CLT" , 1    );
	auto p2s_TIM  = this->template create_socket_out<int32_t>(p2, "TIM" , 1    );
	auto p2s_Y_N1 = this->template create_socket_out<R      >(p2, "Y_N1", 2 * N);
	this->create_codelet(p2, [p2s_OVF, p2s_SEQ, p2s_CLT, p2s_TIM, p2s_Y_N1](Module &m, Task &t, const size_t frame_id) -> int
	{
		auto& radio = static_cast<Radio<R>&>(m);
		radio._receive(static_cast<R*>(t[p2s_Y_N1].get_dataptr()), frame_id);


		auto OVF = static_cast<int32_t*>(t[p2s_OVF ].get_dataptr());
		auto SEQ = static_cast<int32_t*>(t[p2s_SEQ ].get_dataptr());
		auto CLT = static_cast<int32_t*>(t[p2s_CLT ].get_dataptr());
		auto TIM = static_cast<int32_t*>(t[p2s_TIM ].get_dataptr());
		*OVF = radio.ovf_flags[frame_id];
		*SEQ = radio.seq_flags[frame_id];
		*CLT = radio.clt_flags[frame_id];
		*TIM = radio.tim_flags[frame_id];
		radio.ovf_flags[frame_id] = 0;
		radio.seq_flags[frame_id] = 0;
		radio.clt_flags[frame_id] = 0;
		radio.tim_flags[frame_id] = 0;

		return 0;
	});
}

template <typename R>
bool Radio<R>
::is_done() const
{
	return Radio<R>::done_flag;
}

template <typename R>
void Radio<R>
::set_n_frames(const size_t n_frames)
{
	this->ovf_flags.resize(n_frames);
	this->seq_flags.resize(n_frames);
	this->clt_flags.resize(n_frames);
	this->tim_flags.resize(n_frames);
	this->Module::set_n_frames(n_frames);
}

template <typename R>
template <class A>
void Radio<R>
::send(const std::vector<R,A>& X_N1, const int frame_id, const bool managed_memory)
{
	(*this)[rad::sck::send::X_N1].bind(X_N1);
	(*this)[rad::tsk::send].exec(frame_id, managed_memory);

}

template <typename R>
void Radio<R>
::send(const R *X_N1, const int frame_id, const bool managed_memory)
{
	(*this)[rad::sck::send::X_N1].bind(X_N1);
	(*this)[rad::tsk::send].exec(frame_id, managed_memory);
}

template <typename R>
template <class A>
void Radio<R>
::receive(std::vector<int32_t>& OVF,
          std::vector<int32_t>& SEQ,
          std::vector<int32_t>& CLT,
          std::vector<int32_t>& TIM,
          std::vector<R,A>& Y_N1,
          const int frame_id,
          const bool managed_memory)
{
	(*this)[rad::sck::receive::OVF ].bind(OVF);
	(*this)[rad::sck::receive::SEQ ].bind(SEQ);
	(*this)[rad::sck::receive::CLT ].bind(CLT);
	(*this)[rad::sck::receive::TIM ].bind(TIM);
	(*this)[rad::sck::receive::Y_N1].bind(Y_N1);

	(*this)[rad::tsk::receive].exec(frame_id, managed_memory);

	//this->receive(OVF.data(), SEQ.data(), CLT.data(), TIM.data(), Y_N1.data(), frame_id);
}

template <typename R>
void Radio<R>
::receive(int32_t *OVF, int32_t *SEQ, int32_t *CLT, int32_t *TIM, R *Y_N1, const int frame_id, const bool managed_memory)
{
	(*this)[rad::sck::receive::OVF ].bind(OVF);
	(*this)[rad::sck::receive::SEQ ].bind(SEQ);
	(*this)[rad::sck::receive::CLT ].bind(CLT);
	(*this)[rad::sck::receive::TIM ].bind(TIM);
	(*this)[rad::sck::receive::Y_N1].bind(Y_N1);

	(*this)[rad::tsk::receive].exec(frame_id, managed_memory);
}

template <typename R>
void Radio<R>::signal_handler (int signum)
{
	Radio<R>::done_flag = true;
}

}
}


#endif
