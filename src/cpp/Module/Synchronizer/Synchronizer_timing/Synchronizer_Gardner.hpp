#ifndef SYNCHRONIZER_GARDNER_HPP
#define SYNCHRONIZER_GARDNER_HPP

#include <vector>
#include <mutex>
#include <complex>

#include "Module/Synchronizer/Synchronizer_timing/Synchronizer_timing.hpp"
#include "Module/Filter/Filter_FIR/Filter_FIR_ccr/Farrow/Filter_Farrow_quad.hpp"

namespace aff3ct
{
namespace module
{
template <typename B = int, typename R = float>
class Synchronizer_Gardner : public Synchronizer_timing<B,R>
{
private:
	const std::vector<int>  set_bits_nbr = {0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4, 1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5, 1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7, 1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7, 3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7, 4, 5, 5, 6, 5, 6, 6, 7, 5, 6, 6, 7, 6, 7, 7, 8};

	// Interpolation filter
	Filter_Farrow_quad <R>   farrow_flt;

	// TED parameters
	int strobe_history;
	R TED_error;
	std::vector<std::complex<R> > TED_buffer;
	int TED_head_pos;
	int TED_mid_pos;

	// Loop filter parameters
	R lf_proportional_gain;
	R lf_integrator_gain;
	R lf_prev_in;
	R lf_filter_state;
	R lf_output;

	R NCO_counter;

	std::mutex buffer_mtx;

public:
	Synchronizer_Gardner (const int N, int osf, const R damping_factor = (R)1.0, const R normalized_bandwidth = (R)0.01, const R detector_gain = (R)2.7);
	virtual ~Synchronizer_Gardner();

	inline void step(const std::complex<R> *X_N1, R* MU, std::complex<R>* Y_N1, B* B_N1);

	void set_loop_filter_coeffs(const R damping_factor,
	                            const R normalized_bandwidth,
	                            const R detector_gain        );

protected:
	void _reset();
	void _synchronize(const R *X_N1, R* MU, R *Y_N1, B *B_N1, const int frame_id);

	inline void TED_update(std::complex<R> strobe);
	inline void loop_filter();
	inline void interpolation_control();
};

}
}

#include "Module/Synchronizer/Synchronizer_timing/Synchronizer_Gardner.hxx"

#endif //SYNCHRONIZER_GARDNER_HPP
