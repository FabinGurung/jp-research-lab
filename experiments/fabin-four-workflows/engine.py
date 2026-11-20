#!/usr/bin/env python3
"""Small synthetic four-workflow demonstrator. No SQL or project evidence imports."""
from __future__ import annotations
import argparse, csv, hashlib, io, json, math, os, re, subprocess
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PARAMETERS = [
    ("span_x",4,"m","Grid A–B, column centrelines"),
    ("span_y",4,"m","Grid 1–2, column centrelines"),
    ("column_height",3,"m","Base to idealized roof joint; QTO to slab soffit"),
    ("column_width",.30,"m","Square column"),
    ("beam_width",.25,"m","All four perimeter beams"),
    ("beam_depth",.45,"m","Total depth including slab"),
    ("slab_thickness",.15,"m","One two-way panel"),
    ("concrete_density",25,"kN/m3","Synthetic normal-weight concrete"),
    ("elastic_modulus",25000000,"kN/m2","Synthetic linear-elastic stiffness"),
    ("finish_load",1,"kN/m2","Illustrative superimposed dead load"),
    ("live_load",2,"kN/m2","Illustrative gravity load; no occupancy/code claim"),
    ("concrete_rate",12000,"NPR/m3","Illustrative concrete only; excludes rebar/formwork"),
    ("column_output",.60,"m3/crew-day","Synthetic productivity for column preparation"),
    ("formwork_output",6,"m2/crew-day","Synthetic roof formwork productivity"),
    ("rebar_output",8,"m2/crew-day","Synthetic roof preparation duration; not steel quantity"),
    ("pour_output",3,"m3/crew-day","Synthetic concrete placing productivity"),
    ("skilled_workers",2,"people","One sequential crew"),
    ("helpers",3,"people","One sequential crew"),
    ("shift_hours",8,"hours/day","Productivities correspond to an 8-hour crew day"),
    ("column_cure",7,"calendar-days","Illustrative wait only; not stripping/strength approval"),
    ("slab_cure",14,"calendar-days","Illustrative wait only; not stripping/strength approval"),
    ("start_date","2026-11-22","ISO-date","Synthetic planning origin, Asia/Kathmandu"),
    ("saturday_off",True,"boolean","Sunday–Friday working calendar"),
    ("steel_rate",None,"NPR/kg","Unresolved; no steel design/BBS"),
    ("formwork_rate",None,"NPR/m2","Unresolved; excluded from concrete subtotal"),
    ("latitude",None,"degrees","Unresolved; no surveyed or GIS location"),
    ("longitude",None,"degrees","Unresolved; no surveyed or GIS location"),
]
UNITS = {k:u for k,v,u,n in PARAMETERS}

def canonical(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False)

def digest(x):
    return hashlib.sha256(canonical(x).encode()).hexdigest()

def parse_rows(rows):
    if not rows or rows[0][:4] != ["Parameter","Value","Unit","Basis"]:
        raise ValueError("Inputs A1:D1 must be Parameter | Value | Unit | Basis")
    out={}
    for row in rows[1:]:
        if not row or not row[0]:
            continue
        key=row[0]
        if key not in UNITS or key in out:
            raise ValueError("Unknown or duplicate parameter: "+str(key))
        if len(row)<3 or row[2]!=UNITS[key]:
            raise ValueError("Unit mismatch: "+key)
        value=row[1] if len(row)>1 and row[1]!="" else None
        if key=="saturday_off" and isinstance(value,str):
            if value.upper() not in ("TRUE","FALSE"):
                raise ValueError("saturday_off must be TRUE or FALSE")
            value=value.upper()=="TRUE"
        elif key!="start_date" and key!="saturday_off" and value is not None:
            if isinstance(value,bool): raise ValueError("Boolean supplied for numeric input")
            value=float(value)
        out[key]=value
    if set(out)!=set(UNITS):
        raise ValueError("Missing input rows: "+", ".join(set(UNITS)-set(out)))
    validate(out)
    return out

