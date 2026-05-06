import math
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List

Z_90 = 1.2815515655446004

@dataclass
class SimConfig:
    speeds_mps: List[float]
    gnss_sigma_m: List[float]
    seeds: List[int]
    tasks_per_setting: int
    boundary_task_ratio: float
    cell_scale: float
    queue_load: float
    slot_s: float
    a3_hysteresis_db: float
    ttt_s: float
    handover_interruption_s: float
    risk_epsilon: float
    edge_cpu_cycles_per_s: float
    device_cpu_cycles_per_s: float
    base_uplink_MBps: float
    base_downlink_MBps: float
    boundary_distance_range_m: List[float]
    interior_distance_range_m: List[float]
    failed_latency_penalty_s: float
    algorithms: List[str]
    @staticmethod
    def from_dict(d: Dict):
        return SimConfig(**d)

def task_sample(rng):
    r = rng.random()
    if r < 0.30:
        up, down, cycles, deadline, typ = 0.35, 0.05, 0.65e9, 0.55, 'short'
    elif r < 0.80:
        up, down, cycles, deadline, typ = 1.15, 0.15, 1.75e9, 0.88, 'perception'
    else:
        up, down, cycles, deadline, typ = 1.85, 0.20, 3.05e9, 1.20, 'analytics'
    scale = rng.lognormal(mean=0.0, sigma=0.08)
    return up*scale, down*scale, cycles*scale, deadline, typ

def estimate_rates(distance_m, speed, sigma, rng, cfg):
    boundary_factor = 0.55 + 0.45 * np.clip(distance_m/80.0, 0.0, 1.0)
    mobility_factor = 1.0/(1.0+0.010*speed)
    uncertainty_factor = 1.0/(1.0+0.010*sigma)
    fading = rng.lognormal(mean=0.0, sigma=0.07)
    return max(cfg.base_uplink_MBps*boundary_factor*mobility_factor*uncertainty_factor*fading, 1.0), max(cfg.base_downlink_MBps*boundary_factor*mobility_factor*uncertainty_factor*fading, 1.5)

def queue_delay(rng, cfg):
    rho = np.clip(cfg.queue_load, 0.10, 0.92)
    return 0.035 + 0.18*rho + rng.gamma(shape=2.0, scale=0.020+0.035*rho)

def kfgins_sigma_projection(speed, sigma, T_edge):
    velocity_sigma = 0.045*speed + 0.20
    map_sigma = 1.5
    return math.sqrt((0.80*sigma)**2 + (velocity_sigma*T_edge)**2 + map_sigma**2)

def predicted_handover_time(distance_m, speed, sigma, rng, cfg, algorithm):
    a3_offset = 10.0 + 0.20*sigma
    pred_err = rng.normal(0.0, 0.08*sigma + 0.8)
    return max(0.0, distance_m-a3_offset+pred_err)/max(speed,0.1) + cfg.ttt_s

def decide(algorithm, values, cfg):
    T_edge, T_local, deadline = values['T_edge'], values['T_local'], values['deadline']
    mu_G, sigma_G = values['mu_G'], values['sigma_G']
    tau_HO_hat, T_guard = values['tau_HO_hat'], values['T_guard']
    edge_energy, local_energy = values['edge_energy'], values['local_energy']
    if algorithm == 'nearest_rtt':
        return (T_edge < T_local) and (T_edge <= deadline)
    if algorithm == 'expected_cost':
        return (T_edge + 0.12*edge_energy < T_local + 0.12*local_energy) and (T_edge <= deadline)
    if algorithm == 'risk_no_cov':
        return (T_edge <= deadline) and (T_edge + T_guard <= tau_HO_hat) and (mu_G >= 0.0)
    if algorithm == 'kfgins_risk':
        return (T_edge <= deadline) and (T_edge + T_guard <= tau_HO_hat) and (mu_G - Z_90*sigma_G >= 0.0)
    raise ValueError(algorithm)

def summarise(df):
    off = df['decision'].eq('edge')
    off_failed = off & df['success'].eq(0)
    off_success = off & df['success'].eq(1)
    success_lat = df.loc[df['success'].eq(1), 'latency']
    return {
        'num_tasks': len(df),
        'success_ratio': df['success'].mean(),
        'wasted_offloading_ratio': off_failed.sum()/max(off.sum(),1),
        'handover_failure_ratio': df['fail_reason'].eq('handover_interruption').mean(),
        'offload_precision': off_success.sum()/max(off.sum(),1),
        'p95_success_latency': float(np.percentile(success_lat,95)) if len(success_lat) else float('nan'),
        'p95_effective_latency': float(np.percentile(df['eff_latency'],95)),
        'offload_attempt_ratio': off.mean(),
        'cov_reject_ratio': df['cov_reject'].mean(),
        'mean_queue_delay': df['queue_delay'].mean(),
        'mean_margin': df['margin'].mean(),
    }
