#include <cassert>
#include <iostream>
#include <sstream>
#include <vector>
#include <mutex>
#include <numeric>
#include <cmath>
#include <thread>
#include <condition_variable>
#include <time.h>
#include "Ring_Buffer.hpp"

Ring_Buffer
::Ring_Buffer(int size)
:stop(false),buffer(size,int8_t(0)), w_idx(0), r_idx(0), size(size)
{
	assert(size > 0);
}

Ring_Buffer
::~Ring_Buffer()
{
}

void Ring_Buffer
::reset()
{
	this->w_idx = 0;
	this->r_idx = 0;
	std::fill(this->buffer.begin(), this->buffer.end(), 0);
	this->stop = false;
}


void Ring_Buffer
::pull (int8_t* data, const uint32_t sz)
{
	uint16_t* data_ptr = reinterpret_cast<uint16_t*>(data);
	uint32_t sz_2 = sz/2;
	uint32_t n_item = 0;
	while(n_item < sz_2 && !this->stop)
	{
		int b = pull(data_ptr + n_item);
		n_item += b;
		if (b==0)
			nanosleep((const struct timespec[]){{0,10}}, NULL);
	}
}

int Ring_Buffer
::pull (uint16_t* byte)
{
	uint32_t r = this->r_idx.load();

	if (this->w_idx.load() == r)
		return 0;

	*byte = this->buffer[r];
	r = r+1;
	r = r >= size? r - size:r;
	this->r_idx = r;
	return 1;
}

void Ring_Buffer
::push (const int8_t* data, const uint32_t sz)
{
	const uint16_t* data_ptr = reinterpret_cast<const uint16_t*>(data);
	uint32_t sz_2 = sz/2;
	uint32_t n_item = 0;
	while(n_item < sz_2 && !this->stop)
	{
		int b = push(data_ptr + n_item);
		n_item += b;
		if (b==0)
			nanosleep((const struct timespec[]){{0,10}}, NULL);
	}

}

int Ring_Buffer
::push(const uint16_t* byte)
{
	uint32_t w = this->w_idx.load();
	uint32_t next_w = w+1;
	next_w = next_w >= size ? next_w - size:next_w;

	if ( next_w == this->r_idx.load())
		return 0;

	this->buffer[w] = *byte;
	this->w_idx = next_w;
	return 1;
}

void Ring_Buffer
::print()
{
	std::stringstream msg;

    msg << "---------------------------------------" << "\n";
	msg << "Thread ID : "<< std::this_thread::get_id() << "\n";
	msg << "Reader number : "<< this->r_idx << "\n";
	msg << "Writer number : "<< this->w_idx << "\n";
	msg << "---------------------------------------" << "\n";
	std::cout << msg.str();
}