def validate(p):
    for k in UNITS:
        if k not in p: raise ValueError("Missing parameter "+k)
    nullable={"steel_rate","formwork_rate","latitude","longitude"}
    nonnegative={"finish_load","live_load"}
    for k in set(p)-nullable-{"start_date","saturday_off"}:
        v=p[k]
        if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):
            raise ValueError("Finite numeric input required: "+k)
        if v<0 or (v==0 and k not in nonnegative): raise ValueError("Invalid input "+k)
    for k in nullable:
        if p[k] is not None and (isinstance(p[k],bool) or not isinstance(p[k],(int,float)) or not math.isfinite(p[k])):
            raise ValueError("Invalid nullable input "+k)
    for k in ("steel_rate","formwork_rate"):
        if p[k] is not None and p[k]<0: raise ValueError("Negative unit rate")
    if p["latitude"] is not None and not -90<=p["latitude"]<=90: raise ValueError("Latitude outside range")
    if p["longitude"] is not None and not -180<=p["longitude"]<=180: raise ValueError("Longitude outside range")
    for k in ("skilled_workers","helpers","column_cure","slab_cure"):
        if p[k]!=int(p[k]): raise ValueError("Integer required: "+k)
    if not isinstance(p["saturday_off"],bool): raise ValueError("Boolean required")
    if not 0<p["shift_hours"]<=16: raise ValueError("Shift must be 0–16 hours")
    for L in (p["span_x"],p["span_y"]):
        if L<=2*p["column_width"] or L>20: raise ValueError("Span outside demonstrator scope")
    if p["beam_width"]>p["column_width"]: raise ValueError("Beam must fit within column for QTO exclusion")
    if p["beam_depth"]<=p["slab_thickness"]: raise ValueError("Beam depth must exceed slab thickness")
    if max(p["span_x"],p["span_y"])/min(p["span_x"],p["span_y"])>2:
        raise ValueError("45-degree two-way slab demo requires aspect ratio <= 2")
    date.fromisoformat(p["start_date"])

def mdm(L,h,E,Ib,Ic,F):
    """Two roof joints, one beam, fixed bases, no sidesway. Clockwise I/J moments."""
    kb=4*E*Ib/L; kc=4*E*Ic/h
    dfb=kb/(kb+kc); dfc=kc/(kb+kc)
    mb=[-F,F]; mt=[0.,0.]; base=[0.,0.]; history=[]
    for sweep in range(1,201):
        for j in (0,1):
            unbalanced=mb[j]+mt[j]
            db=-unbalanced*dfb; dc=-unbalanced*dfc
            mb[j]+=db; mt[j]+=dc; mb[1-j]+=.5*db; base[j]+=.5*dc
            history.append({"sweep":sweep,"joint":j+1,"unbalanced_kNm":unbalanced,
                "beam_distribution":dfb,"column_distribution":dfc,
                "beam_correction_kNm":db,"column_correction_kNm":dc,
                "beam_carry_over_kNm":db/2,"base_carry_over_kNm":dc/2,
                "beam_I_kNm":mb[0],"beam_J_kNm":mb[1],
                "column_top_I_kNm":mt[0],"column_top_J_kNm":mt[1]})
        if max(abs(mb[j]+mt[j]) for j in (0,1))<1e-10: break
    else: raise ValueError("Moment distribution did not converge")
    # Independent closed-form slope-deflection, opposite end rotations by symmetry.
    exact=F*kc/(kc+kb/2)
    if max(abs(abs(m)-exact) for m in mb)>1e-8: raise ValueError("MDM/slope-deflection mismatch")
    return {"beam_I_kNm":mb[0],"beam_J_kNm":mb[1],"column_top_kNm":mt,
        "column_base_kNm":base,"joint_residual_kNm":max(abs(mb[j]+mt[j]) for j in (0,1)),
        "independent_hogging_kNm":exact,"iterations":sweep,"history":history}

def simpson(fn,L,n=400):
    dx=L/n
    return dx/3*(fn(0)+fn(L)+sum((4 if i%2 else 2)*fn(i*dx) for i in range(1,n)))

