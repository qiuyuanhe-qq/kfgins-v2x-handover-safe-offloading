from pathlib import Path
import argparse,pandas as pd,matplotlib.pyplot as plt

def main():
 p=argparse.ArgumentParser(); p.add_argument("--summary",default="results/csv/summary.csv"); p.add_argument("--out",default="results/figs"); p.add_argument("--sigma",type=float,default=12.0); a=p.parse_args(); out=Path(a.out); out.mkdir(parents=True,exist_ok=True); df=pd.read_csv(a.summary); df=df[df.sigma.eq(a.sigma)]
 labels={"nearest_rtt":"Nearest-RTT","expected_cost":"Expected-cost","risk_no_cov":"Risk-aware (no cov)","kfgins_risk":"KF-GINS risk-aware"}
 metrics=[("success_ratio","Task success ratio","Fig3a_success_ratio_vs_speed.png"),("wasted_offloading_ratio","Wasted offloading ratio","Fig3b_wasted_offloading_vs_speed.png"),("p95_effective_latency","Effective p95 latency (s)","Fig4_effective_p95_latency_vs_speed.png"),("handover_failure_ratio","Handover-induced failure ratio","Fig5_handover_failure_vs_speed.png")]
 g=df.groupby(["algorithm","speed"]).mean(numeric_only=True).reset_index();
 for m,y,f in metrics:
  plt.figure(figsize=(3.45,2.55));
  for alg,lab in labels.items():
   d=g[g.algorithm.eq(alg)].sort_values("speed"); plt.plot(d.speed,d[m],marker="o",label=lab)
  plt.xlabel("Speed (m/s)"); plt.ylabel(y); plt.grid(True,ls=":"); plt.legend(fontsize=7); plt.tight_layout(); plt.savefig(out/f,dpi=600); plt.close()
 d=g[g.algorithm.eq("kfgins_risk")].sort_values("speed"); plt.figure(figsize=(3.45,2.55)); plt.plot(d.speed,d.cov_reject_ratio,marker="o",label="KF-GINS risk-aware"); plt.xlabel("Speed (m/s)"); plt.ylabel("Covariance rejection ratio"); plt.grid(True,ls=":"); plt.legend(fontsize=7); plt.tight_layout(); plt.savefig(out/"Fig6_covariance_rejection_vs_speed.png",dpi=600)
if __name__=="__main__": main()
