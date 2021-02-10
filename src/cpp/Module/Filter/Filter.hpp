/*!
 * \file
 * \brief Filters a signal.
 *
 * \section LICENSE
 * This file is under MIT license (https://opensource.org/licenses/MIT).
 */
#ifndef FILTER_HPP_
#define FILTER_HPP_

#include <vector>

#include "Module/Module.hpp"
#include "Tools/Interface/Interface_reset.hpp"

namespace aff3ct
{
namespace module
{
	namespace flt
	{
		enum class tsk : size_t { filter, SIZE };

		namespace sck
		{
			enum class filter : size_t { X_N1, Y_N2, status };
		}
	}

/*!
 * \class Filter
 *
 * \brief Filters a signal.
 *
 * \tparam R: type of the reals (floating-point representation) of the filtering process.
 *
 * Please use Filter for inheritance (instead of Filter)
 */
template <typename R = float>
class Filter : public Module, public tools::Interface_reset
{
public:
	inline Task&   operator[](const flt::tsk                 t) { return Module::operator[]((int)t);                        }
	inline Socket& operator[](const flt::sck::filter         s) { return Module::operator[]((int)flt::tsk::filter)[(int)s]; }

protected:
	const int N;     /*!< Size of one frame (= number of samples in one frame) */
	const int N_fil; /*!< Number of samples after the filtering process */

public:
	/*!
	 * \brief Constructor.
	 *
	 * \param N:        size of one frame (= number of samples in one frame).
	 * \param N_fil:    number of samples after the filtering process.
	 */
	Filter(const int N, const int N_fil);

	void init_processes();

	/*!
	 * \brief Destructor.
	 */
	virtual ~Filter() = default;

	int get_N() const;

	int get_N_fil() const;

	virtual void reset();
	/*!
	 * \brief Filters a vector of samples.
	 *
	 * By default this method does nothing.
	 *
	 * \param X_N1: a vector of samples.
	 * \param Y_N2: a filtered vector.
	 */
	template <class AR = std::allocator<R>>
	void filter(const std::vector<R,AR>& X_N1, std::vector<R,AR>& Y_N2, const int frame_id = -1, const bool managed_memory = true);

	void filter(const R *X_N1, R *Y_N2, const int frame_id = -1, const bool managed_memory = true);

	virtual void step  (const R *X_elt, R *Y_elt);

	virtual Filter<R>* clone() const;
protected:
	virtual void _filter(const R *X_N1,  R *Y_N2, const int frame_id);
	virtual void _reset ();
};
}
}

#endif /* FILTER_HPP_ */
