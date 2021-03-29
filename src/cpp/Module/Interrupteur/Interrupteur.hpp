/*!
 * \file
 * \brief Interrupteurs a signal.
 *
 * \section LICENSE
 * This file is under MIT license (https://opensource.org/licenses/MIT).
 */
#ifndef INTERRUPTEUR_HPP_
#define INTERRUPTEUR_HPP_

#include <vector>

#include "Module/Module.hpp"
#include "Tools/Interface/Interface_reset.hpp"

namespace aff3ct
{
namespace module
{
	namespace itr
	{
		enum class tsk : size_t { select, SIZE };

		namespace sck
		{
			enum class select : size_t { X_N, bln, Y_N, status };
		}
	}

/*!
 * \class Interrupteur
 *
 * \brief Interrupteurs a signal.
 *
 * \tparam R: type of the reals (floating-point representation) of the Interrupteuring process.
 *
 * Please use Interrupteur for inheritance (instead of Interrupteur)
 */
template <typename B = int, typename R = float>
class Interrupteur : public Module
{
public:
	inline Task&   operator[](const itr::tsk                 t) { return Module::operator[]((int)t);                        }
	inline Socket& operator[](const itr::sck::select         s) { return Module::operator[]((int)itr::tsk::select)[(int)s]; }

protected:
	const int N;     /*!< Size of one frame (= number of samples in one frame) */

public:
	/*!
	 * \brief Constructor.
	 *
	 * \param N:        size of one frame (= number of samples in one frame).
	 */
	Interrupteur(const int N);

	void init_processes();

	/*!
	 * \brief Destructor.
	 */
	virtual ~Interrupteur() = default;

	int get_N() const;

	virtual Interrupteur<B,R>* clone() const;
protected:
	virtual void _select(const R *X_N,const B *bln ,  R *Y_N, const int frame_id);
};
}
}

#endif /* INTERRUPTEUR_HPP */
