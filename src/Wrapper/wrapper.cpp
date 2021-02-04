#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <vector>

#include "Module/Filter/Filter.hpp"
#include "Module/Filter/Filter_FIR/Filter_FIR.hpp"
#include "Module/Filter/Filter_FIR/Filter_FIR_ccr/Filter_FIR_ccr.hpp"
#include "Module/Filter/Filter_FIR/Filter_FIR_ccr/Filter_FIR_ccr_fast.hpp"
#include "Module/Filter/Filter_FIR/Filter_FIR_ccr/Root_Raised_Cosine/Filter_root_raised_cosine.hpp"

#include "Module/Filter/Filter_UPFIR/Filter_UPFIR.hpp"

namespace py = pybind11;
using namespace py::literals;
using namespace aff3ct;

PYBIND11_MODULE(eirballoon, m){
	// Split in two following https://pybind11.readthedocs.io/en/stable/advanced/misc.html#avoiding-c-types-in-docstrings
	// for enhancing python doc
	py::object py_aff3ct_module = (py::object) py::module_::import("py_aff3ct").attr("module").attr("Module");
	
	py::module_ m_filter = m.def_submodule("filter");

	py::class_<aff3ct::module::Filter<float>>(m_filter,"Filter",py_aff3ct_module)
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

}