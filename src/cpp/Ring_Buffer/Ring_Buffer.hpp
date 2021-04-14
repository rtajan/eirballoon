#ifndef Ring_Buffer_HPP_
#define Ring_Buffer_HPP_

#include <vector>
#include <atomic>

class Ring_Buffer
{
public:
	bool stop;

protected:
	std::vector<int16_t> buffer;

	std::atomic<uint32_t> w_idx;
	std::atomic<uint32_t> r_idx;

	uint32_t size;

public:
	Ring_Buffer (int size);

	virtual ~Ring_Buffer();

	//inline int get_cur_buffer_nbr() const
	//{
	//	return (int)this->head_buffer - (int)this->tail_buffer + ((this->tail_buffer > this->head_buffer)?(int)//this->cb_size:0);
	//};
	//int get_max_read_buf_sz () {return this->max_read_buf_sz;}
	//int get_max_write_buf_sz () {return this->max_write_buf_sz;}
	void reset();

	void pull (      int8_t* data, const uint32_t sz);
	void push (const int8_t* data, const uint32_t sz);
	int  pull (      uint16_t* byte);
	int  push (const uint16_t* byte);
	void print();

	//inline bool is_empty() const {return this->get_cur_buffer_nbr() == 0;                   };
};

#endif //Ring_Buffer_HPP_
