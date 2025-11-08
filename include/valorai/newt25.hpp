#pragma once

namespace valorai {
namespace newt25 {

/**
 * @brief Calculates the induced voltage in a loop due to a changing magnetic field.
 *
 * This function models the electromagnetic pulse (EMP) or electromagnetic interference (EMI) effect
 * on a conceptual circuit loop based on Faraday's law of induction.
 *
 * @param area_m2 The area of the loop in square meters.
 * @param dBdt_Ts The rate of change of the magnetic field in Teslas per second.
 * @return The induced voltage in Volts.
 */
double induced_voltage(double area_m2, double dBdt_Ts);

/**
 * @brief Calculates a risk score based on the induced voltage and a component's withstand voltage.
 *
 * The risk score is a value between 0.0 and 1.0, calculated using a sigmoid function.
 * A score close to 1.0 indicates a high probability of failure.
 *
 * @param V The induced voltage in Volts.
 * @param withstand The maximum voltage the component can withstand in Volts.
 * @return The calculated risk score (0.0 to 1.0).
 */
double risk_score(double V, double withstand);

} // namespace newt25
} // namespace valorai
