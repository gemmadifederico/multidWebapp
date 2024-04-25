from scripts.Statsdata import (get_activity_freq_stats, get_trace_length_stats)
from scripts.Mining import discovery_inductive
from subprocess import call
import os
from uuid import uuid4
from pandas import read_csv
from json import dump, dumps, load
from pm4py import format_dataframe, convert_to_event_log, write_xes

def execall(path_logA, path_discovered_model):
    df = read_csv(path_logA+".csv", sep=';', header=None)
    df.columns = ["case:concept:name", "concept:name", "time:timestamp"]
    df['start_timestamp'] = df.loc[:, 'time:timestamp']
    dataframe = format_dataframe(df, case_id='case:concept:name', activity_key='concept:name', timestamp_key='time:timestamp', start_timestamp_key="time:timestamp")    
    logA = convert_to_event_log(dataframe)
    write_xes(logA, path_logA+'.xes')

    uuidstr = str(uuid4())

    PATH = os.path.join(path_discovered_model, "Models")
    if not os.path.exists(PATH):
        os.makedirs(PATH)

    # Discovery using Inductive
    print("Discovering using Inductive...")
    filepath_ind = discovery_inductive(logA, uuidstr,PATH)
    
    print("Done")

    # Discovery of DCR
    # java -jar "dcr-discovery.jar" "path xes" "path JSON .JSON"
    print("Discovering of DCRgraph...")
    filepath_dcr = PATH+"\dcr_"+uuidstr+".JSON"
    filepath_dcr2 = PATH+"\dcr_"+uuidstr+".svg"
    call(['java', '-jar', 'scripts/dcr-discovery.jar', path_logA+".xes", filepath_dcr])
    call(['java', '-cp', 'scripts/dcr-printmodel.jar', 'beamline.miners.dcr.DCR2SVG', filepath_dcr, filepath_dcr2])
    print("Done")
    
    # Discovery of freq stats
    print("Discovering frequency stats...")
    fstats = get_activity_freq_stats(logA)
    print("Done")

    # Discovery of traces length stats
    print("Discovering trace length stats...")
    lenstats = get_trace_length_stats(logA)
    # writeTable(lenstats, "Trace length", f)
    print("Done")
    
    a = []
    entry = {"UUID": uuidstr,"Ind": filepath_ind, "DCR":filepath_dcr, "DCR2":filepath_dcr2,"Freq":fstats, "Len":lenstats}
    if not os.path.isfile(PATH + "/AllModels.json"):
        a.append(entry)
        with open(PATH + "/AllModels.json", mode='w') as f:
            f.write(dumps(a, indent=2))
    else:
        with open(PATH + "/AllModels.json") as feedsjson:
            feeds = load(feedsjson)

        feeds.append(entry)
        with open(PATH + "/AllModels.json", mode='w') as f:
            f.write(dumps(feeds, indent=2))
    
    dicovered_models = open(PATH + "/Models.json", "w")
    jsondict = {"UUID": uuidstr,"Ind": filepath_ind, "DCR":filepath_dcr, "DCR2":filepath_dcr2, "Freq":fstats, "Len":lenstats}
    dump(jsondict, dicovered_models)
    dicovered_models.close()