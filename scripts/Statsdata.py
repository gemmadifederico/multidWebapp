from pm4py.statistics.attributes.log.get import get_attribute_values
from copy import deepcopy
import numpy as np
from scipy.stats import norm
import statistics as stats

# Fitness of frequencies based on the normal distribution of freq
def get_freq_fitness(u, logBase, logComp):
    result = {}
    i = 0
    attr_list = get_attribute_values(logBase, attribute_key="concept:name")
    for trace in logComp:
        temp = dict.fromkeys(attr_list, None)
        i = i+1
        fitness = []
        for event in trace:
            cn = event.get("concept:name")
            if(cn in temp.keys()):
                if(temp[cn] is None): #First initialization
                    temp[cn] = 1
                else:
                    temp[cn] = temp[cn] +1 
        freqsum = deepcopy(temp)
        # now that I counted the occurences in this trace, I compare the values with the normal one
        # for each temp activity, I check the probability of the actual activity frequency to fit
        # in the normal distribution of the normal log, using the normal mean and stdev
        for key, value in temp.items():
            if(value is None):
                # I've never observed this activity in the log to compare (but I have it in the reference model as it comes from attr_list)
                # therefore the fitness is 0
                fitness.append(0)
            else: 
                # nAvg = u.get(avgtype).get(key)
                nAvg = u.get('Mean').get(key)
                # nMedian = u.get("Median").get(key)
                nStdev = u.get("StDev").get(key)
                nMin = u.get("Min").get(key)
                nMax = u.get("Max").get(key)
                #  worst case in which the value is < nMin or > nMax
                if value < nMin or value > nMax:
                    fitness.append(0)
                # optimum case where the stdev = 0 and avg = value, meaning that there is a perfect fit
                elif(nStdev == 0 and value == nAvg): 
                    fitness.append(1)
                else:
                    f = norm.pdf(value, loc = nAvg , scale = nStdev)
                    g = norm.pdf(nAvg, loc = nAvg , scale = nStdev)
                    fitness.append(round(f/g,5))
        
        for k in temp.keys():
            temp[k] = ""
        # trace index: trace.attributes.get("concept:name")
        result[trace.attributes.get("concept:name")] = fitness
    tot = {}
    for index, values in result.items():
        tot[index] = np.mean(values)
    return(freqsum, tot, np.mean(list(tot.values())))

def get_length_fitness(statsl, logTest):
    res = {}
    value = None
    for trace in logTest:
        value = len(trace)
        #  worst case in which the value is < nMin or > nMax
        if value < statsl.get("Min") or value > statsl.get("Max"):
            fitness = 0
        # optimum case where the stdev = 0 and avg = value, meaning that there is a perfect fit
        elif(statsl.get("StDev") == 0 and value == statsl.get("Mean")): 
            fitness = 1
        else:
            f = norm.pdf(value, loc = statsl.get("Mean") , scale = statsl.get("StDev"))
            g = norm.pdf(statsl.get("Mean"), loc = statsl.get("Mean") , scale = statsl.get("StDev"))
            fitness = round(f/g,5)
        res[trace.attributes.get("concept:name")] = fitness
    return(res, np.mean(list(res.values())), value)

def get_activity_freq_stats(log):
    """
    Get frequency statisics

    Parameters
    --------------
    log
        Log

    Returns
    --------------
    map
        "Sum" : fsum, "Mean": fmean, "Median": fmedian, "StDev": fstdev, "Min": fmin, "Max": fmax
    list
        Attrbute values
    """
    fr = freq_attributes(log)
    fmean = {}
    fmedian = {}
    fmin = {}
    fmax = {}
    fstdev = {}
    fsum = {}
    # Sum
    for key, value in fr.items():
        fsum[key] = sum(value)
    # Mean
    for key, value in fr.items():
        fmean[key] = stats.mean(value)
    # Median
    for key, value in fr.items():
        fmedian[key] = stats.median(value)
    # Min
    for key, value in fr.items():
        fmin[key] = min(value)
    # Max
    for key, value in fr.items():
        fmax[key] = max(value)
    # St Dev
    # If there is only one element, the st dev is 0
    for key, value in fr.items():
        if(len(value) == 1):
            fstdev[key] = 0
        else: fstdev[key] = stats.stdev(value)

    # print(f"Sum: {fsum}, \n Mean {fmean}, \n Median {fmedian}, \n StDev {fstdev}, \n Min {fmin}, \n Max {fmax}")
    attr_list = get_attribute_values(log, attribute_key="concept:name")
    return({"Sum" : fsum, "Mean": fmean, "Median": fmedian, "StDev": fstdev, "Min": fmin, "Max": fmax})
    # return(fsum, fmean, fmedian, fstdev, fmin, fmax)
    
def get_trace_length_stats(log):
    temp = []
    #pm4py.objects.log.util.index_attribute.insert_trace_index_as_event_attribute(log)
    for trace in log:
        temp.append(len(trace))
    stdev = 0
    if(len(temp) >1): stdev = stats.stdev(temp)

    return({"Mean": stats.mean(temp), "Median": stats.median(temp), "StDev": stdev, "Min": min(temp), "Max": max(temp)})

def freq_attributes(log):
    attr_list = get_attribute_values(log, attribute_key="concept:name")
    attr_list_freq = dict.fromkeys(attr_list, 0)
    temp = attr_list_freq
    i = 0
    for trace in log:
        temp = dict.fromkeys(temp, 0)
        i = i+1
        for event in trace:
            cn = event.get("concept:name")
            temp[cn] = temp[cn] +1 
        for a, value in attr_list_freq.items():
            if(value == 0): value = []
            value.append(temp[a])
            attr_list_freq[a] = value
    return attr_list_freq