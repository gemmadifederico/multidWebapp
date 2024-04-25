from datetime import datetime
from scripts import Discovery as dis
from scripts import Conformance as conf
import json
import pandas as pd
from flask import Flask, render_template, redirect
from scripts.Mining import get_aligned_traces

app = Flask(__name__, static_folder="static/Models")


@app.route("/")
def home():
    return render_template(
        "home.html"
    )
@app.route("/conf")
def homeconf():
    return render_template(
        "homeconf.html"
    )

@app.route('/discovery')
def discovery():
    dis.execall("../log", "static")
    return redirect("/visdiscovery")


@app.route('/visdiscovery')
def visdiscovery():
    f = open("static/Models/Models.json")
    log = json.load(f)
    f.close()
    id = log['UUID']
    dcrpath = "dcr_"+id+".svg"
    pnpath = "ind_"+id+".png"
    freq = log["Freq"]
    len = log["Len"]
    listofact = freq.get("Sum").keys()
    
    return render_template(
        "discovery.html",
        dcrpath=dcrpath,
        pnpath=pnpath,
        freq=freq,
        len=len,
        listofact=listofact
        )
    
@app.route('/conformance')
def conformance():
    conf.execall("../log", 
                 "static/Models/",
                 1,
                 "1")
    return redirect("/visconformance")
    
@app.route('/visconformance')
def visconformance():

    df = pd.read_csv("static/Results.csv")
    wind = 1
    wdcr = 1
    wfreq = 1
    wlen = 1
    wdf = 0.5
    wcf = 0.5
    
    lastres = df[-1:]
    ccind = lastres.get("CCInd").item()
    ccdcr = lastres.get("CCDcr").item()
    ccfreq = lastres.get("CCFreq").item()
    cclen = lastres.get("CCLen").item()
    cccf = lastres.get("CCCf").item()
    ccdf = lastres.get("CCDf").item()
    fitness = lastres.get("Fitness").item()

    # cccf = ((ccind*wind)+(ccdcr*wdcr))/(wind+wdcr)
    # ccdf = ((ccfreq*wfreq)+(cclen*wlen))/(wfreq+wlen)
    # fitness = ((cccf*wcf)+(ccdf*wdf))/(wcf+wdf)
    
    f = open("static/Models/Models.json")
    log = json.load(f)
    f.close()
    id = log['UUID']
    dcrpath = "dcr_"+id+".svg"
    pnpath = "ind_"+id+".png"
    freq = log["Freq"]
    len = log["Len"]
    listofact = freq.get("Sum").keys()
        
    aligned_traces = get_aligned_traces("static/Models/ind_"+id, "../logconf.xes")
    top = [str(t[0])[:3] for t in aligned_traces]
    bottom = [str(t[1])[:3] for t in aligned_traces]
    
    f = open("static/confres.json")
    data = json.load(f)
    f.close()
    
    return render_template(
        "conformance.html",
        df = df,
        ccind = ccind,
        ccdcr = ccdcr,
        fitness = fitness,
        pnpath=pnpath,
        freq=freq,
        len=len,
        listofact = listofact,
        fresum = data[0],
        lentrace = data[1],
        cccf = cccf,
        ccdf = ccdf,
        labels = list(df["Id"]),
        fits = list(df["Fitness"]),
        ccfreq=ccfreq,
        cclen=cclen,
        aligned_traces = aligned_traces,
        top=top,
        bottom=bottom
    )
    
    #python -m flask run