def section(L,other,p):
    q=p["slab_thickness"]*p["concrete_density"]+p["finish_load"]+p["live_load"]
    depth=p["beam_depth"]-p["slab_thickness"]
    clear=L-p["column_width"]
    V=clear*p["beam_width"]*depth
    w=V*p["concrete_density"]/L
    # Area of one 45-degree edge tributary polygon, including rectangular panels.
    m=min(L,other)
    area=m*L/2-m*m/4
    load=lambda x:q*min(x,L-x,other/2)+w
    # Fixed-end moment from the beam interpolation function (independent integration).
    F=simpson(lambda x:load(x)*x*(L-x)**2/L**2,L)
    I_b=p["beam_width"]*p["beam_depth"]**3/12
    I_c=p["column_width"]**4/12
    moments=mdm(L,p["column_height"],p["elastic_modulus"],I_b,I_c,F)
    R=(q*area+w*L)/2
    mid=-moments["independent_hogging_kNm"]+R*L/2-simpson(lambda x:load(x)*(L/2-x),L/2)
    return {"span_m":L,"clear_length_m":clear,"tributary_area_m2":area,
        "slab_load_kPa":q,"beam_downstand_m3":V,"beam_selfweight_kN_per_m":w,
        "roof_load_kN":q*area+w*L,"reaction_kN":R,"fixed_end_magnitude_kNm":F,
        "midspan_sagging_kNm":mid,**moments}

def compute(p):
    validate(p)
    X,Y,H=p["span_x"],p["span_y"],p["column_height"]
    xy=[(0,0),(X,0),(X,Y),(0,Y)]
    columns=[{"id":f"C{i+1}","grid":["A1","B1","B2","A2"][i],"x":x,"y":y,
        "z0":0,"z1":H,"width":p["column_width"]} for i,(x,y) in enumerate(xy)]
    xres=section(X,Y,p); yres=section(Y,X,p)
    beams=[{"id":f"B{i+1}","start_column":f"C{i+1}","end_column":f"C{(i+1)%4+1}",
        "axis":"X" if i%2==0 else "Y","result":xres if i%2==0 else yres} for i in range(4)]
    slab=X*Y*p["slab_thickness"]
    beamsV=2*(xres["beam_downstand_m3"]+yres["beam_downstand_m3"])
    columnsV=4*p["column_width"]**2*H
    roof=2*(xres["roof_load_kN"]+yres["roof_load_kN"])
    total=roof+columnsV*p["concrete_density"]
    reaction=total/4
    if abs(2*(xres["tributary_area_m2"]+yres["tributary_area_m2"])-X*Y)>1e-8:
        raise ValueError("Slab tributary areas do not reconcile")
    qto=[{"element":"Columns C1–C4","quantity":columnsV,"unit":"m3"},
         {"element":"Beams B1–B4, downstands only","quantity":beamsV,"unit":"m3"},
         {"element":"Slab S1","quantity":slab,"unit":"m3"}]
    for q in qto: q.update(rate=p["concrete_rate"],amount=q["quantity"]*p["concrete_rate"])
    return {"schema":"fabin.four-workflows.v1","scope":"SYNTHETIC_RESEARCH_EXPERIMENT",
        "parameters":p,"input_sha256":digest(p),"columns":columns,"beams":beams,
        "slab":{"id":"S1","corners":["C1","C2","C3","C4"],"area_m2":X*Y},
        "quantities":qto,"concrete_m3":sum(q["quantity"] for q in qto),
        "concrete_subtotal_npr":sum(q["amount"] for q in qto),
        "analysis":{"method":"Moment distribution; two orthogonal no-sway portal frames",
            "load_transfer":"45-degree two-way tributary polygons; triangular/trapezoidal beam loads",
            "load_case":"Unfactored symmetric gravity","roof_load_kN":roof,"total_load_kN":total,
            "base_reaction_each_kN":reaction,"vertical_residual_kN":4*reaction-total,
            "x":xres,"y":yres},
        "excluded":{"steel_quantity_kg":None,"steel_amount_npr":None,"formwork_amount_npr":None,
            "foundations":None,"seismic_design":None,"GIS_survey":None},
        "engineering_approval":False,"remote_peer_repositories_modified":False}

