from pm4py.objects.log.importer.xes import importer as xes_importer
from scripts.Statsdata import (get_freq_fitness, get_length_fitness)
from scripts.Mining import conformance_pt
from subprocess import call
from csv import writer
from os import path
from json import load, dumps
import pandas as pd
from pm4py import format_dataframe, convert_to_event_log, write_xes
from sys import argv

def execall(path_logA, path_models, case, exp_name):
    # Test log, base log, models path
    # Opening JSON file
    with open(path_models+"Models.json") as json_file:
        discovered_models = load(json_file)
        
    df = pd.read_csv(path_logA+".csv", sep=';', header=None)
    df.columns = ["case:concept:name", "concept:name", "time:timestamp"]
    # df['start_timestamp'] = df.loc[:, 'time:timestamp']
        
    lastcid = df["case:concept:name"][-1:]

    logA = xes_importer.apply(path_logA+".xes")

    logBdf = df.loc[df["case:concept:name"] == int(lastcid)]
    logBdf = format_dataframe(logBdf, case_id='case:concept:name', activity_key='concept:name', timestamp_key='time:timestamp', start_timestamp_key="time:timestamp")    
    logB = convert_to_event_log(logBdf)
    write_xes(logB, path_logA+'conf.xes')
    
    res = pd.DataFrame()

    # Conformance checking (alignment) from Inductive
    print("Conformance checking from Inductive...")
    ccind_traces, ccind, precind = conformance_pt(discovered_models["Ind"], logB)
    res = res.assign(ccind = ccind_traces.loc[:,"fitness"])
    print("Done")

    # Conformance checking of DCR
    # java -jar "dcr-conformance.jar" "path model .JSON" "path logB" open world flag
    print("Conformance of DCR...")
    call(['java', '-jar', 'scripts/dcr-conformance.jar', discovered_models["DCR"], path_logA+"conf.xes", "FALSE"])
    
    # The total fitness value is saved in the file dcrcc.txt
    f = open("C:/Users/gdfe/OneDrive - Danmarks Tekniske Universitet/Dokumenter/ResearchEvaluation/Webapp/scripts/dcrcc.txt", "r")
    for line in f:
        ccdcr = float(line)
    f.close()
    print("Done")

    # Conformance of frequency
    print("Conformance of frequency...")
    freqsum, ccfreq_t, ccfreq = get_freq_fitness(discovered_models["Freq"], logA, logB)
    ccfreq_traces = pd.DataFrame(ccfreq_t.items(), columns=["id", "fitness"])
    res = res.assign(ccfreq = ccfreq_traces.loc[:,"fitness"])
    # ccfreq_traces.to_csv(PATH+"/accepted_traces_freq_"+uuid+".csv")
    print("Done")

    # Get fitness of trace length
    print("Trace length comparison...")
    cclen_t, cclen, lentrace = get_length_fitness(discovered_models["Len"], logB)
    cclen_traces = pd.DataFrame(data=cclen_t.items(),columns=["id", "fitness"])
    res = res.assign(cclen = cclen_traces.loc[:,"fitness"])
    print("Done")

    res.index += 1 
    
    lasttrace = logB[-1]
    cid = lasttrace.attributes.get("concept:name")

    wind = 1
    wdcr = 1
    wfreq = 1
    wlen = 1
    wdf = 0.5
    wcf = 0.5
    cccf = ((ccind*wind)+(ccdcr*wdcr))/(wind+wdcr)
    ccdf = ((ccfreq*wfreq)+(cclen*wlen))/(wfreq+wlen)
    fitness = ((cccf*wcf)+(ccdf*wdf))/(wcf+wdf)
    
    header = ["Case", "Conf", "logA", "logB", "CCInd", "PrecInd", "CCDcr", "CCFreq", "CCLen", "CCCf", "CCDf", "Fitness", "Id"]
    values = [case, '\"'+exp_name+'\"', path_logA, path_logA+"conf", ccind, precind, ccdcr, ccfreq, cclen, cccf, ccdf, fitness, cid]
    print("Writing the results...")
    # open the file in the write mode

    c = [freqsum, lentrace]
    with open("static/confres.json", mode='w') as f:
        f.write(dumps(c, indent=2))

    # Create File
    if not path.exists('static/Results.csv'):
        print("Creating file...")
        with open('static/Results.csv', 'w', newline="") as f:
            writercsv = writer(f)
            writercsv.writerow(header)
            writercsv.writerow(values)
            print("Done")
    else:
        with open('static/Results.csv', 'a', newline="") as f:
            writercsv = writer(f)
            writercsv.writerow(values)
            print("Done")

if __name__ == "__main__":
    A = argv[1]
    C = argv[3]
    D = argv[4]
    E = argv[5]
    execall(A,C,D,E)
    print("####################")
    print("TASKS COMPLETED")
    print("####################")