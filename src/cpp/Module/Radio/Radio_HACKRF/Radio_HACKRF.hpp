#ifdef LINK_LIBHACKRF

/*!
 * \file
 * \brief Pushes data to a file.
 *
 * \section LICENSE
 * This file is under MIT license (https://opensource.org/licenses/MIT).
 */
#ifndef Radio_HACKRF_HPP
#define Radio_HACKRF_HPP

#include <libhackrf/hackrf.h>

#include "Module/Radio/Radio.hpp"
#include "Ring_Buffer/Ring_Buffer.hpp"

namespace aff3ct
{
namespace module
{

struct HACKRF_params
{
	int N                      = 0;
	bool threaded              = false;
	uint64_t fifo_size         = uint64_t(10000000);
	std::string type           = "";
	std::string addr           = "";
	double clk_rate            = 0; // If clk_rate is 0,the default clock rate is used.

	bool rx_enabled            = false;
	double rx_rate             = 0; // if rx_rate is not overriden, rx is disabled
	std::string rx_subdev_spec = "";
	std::string rx_antenna      = "";
	double rx_freq             = 1090e6;
	double rx_gain             = 10;
	std::string rx_filepath    = "";
	std::string tx_filepath    = "";

	bool tx_enabled            = false;
	double tx_rate             = 0; // if tx_rate is not overriden, tx is disabled
	std::string tx_subdev_spec = "";
	std::string tx_antenna     = "";
	double tx_freq             = 833e6;
	double tx_gain             = 10;

	HACKRF_params();
	~HACKRF_params() = default;
};
/*!
 * \class Radio
 *
 * \brief Transmit or receive data to or from a radio module.
 *
 * \tparam R: type of the data to send or receive.
 *
 */
template <typename R = float>
class Radio_HACKRF : public Radio<R>, public tools::Interface_waiting
{
private:
	/*uhd::usrp::multi_usrp::sptr usrp;
	uhd::stream_args_t          stream_args;
	uhd::rx_streamer::sptr      rx_stream;
	uhd::tx_streamer::sptr      tx_stream;

	boost::thread send_thread;
	boost::thread receive_thread;

	const bool threaded;
	const bool rx_enabled;
	const bool tx_enabled;

	std::vector<R*>       fifo_send;
	std::vector<R*>       fifo_receive;
	std::vector<int32_t*> fifo_ovf_flags;
	std::vector<int32_t*> fifo_seq_flags;
	std::vector<int32_t*> fifo_clt_flags;
	std::vector<int32_t*> fifo_tim_flags;

	std::atomic<bool> stop_threads;

	std::atomic<std::uint64_t> idx_w_send;
	std::atomic<std::uint64_t> idx_r_send;

	std::atomic<std::uint64_t> idx_w_receive;
	std::atomic<std::uint64_t> idx_r_receive;

	bool start_thread_send;
	bool start_thread_receive;*/

public:
	Radio_HACKRF(const HACKRF_params& params);
	~Radio_HACKRF();

	Ring_Buffer buffer;
	hackrf_device* device;
	bool stop;

	void flush();
	virtual void reset();
	virtual void send_cancel_signal();
	virtual void wake_up();
	void start_rx();
	void start_tx();
	void stop_rx();
	void stop_tx();

	virtual void cancel_waiting();

protected:
	void _send   (const R *X_N1, const int frame_id);
	void _receive(      R *Y_N1, const int frame_id);


	static int rx_callback(hackrf_transfer* transfer);
	static int tx_callback(hackrf_transfer* transfer);

/*private:
	void thread_function_receive();
	inline void receive_usrp     (int32_t *OVF, int32_t *SEQ, int32_t *CLT, int32_t *TIM, R *Y_N1);
	inline void fifo_receive_read(int32_t *OVF, int32_t *SEQ, int32_t *CLT, int32_t *TIM, R *Y_N1);
	inline void fifo_receive_write();

	void thread_function_send();
	inline void send_usrp(const R *X_N1);
	inline void fifo_send_read();
	inline void fifo_send_write(const R* X_N1);*/
};
}
}

#endif /* Radio_HACKRF_HPP */

#endif