def make_schedule(p,r):
    # Active work uses a Saturday-off workweek; curing waits use calendar time.
    factor=8/p["shift_hours"]
    tasks=[("A01","Set out",1,"work",["C1","C2","C3","C4"]),
        ("A02","Column preparation",math.ceil(r["quantities"][0]["quantity"]/p["column_output"]*factor),"work",["C1","C2","C3","C4"]),
        ("A03","Column casting",math.ceil(r["quantities"][0]["quantity"]/p["pour_output"]*factor),"work",["C1","C2","C3","C4"]),
        ("A04","Column curing wait",int(p["column_cure"]),"calendar",["C1","C2","C3","C4"]),
        ("A05","Beam and slab formwork",math.ceil(r["slab"]["area_m2"]/p["formwork_output"]*factor),"work",["B1","B2","B3","B4","S1"]),
        ("A06","Roof reinforcement preparation",math.ceil(r["slab"]["area_m2"]/p["rebar_output"]*factor),"work",["B1","B2","B3","B4","S1"]),
        ("A07","Beam and slab casting",math.ceil(sum(x["quantity"] for x in r["quantities"][1:])/p["pour_output"]*factor),"work",["B1","B2","B3","B4","S1"]),
        ("A08","Slab curing wait",int(p["slab_cure"]),"calendar",["S1"]),
        ("A09","Review before prop removal",1,"work",["B1","B2","B3","B4","S1"])]
    current=date.fromisoformat(p["start_date"]); origin=current
    activities=[]
    def workday(d): return not (p["saturday_off"] and d.weekday()==5)
    for i,(key,name,duration,kind,els) in enumerate(tasks):
        if kind=="work":
            while not workday(current): current+=timedelta(days=1)
        start=current
        remaining=duration
        while remaining:
            if kind=="calendar" or workday(current): remaining-=1
            current+=timedelta(days=1)
        activities.append({"id":key,"name":name,"duration":(current-start).days,
            "active_duration":duration,"duration_basis":kind,"predecessor":tasks[i-1][0] if i else None,
            "start":start.isoformat(),"finish":(current-timedelta(days=1)).isoformat() if duration else current.isoformat(),
            "es":(start-origin).days,"ef":(current-origin).days,"elements":els})
    r["schedule"]={"activities":activities,"elapsed_days":(current-origin).days,
        "origin_date":origin.isoformat(),"finish_date":(current-timedelta(days=1)).isoformat(),
        "crew":{"skilled":p["skilled_workers"],"helpers":p["helpers"],"hours":p["shift_hours"]},
        "basis":"Sequential single crew; work excludes Saturdays, curing uses calendar days",
        "native_kernel_verified":False}
    return r

def native_schedule(r,kernel_dir):
    # Feed elapsed spans and start constraints to the pinned existing CPM engine.
    # This preserves Saturday gaps and calendar-day curing rather than mislabelling curing work slots.
    acts=r["schedule"]["activities"]
    net={"activities":[{"id":a["id"],"name":a["name"],"duration":a["duration"]} for a in acts],
        "relationships":[{"predecessor":a["predecessor"],"successor":a["id"],"type":"FS","lag":0} for a in acts if a["predecessor"]],
        "constraints":[{"activity_id":a["id"],"type":"START_ON_OR_AFTER","slot":a["es"]} for a in acts]}
    bridge=ROOT/"native-cpm.mjs"
    proc=subprocess.run(["node",str(bridge),str(kernel_dir)],input=json.dumps(net),capture_output=True,text=True,check=True)
    solved=json.loads(proc.stdout)
    got={a["id"]:a for a in solved["activities"]}
    for a in acts:
        b=got[a["id"]]
        if b["es"]!=a["es"] or b["ef"]!=a["ef"]: raise ValueError("Native CPM calendar mismatch")
        a.update(total_float=b["total_float"],critical=b["critical"],ls=b["ls"],lf=b["lf"])
    r["schedule"]["native_kernel_verified"]=True
    r["schedule"]["native_project"]=solved["project"]
    return r

def csv_write(path,rows):
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def export(r,out):
    out.mkdir(parents=True,exist_ok=True)
    (out/"results.json").write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n")
    csv_write(out/"quantities.csv",r["quantities"])
    for direction in ("x","y"): csv_write(out/f"moment-distribution-{direction}.csv",r["analysis"][direction]["history"])
    csv_write(out/"schedule.csv",[{k:v for k,v in a.items() if k!="elements"} for a in r["schedule"]["activities"]])

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path);ap.add_argument("--out",type=Path,required=True);ap.add_argument("--kernel-dir",type=Path)
    a=ap.parse_args(); p=json.loads(a.input.read_text()) if a.input else {k:v for k,v,u,n in PARAMETERS}
    r=make_schedule(p,compute(p))
    if a.kernel_dir: r=native_schedule(r,a.kernel_dir)
    export(r,a.out)
    print(json.dumps({"concrete_m3":r["concrete_m3"],"concrete_subtotal_npr":r["concrete_subtotal_npr"],
        "gravity_kN":r["analysis"]["total_load_kN"],"schedule_finish":r["schedule"]["finish_date"],
        "native_cpm":r["schedule"]["native_kernel_verified"]}))

if __name__=="__main__":main()
