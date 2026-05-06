import argparse, json
from pathlib import Path
import pandas as pd
import numpy as np
from simulator import SimConfig, task_sample, estimate_rates, queue_delay, kfgins_sigma_projection, predicted_handover_time, decide, summarise, Z_90

def simulate_one(cfg, speed, sigma, seed, alg):
    rng=np.random.default_rng(seed*100000+int(speed*1000)+int(sigma*100)+abs(hash(alg))%10000)
    rows=[]
    for task_id in range(cfg.tasks_per_setting):
        lo,hi = cfg.boundary_distance_range_m if rng.random()<cfg.boundary_task_ratio else cfg.interior_distance_range_m
        d = rng.uniform(lo,hi)*cfg.cell_scale
        up,down,cycles,deadline,typ=task_sample(rng)
        ru,rd=estimate_rates(d,speed,sigma,rng,cfg)
        tq=queue_delay(rng,cfg)
        T_edge=up/ru+tq+cycles/cfg.edge_cpu_cycles_per_s+down/rd
        T_local=cycles/cfg.device_cpu_cycles_per_s
        mu=d+rng.normal(0,0.10*sigma)-speed*T_edge
        sig=kfgins_sigma_projection(speed,sigma,T_edge)
        tau=predicted_handover_time(d,speed,sigma,rng,cfg,alg)
        guard=cfg.ttt_s+cfg.handover_interruption_s
        vals=dict(T_edge=T_edge,T_local=T_local,deadline=deadline,mu_G=mu,sigma_G=sig,tau_HO_hat=tau,T_guard=guard,edge_energy=up/ru+down/rd,local_energy=T_local)
        off=decide(alg,vals,cfg)
        covrej=0
        if alg=='kfgins_risk':
            covrej=int((T_edge<=deadline) and (T_edge+guard<=tau) and (mu>=0) and not(mu-Z_90*sig>=0))
        if off:
            actual_uncertainty=rng.uniform(0,0.80*sigma)
            success=(T_edge<=deadline) and (d-speed*T_edge-actual_uncertainty>=0)
            latency=T_edge; reason='success' if success else 'handover_interruption'
        else:
            success=T_local<=deadline; latency=T_local; reason='success' if success else 'local_deadline_miss'
        rows.append(dict(task_id=task_id,algorithm=alg,speed=speed,sigma=sigma,seed=seed,distance_to_boundary=d,T_edge=T_edge,T_local=T_local,deadline=deadline,tau_HO_hat=tau,mu_G=mu,sigma_G=sig,margin=mu-Z_90*sig,decision='edge' if off else 'local',success=int(success),fail_reason=reason,latency=latency,eff_latency=latency if success else deadline+cfg.failed_latency_penalty_s,cov_reject=covrej,queue_delay=tq))
    return pd.DataFrame(rows)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--config',default='configs/sweep_trace.json'); ap.add_argument('--out',default='results/csv'); args=ap.parse_args()
    cfg=SimConfig.from_dict(json.loads(Path(args.config).read_text(encoding='utf-8-sig'))); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    summaries=[]; details=[]
    for sp in cfg.speeds_mps:
      for sg in cfg.gnss_sigma_m:
        for seed in cfg.seeds:
          for alg in cfg.algorithms:
            df=simulate_one(cfg,sp,sg,seed,alg); details.append(df); s=summarise(df); s.update(dict(algorithm=alg,speed=sp,sigma=sg,seed=seed)); summaries.append(s); print('done',alg,sp,sg,seed)
    pd.concat(details,ignore_index=True).to_csv(out/'task_detail.csv',index=False); pd.DataFrame(summaries).to_csv(out/'summary.csv',index=False)
if __name__=='__main__': main()
