#pragma once
#include <omnetpp.h>
#include <vector>
#include <string>
using namespace omnetpp;
struct TraceRow { double time; std::string vehicleId; double x; double y; double speed; };
struct LinkTraceRow { double time; std::string vehicleId; double uplinkMbps; double downlinkMbps; double mecQueueS; double nextHoS; int hoActive; };
class V2XTaskApp : public cSimpleModule {
 private:
  cMessage *timer = nullptr; int taskId = 0; int traceIndex = 0; int linkIndex = 0;
  std::vector<TraceRow> traceRows; std::vector<LinkTraceRow> linkRows;
  void loadTrace(const std::string& path); void loadLinkTrace(const std::string& path); const LinkTraceRow& nextLinkRow(); double distanceToCellBoundary(double x,double y,double cellSize);
 protected:
  virtual void initialize() override; virtual void handleMessage(cMessage *msg) override; virtual void finish() override;
};
