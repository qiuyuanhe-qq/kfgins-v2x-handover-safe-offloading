import argparse,csv,xml.etree.ElementTree as ET
from pathlib import Path
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--input",required=True); ap.add_argument("--output",required=True); a=ap.parse_args(); p=Path(a.output); p.parent.mkdir(parents=True,exist_ok=True); root=ET.parse(a.input).getroot();
 with p.open("w",newline="",encoding="utf-8") as f:
  w=csv.writer(f); w.writerow(["time","vehicle_id","x","y","speed","angle","lane_id"]);
  for ts in root.findall("timestep"):
   for v in ts.findall("vehicle"): w.writerow([ts.attrib.get("time",""),v.attrib.get("id",""),v.attrib.get("x",""),v.attrib.get("y",""),v.attrib.get("speed",""),v.attrib.get("angle",""),v.attrib.get("lane","")])
if __name__=="__main__": main()
