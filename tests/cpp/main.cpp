#include <vector>

#include <aff3ct.hpp>

#include "Module/Filter/Filter_UPFIR/Filter_UPFIR.hpp"
#include "Module/Filter/Filter_FIR/Filter_FIR_ccr/Filter_FIR_ccr_fast.hpp"

using namespace aff3ct::module;

int main(int argc, char** argv)
{
    aff3ct::module::Source_random<> source(128);
    aff3ct::module::Modem_BPSK<>    modem (128);

    std::vector<float> h(8, 1.0f);
    aff3ct::module::Filter_UPFIR<float,  aff3ct::module::Filter_FIR_ccr_fast>  filter(128, h, 4);

    modem  [mdm::sck::modulate::X_N1].bind(source[src::sck::generate::U_K ]);
    filter [flt::sck::filter  ::X_N1].bind(modem [mdm::sck::modulate::X_N2]);
    
    source [src::tsk::generate].set_debug(true);
    modem  [mdm::tsk::modulate].set_debug(true);
    filter [flt::tsk::filter  ].set_debug(true);

    source [src::tsk::generate].exec();
    modem  [mdm::tsk::modulate].exec();
    filter [flt::tsk::filter  ].exec();
    return 0;
}