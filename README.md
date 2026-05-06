# kfgins-v2x-handover-safe-offloading

## 📦 About This Project
The released package contains a SUMO-trace-driven Python simulator, an OMNeT++ C++ prototype of the KF-GINS offloading controller, and a Simu5G-compatible link-trace logger for exporting uplink/downlink rate, MEC queue delay, estimated handover timing, and handover activity.

The full native binding of all Simu5G PHY/MAC/MEC signals is left as an extensible implementation path.

---
## 🛠️ Components
- `omnetpp_kfgins_fullstack`: OMNeT++ C++ prototype of the KF-GINS offloading controller
- `python_proxy`: SUMO-trace-driven Python simulator
- `simu5g_patch`: Simu5G-compatible link-trace logger
- `scripts`: Auxiliary scripts for data processing




# KF-GINS Handover-Safe V2X Edge Offloading

This repository provides a reproducible code package for the paper-oriented implementation of **KF-GINS-aided handover-safe task offloading for V2X edge communications**.

It contains three layers:

1. `python_proxy/`: SUMO-trace/proxy simulator for reproducible figures.
2. `omnetpp_kfgins_fullstack/`: OMNeT++ C++ prototype that reads `trajectory.csv` and `link_trace.csv`, computes `T_edge = T_up + T_q + T_exec + T_down`, and runs three policies.
3. `simu5g_patch/`: Simu5G `LinkTraceLogger` patch for generating a `link_trace.csv` bridge.

## Intended toolchain

- OMNeT++ 6.1.x
- INET 4.5.4
- Veins 5.3.1
- SUMO 1.22.0
- Simu5G 1.2.3
- Ubuntu 22.04 / WSL2 Ubuntu 22.04

## Quick start: Python proxy

```bash
cd python_proxy
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/run_sweep.py --config configs/sweep_trace.json --out results/csv
python src/plot_results.py --summary results/csv/summary.csv --out results/figs --sigma 12
python src/make_tables.py --summary results/csv/summary.csv --out results/tables
```

## Quick start: OMNeT++ prototype

Copy `omnetpp_kfgins_fullstack/` to `~/sim/kfgins_fullstack`, then:

```bash
cd ~/sim/kfgins_fullstack
source ~/sim/omnetpp-6.1/setenv
opp_makemake -f --deep -o kfgins_fullstack -O out -I src
make -j$(nproc)

cd simulations
rm -f results_*.csv results_task_log.csv
../out/gcc-release/kfgins_fullstack -u Cmdenv -n .:../src -f omnetpp.ini -c NearestRTT
mv results_task_log.csv results_nearest_rtt.csv
../out/gcc-release/kfgins_fullstack -u Cmdenv -n .:../src -f omnetpp.ini -c RiskNoCov
mv results_task_log.csv results_risk_no_cov.csv
../out/gcc-release/kfgins_fullstack -u Cmdenv -n .:../src -f omnetpp.ini -c KFGinsRisk
mv results_task_log.csv results_kfgins_risk.csv
python3 ../scripts/summarise_omnetpp_results.py --in . --out ../results
python3 ../scripts/plot_omnetpp_summary.py --summary ../results/omnetpp_summary.csv --out ../results
```

## Simu5G LinkTraceLogger patch

Copy files from `simu5g_patch/linkTraceLogger/` into Simu5G:

```bash
cd ~/sim/Simu5G-1.2.3
mkdir -p src/apps/linkTraceLogger
cp /path/to/LinkTraceLogger.h src/apps/linkTraceLogger/
cp /path/to/LinkTraceLogger.cc src/apps/linkTraceLogger/
cp /path/to/LinkTraceLogger.ned simulations/NR/networks/
```

Insert this submodule under `submodules:` in `simulations/NR/networks/SingleCell_Standalone.ned`:

```ned
logger: LinkTraceLogger {
    parameters:
        outputPath = "/home/qq/sim/kfgins_fullstack/data/link_trace.csv";
        interval = 1s;
}
```

Rebuild Simu5G:

```bash
source ~/sim/omnetpp-6.1/setenv
cd ~/sim/inet-4.5.4 && source setenv
cd ~/sim/Simu5G-1.2.3
rm -f src/Makefile
make makefiles
make -j$(nproc)
```

Run a Simu5G scenario to generate `link_trace.csv`:

```bash
mkdir -p ~/sim/kfgins_fullstack/data
rm -f ~/sim/kfgins_fullstack/data/link_trace.csv
cd ~/sim/Simu5G-1.2.3/simulations/NR/standalone
opp_run -u Cmdenv \
  -n .:../..:../../../src:/home/qq/sim/inet-4.5.4/src \
  -l /home/qq/sim/inet-4.5.4/src/libINET.so \
  -l /home/qq/sim/Simu5G-1.2.3/out/gcc-release/src/libsimu5g.so \
  -f omnetpp.ini \
  -c Standalone
```

## Scope note

The logger is a Simu5G-compatible bridge. It supports packet-counter-based throughput estimates and custom handover/MEC queue signals. For final full-stack validation, bind `uplink_mbps`, `downlink_mbps`, `next_ho_s`, `ho_active`, and `mec_queue_s` to the exact Simu5G modules/signals used in the target scenario.
