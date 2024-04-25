from pm4py import discover_process_tree_inductive, write_ptml, convert_to_bpmn, read_ptml, write_bpmn
from pm4py.visualization.bpmn import visualizer as bpmn_visualizer
from pm4py.algo.conformance.alignments.process_tree import algorithm as alignmentspt
from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
from pm4py.objects.log.importer.xes import importer as xes_importer

def discovery_inductive(log, uuidstr, path):
    filename = path+"/ind_"+uuidstr    
    ptree = discover_process_tree_inductive(log)
    write_ptml(ptree, filename+".ptml")    
    bpmn = convert_to_bpmn(ptree)
    gviz = bpmn_visualizer.apply(bpmn)
    bpmn_visualizer.save(gviz, filename+".png")
    write_bpmn(bpmn, filename)
    return filename


def conformance_pt (model, logB):
    ptree = read_ptml(model+".ptml")
    aligned_traces = alignmentspt.apply(logB, ptree)
    x = 0
    for trace in aligned_traces:
        x =  x + trace["fitness"]

    aligned_traces_dataframe = alignments.get_diagnostics_dataframe(logB, aligned_traces)
    fit = x/len(logB)
    prec = 0
    return aligned_traces_dataframe, fit, prec

def get_aligned_traces(model,logB):
    log = xes_importer.apply(logB)
    ptree = read_ptml(model+".ptml")
    aligned_traces = alignmentspt.apply(log, ptree)
    res = aligned_traces[0].get("alignment")
    return res