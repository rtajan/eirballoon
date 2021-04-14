#ifdef LINK_LIBHACKRF

#include <typeinfo>

#include <aff3ct.hpp>
#include "Tools/Thread_pinning/Thread_pinning.hpp"
#include "Module/Radio/Radio_HACKRF/Radio_HACKRF.hpp"

#include "Tools/types.h"

using namespace aff3ct;
using namespace aff3ct::module;

template <typename R>
Radio_HACKRF<R>
::Radio_HACKRF(const HACKRF_params& params)
: Radio<R>(params.N), buffer(2*params.N*params.fifo_size), device(NULL), stop(false)
{
	const std::string name = "Radio_HACKRF";
	this->set_name(name);

	int result;

	result = hackrf_init();
	if (result != HACKRF_SUCCESS)
	{
		std::stringstream message;
		message << "hackrf_init() failed: " << hackrf_error_name((hackrf_error)result) << "(" <<  result << ")" << std::endl;
		throw::runtime_error(__FILE__, __LINE__, __func__, message.str());
	}
	// Open device
	const char* serial_number = NULL;
	result = hackrf_open_by_serial(serial_number, &this->device);
	if (result != HACKRF_SUCCESS)
	{
		std::stringstream message;
		message << "hackrf_open_by_serial() failed: " << hackrf_error_name((hackrf_error)result) << "(" <<  result << ")" << std::endl;
		throw::runtime_error(__FILE__, __LINE__, __func__, message.str());
	}

	result = hackrf_set_freq(this->device, params.rx_freq);
	if (result != HACKRF_SUCCESS)
	{
		std::stringstream message;
		message << "hackrf_set_freq() failed: " << hackrf_error_name((hackrf_error)result) << "(" <<  result << ")" << std::endl;
		throw::runtime_error(__FILE__, __LINE__, __func__, message.str());
	}
	// Set sample rate
	result = hackrf_set_sample_rate(this->device, params.rx_rate);
	if (result != HACKRF_SUCCESS)
	{
		std::stringstream message;
		message << "hackrf_set_sample_rate() failed: " << hackrf_error_name((hackrf_error)result) << "(" <<  result << ")" << std::endl;
		throw::runtime_error(__FILE__, __LINE__, __func__, message.str());
	}
}


template <typename R>
Radio_HACKRF<R>
::~Radio_HACKRF()
{
	if(this->device != NULL)
  	{
		// Close device
		int result = hackrf_close( this->device );
		if (result != HACKRF_SUCCESS)
		{
			std::stringstream message;
			message << "hackrf_close() failed: " << hackrf_error_name((hackrf_error)result) << "(" <<  result << ")" << std::endl;
			std::cerr << message.str() << std::endl;
		}
		hackrf_exit();
	}
}

template <typename R>
void Radio_HACKRF<R>
::start_rx()
{
	int result = hackrf_start_rx(this->device, rx_callback, (void *)this);
	if (result != HACKRF_SUCCESS)
	{
		std::stringstream message;
		message << "start_rx() failed: " << hackrf_error_name((hackrf_error)result) << "(" <<  result << ")" << std::endl;
		throw::runtime_error(__FILE__, __LINE__, __func__, message.str());
	}}

template <typename R>
void Radio_HACKRF<R>
::stop_rx()
{
	this->stop = true;
	this->buffer.stop = true;

	if(this->device != NULL)
  	{
		int result = hackrf_stop_rx(this->device);
		if (result != HACKRF_SUCCESS)
		{
			std::stringstream message;
			message << "stop_rx() failed: " << hackrf_error_name((hackrf_error)result) << "(" <<  result << ")" << std::endl;
			throw::runtime_error(__FILE__, __LINE__, __func__, message.str());
		}
	}
}

template <typename R>
void Radio_HACKRF<R>
::start_tx()
{
	int result = hackrf_start_tx(this->device, tx_callback, (void *)this);
	if (result != HACKRF_SUCCESS)
	{
		std::stringstream message;
		message << "start_tx() failed: " << hackrf_error_name((hackrf_error)result) << "(" <<  result << ")" << std::endl;
		throw::runtime_error(__FILE__, __LINE__, __func__, message.str());
	}}

template <typename R>
void Radio_HACKRF<R>
::stop_tx()
{
	std::cout<< "Ending..." << std::endl;
	this->stop = true;
	this->buffer.stop = true;

	if(this->device != NULL)
  	{
		int result = hackrf_stop_tx(this->device);
		if (result != HACKRF_SUCCESS)
		{
			std::stringstream message;
			message << "stop_tx() failed: " << hackrf_error_name((hackrf_error)result) << "(" <<  result << ")" << std::endl;
			throw::runtime_error(__FILE__, __LINE__, __func__, message.str());
		}
	}
}

template <typename R>
void Radio_HACKRF<R>
::_send(const R *X_N1, const int frame_id)
{
	this->buffer.push(X_N1, this->N*2);
}

template <typename R>
void Radio_HACKRF<R>
::_receive(R *Y_N1, const int frame_id)
{
	this->buffer.pull(Y_N1, this->N*2);
}

template <typename R>
void Radio_HACKRF<R>
::flush()
{
}

template <typename R>
void Radio_HACKRF<R>
::reset()
{
	this->flush();
	this->buffer.reset();
	this->stop = false;
}

template <typename R>
void Radio_HACKRF<R>
::send_cancel_signal()
{
}

template <typename R>
void Radio_HACKRF<R>
::wake_up()
{
}

template <typename R>
void Radio_HACKRF<R>
::cancel_waiting()
{
	this->send_cancel_signal();
	this->wake_up();
}

HACKRF_params
::HACKRF_params()
{
}

template <typename R>
int Radio_HACKRF<R>
::rx_callback(hackrf_transfer* transfer)
{
	Radio_HACKRF<R> *obj = (Radio_HACKRF<R>*) transfer->rx_ctx;

	if (obj->stop)
		return 0;

	obj->buffer.push((int8_t*)transfer->buffer, transfer->valid_length);
	return 0;
}

template <typename R>
int Radio_HACKRF<R>
::tx_callback(hackrf_transfer* transfer)
{
	Radio_HACKRF<R> *obj = (Radio_HACKRF<R>*) transfer->tx_ctx;
	if (obj->stop)
		return 0;

	obj->buffer.pull((int8_t*)transfer->buffer, transfer->valid_length);
	return 0;
}
// ==================================================================================== explicit template instantiation
//template class aff3ct::module::Radio_HACKRF<double>;
//template class aff3ct::module::Radio_HACKRF<float>;
//template class aff3ct::module::Radio_HACKRF<int16_t>;
template class aff3ct::module::Radio_HACKRF<int8_t>;
// ==================================================================================== explicit template instantiation

#endif