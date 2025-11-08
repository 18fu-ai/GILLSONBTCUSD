#include "valorai/newt25.hpp"
#include <cmath>

namespace valorai {
namespace newt25 {

double induced_voltage(double area_m2, double dBdt_Ts) {
    // Faraday's law of induction: EMF = -dΦB/dt
    // For a uniform magnetic field perpendicular to the loop, ΦB = B * A
    // So, EMF = -A * dB/dt
    return -area_m2 * dBdt_Ts;
}

double risk_score(double V, double withstand) {
    // A simple sigmoid function to model failure probability.
    // The risk is 0.5 when the induced voltage equals the withstand voltage.
    // The steepness of the curve is determined by the constant '3'.
    if (withstand <= 0) {
        return 1.0; // Instant failure if withstand voltage is zero or negative.
    }
    return 1.0 / (1.0 + std::exp(-( (V / withstand) - 1.0) * 3.0));
}

} // namespace newt25
} // namespace valorai
