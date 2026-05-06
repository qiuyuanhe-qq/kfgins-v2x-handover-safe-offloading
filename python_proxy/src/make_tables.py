import argparse,pandas as pd
from pathlib import Path
def main():
 p=argparse.ArgumentParser(); p.add_argument("--summary",default="results/csv/summary.csv"); p.add_argument("--out",default="results/tables"); p.add_argument("--speed",type=float,default=25); p.add_argument("--sigma",type=float,default=12); a=p.parse_args(); out=Path(a.out); out.mkdir(parents=True,exist_ok=True); df=pd.read_csv(a.summary); hard=df[df.speed.eq(a.speed)&df.sigma.eq(a.sigma)]; tab=hard.groupby("algorithm").mean(numeric_only=True).reset_index(); tab.to_csv(out/"hardest_setting_summary.csv",index=False); print(tab.round(3))
if __name__=="__main__": main()
