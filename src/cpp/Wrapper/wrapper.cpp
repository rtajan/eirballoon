#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/iostream.h>

#include <vector>

#include "Module/Filter/Filter.hpp"
#include "Module/Filter/Filter_FIR/Filter_FIR.hpp"
#include "Module/Filter/Filter_FIR/Filter_FIR_ccr/Filter_FIR_ccr.hpp"
#include "Module/Filter/Filter_FIR/Filter_FIR_ccr/Filter_FIR_ccr_fast.hpp"
#include "Module/Filter/Filter_FIR/Filter_FIR_ccr/Root_Raised_Cosine/Filter_root_raised_cosine.hpp"
#include "Module/Filter/Filter_FIR/Filter_FIR_ccr/Farrow/Filter_Farrow_quad.hpp"

#include "Module/Filter/Filter_UPFIR/Filter_UPFIR.hpp"

#include "Module/Synchronizer/Synchronizer_timing/Synchronizer_timing.hpp"
#include "Module/Synchronizer/Synchronizer_timing/Synchronizer_Gardner.hpp"

#include "Module/Radio/Radio.hpp"
#ifdef LINK_UHD
#include "Module/Radio/Radio_USRP/Radio_USRP.hpp"
#endif //LINK_UHD

namespace py = pybind11;
using namespace py::literals;
using namespace aff3ct;

PYBIND11_MODULE(eirballoon, m){
	// Split in two following https://pybind11.readthedocs.io/en/stable/advanced/misc.html#avoiding-c-types-in-docstrings
	// for enhancing python doc
	py::object py_aff3ct_module = (py::object) py::module_::import("py_aff3ct").attr("module").attr("Module");

	py::module_ m_filter = m.def_submodule("filter");

	py::class_<aff3ct::module::Filter<float>>(m_filter,"Filter", py_aff3ct_module)
		.def(py::init<const int, const int>(), "N"_a, "N_fil"_a);

	py::class_<aff3ct::module::Filter_FIR<float>, aff3ct::module::Filter<float>>(m_filter,"Filter_FIR")
		.def(py::init<const int, const std::vector<float>>(), "N"_a, "h"_a);
	
	py::class_<aff3ct::module::Filter_FIR_ccr<float>, aff3ct::module::Filter_FIR<float>>(m_filter,"Filter_FIR_ccr")
		.def(py::init<const int, const std::vector<float>>(), "N"_a, "h"_a);

	py::class_<aff3ct::module::Filter_FIR_ccr_fast<float>, aff3ct::module::Filter_FIR_ccr<float>>(m_filter,"Filter_FIR_ccr_fast")
		.def(py::init<const int, const std::vector<float>>(), "N"_a, "h"_a);

	py::class_<aff3ct::module::Filter_root_raised_cosine<float>, aff3ct::module::Filter_FIR_ccr_fast<float>>(m_filter,"Filter_root_raised_cosine")
		.def(py::init<const int,  const float, const int, const int>(), "N"_a, "rolloff"_a = 0.05, "samples_per_symbol"_a = 4, "delay_in_symbol"_a = 50)
		.def_static("synthetize", &aff3ct::module::Filter_root_raised_cosine<float>::synthetize);

	py::class_<aff3ct::module::Filter_UPFIR<float, aff3ct::module::Filter_FIR_ccr>, aff3ct::module::Filter<float>>(m_filter,"Filter_UPFIR")
		.def(py::init<const int, const std::vector<float>, const int>(), "N"_a, "h"_a, "osf"_a = 1);

	py::class_<aff3ct::module::Filter_Farrow_quad<float>, aff3ct::module::Filter_FIR_ccr_fast<float>>(m_filter,"Filter_Farrow_quad")
		.def(py::init<const int, const float>(), "N"_a, "mu"_a=0.0);

	py::module_ m_synchro = m.def_submodule("synchronizer");
	py::module_ m_synchro_timing = m_synchro.def_submodule("timing");

	py::class_<aff3ct::module::Synchronizer_timing<int, float>>(m_synchro_timing,"Synchronizer_timing",py_aff3ct_module);

	py::class_<aff3ct::module::Synchronizer_Gardner<int, float>, aff3ct::module::Synchronizer_timing<int, float>>(m_synchro_timing,"Synchronizer_Gardner")
		.def(py::init<const int, const int, const float, const float, const float>(), "N"_a, "osf"_a, "damping_factor"_a = 1.0, "normalized_bandwidth"_a = 0.01, "detector_gain"_a = 2.7);

	py::module_ m_radio = m.def_submodule("radio");
	py::class_<aff3ct::module::Radio<float>>(m_radio,"Radio",py_aff3ct_module);

	#ifdef LINK_UHD
	
	py::class_<aff3ct::module::USRP_params>(m_radio,"USRP_params")
	.def(py::init<>())
	.def_readwrite("N",              &aff3ct::module::USRP_params::N             )
	.def_readwrite("threaded",       &aff3ct::module::USRP_params::threaded      )
	.def_readwrite("fifo_size",      &aff3ct::module::USRP_params::fifo_size     )
	.def_readwrite("type",           &aff3ct::module::USRP_params::type          )
	.def_readwrite("usrp_addr",      &aff3ct::module::USRP_params::usrp_addr     )
	.def_readwrite("clk_rate",       &aff3ct::module::USRP_params::clk_rate      )
	.def_readwrite("rx_enabled",     &aff3ct::module::USRP_params::rx_enabled    )
	.def_readwrite("rx_rate",        &aff3ct::module::USRP_params::rx_rate       )
	.def_readwrite("rx_subdev_spec", &aff3ct::module::USRP_params::rx_subdev_spec)
	.def_readwrite("rx_antenna",     &aff3ct::module::USRP_params::rx_antenna    )
	.def_readwrite("rx_freq",        &aff3ct::module::USRP_params::rx_freq       )
	.def_readwrite("rx_gain",        &aff3ct::module::USRP_params::rx_gain       )
	.def_readwrite("rx_filepath",    &aff3ct::module::USRP_params::rx_filepath   )
	.def_readwrite("tx_enabled",     &aff3ct::module::USRP_params::tx_enabled    )	
	.def_readwrite("tx_rate",        &aff3ct::module::USRP_params::tx_rate       )
	.def_readwrite("tx_subdev_spec", &aff3ct::module::USRP_params::tx_subdev_spec)
	.def_readwrite("tx_antenna",     &aff3ct::module::USRP_params::tx_antenna    )
	.def_readwrite("tx_freq",        &aff3ct::module::USRP_params::tx_freq       )
	.def_readwrite("tx_gain",        &aff3ct::module::USRP_params::tx_gain       )	
	.def_readwrite("tx_filepath",    &aff3ct::module::USRP_params::tx_filepath   );

	py::class_<aff3ct::module::Radio_USRP<float>, aff3ct::module::Radio<float>>(m_radio,"Radio_USRP")
		.def(py::init<const aff3ct::module::USRP_params&>(), "params"_a, "USRP parameter object.");
	
	#endif //LINK_UHD
}