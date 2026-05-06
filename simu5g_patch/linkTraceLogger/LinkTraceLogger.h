#pragma once
#include <omnetpp.h>
#include <fstream>
#include <string>
#include <set>
using namespace omnetpp;
class LinkTraceLogger : public cSimpleModule, public cListener {
 private:
  cMessage *timer=nullptr; std::ofstream out; std::string outputPath; double interval=1.0; long ulBytes=0, dlBytes=0; bool hoActive=false; double currentNextHoS=2.0, currentMecQueueS=0.12; std::set<simsignal_t> ulSignals, dlSignals, hoStartSignals, hoEndSignals; simsignal_t kfginsHoStartSig,kfginsHoEndSig,kfginsNextHoSig,kfginsMecQueueDelaySig;
 protected:
  virtual void initialize() override; virtual void handleMessage(cMessage *msg) override; virtual void finish() override; virtual void receiveSignal(cComponent *source,simsignal_t signalID,cObject *obj,cObject *details) override; virtual void receiveSignal(cComponent *source,simsignal_t signalID,long value,cObject *details) override; virtual void receiveSignal(cComponent *source,simsignal_t signalID,double value,cObject *details) override; void subscribeRecursively(cModule *module); void writeHeader(); void writeRow();
};
