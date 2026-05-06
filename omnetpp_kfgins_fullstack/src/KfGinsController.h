#pragma once
#include <cmath>
struct KfGinsInput { double distanceToBoundary, speed, gnssSigma, tEdge, tLocal, deadline, tauHoHat, tGuard; };
struct KfGinsDecision { bool offload; double muG, sigmaG, margin; };
class KfGinsController {
 public:
  double z = 1.2815515655;
  KfGinsDecision decide(const KfGinsInput& in) const {
    double velocitySigma = 0.045 * in.speed + 0.20;
    double sigmaG = std::sqrt(std::pow(0.80*in.gnssSigma,2.0)+std::pow(velocitySigma*in.tEdge,2.0)+std::pow(1.5,2.0));
    double muG = in.distanceToBoundary - in.speed * in.tEdge;
    double margin = muG - z * sigmaG;
    bool ok = (in.tEdge <= in.deadline) && (in.tEdge + in.tGuard <= in.tauHoHat) && (margin >= 0.0);
    return {ok, muG, sigmaG, margin};
  }
};
