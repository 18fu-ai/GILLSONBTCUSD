#include <iostream>
#include <cassert>
#include <cmath>
#include "valorai/newt25.hpp"

// A simple function to check for near-equality of floating-point numbers
void check_near(double a, double b, double epsilon = 1e-9) {
    assert(std::abs(a - b) < epsilon);
}

int main() {
    std::cout << "Running NEWT25 tests..." << std::endl;

    // Test case 1: Test induced_voltage
    double area = 0.5; // m^2
    double dBdt = 2.0; // T/s
    double expected_voltage = -1.0;
    double actual_voltage = valorai::newt25::induced_voltage(area, dBdt);
    check_near(actual_voltage, expected_voltage);
    std::cout << "[PASS] induced_voltage calculation is correct." << std::endl;

    // Test case 2: Test risk_score - induced voltage equals withstand voltage
    double voltage1 = 5.0;
    double withstand1 = 5.0;
    double expected_risk1 = 0.5;
    double actual_risk1 = valorai::newt25::risk_score(voltage1, withstand1);
    check_near(actual_risk1, expected_risk1);
    std::cout << "[PASS] risk_score at 50% threshold is correct." << std::endl;

    // Test case 3: Test risk_score - induced voltage is much lower than withstand
    double voltage2 = 1.0;
    double withstand2 = 10.0;
    double actual_risk2 = valorai::newt25::risk_score(voltage2, withstand2);
    assert(actual_risk2 < 0.5); // Should be a low risk
    std::cout << "[PASS] risk_score for low voltage is correctly low." << std::endl;

    // Test case 4: Test risk_score - induced voltage is much higher than withstand
    double voltage3 = 10.0;
    double withstand3 = 1.0;
    double actual_risk3 = valorai::newt25::risk_score(voltage3, withstand3);
    assert(actual_risk3 > 0.9); // Should be a very high risk
    std::cout << "[PASS] risk_score for high voltage is correctly high." << std::endl;

    std::cout << "All NEWT25 tests passed!" << std::endl;

    return 0;
}
