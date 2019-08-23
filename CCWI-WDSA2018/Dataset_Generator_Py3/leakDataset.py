# -*- coding: utf-8 -*-
from __future__ import print_function
import multiprocessing
from demandGenerator import genDem
import wntr
import numpy as np
import pickle
import os
import shutil
#import csv
import pandas
import time
#import sys

benchmark = os.getcwd()[:-17]+'Benchmarks\\'
try:
    os.makedirs(benchmark)
except:
    pass 

# demand-driven (DD) or pressure dependent demand (PDD) 
Mode_Simulation = 'PDD'#'PDD'#'PDD'

# Leak types
leak_time_profile = ["abrupt", "incipient"]
sim_step_minutes = 30

# Set duration in hours
durationHours = 24*365 # One Year
timeStamp = pandas.date_range("2018-01-01 00:00", "2018-12-31 23:55", freq=str(sim_step_minutes)+"min")

#timeStamp = pandas.date_range("2017-12-01 00:00", "2017-12-30 23:55", freq="24h")
#timeStamp = pandas.date_range("00:00", "23:55", freq="5min")
#timeStamp = pandas.date_range("2017-12-30 00:00", "2017-12-31 23:55", freq="24h")

labelScenarios = []
uncertainty_Topology = 'NO'
INP = "Net1"  

# RUN SCENARIOS
def runScenarios(scNum):

    #itsok = False
    #while itsok != True:
        #try:
    qunc = np.arange(0, 0.25 ,0.05)
        
    # Path of EPANET Input File
    #INPUT_FILES = ["Net1_CMH","Hanoi_CMH"]
    #INPUT_FILES = ["Net1_CMH","Net2_CMH","Net3_CMH","Anytown_CMH","Hanoi_CMH","ky2_CMH","ky3_CMH"]
    #for INP in INPUT_FILES:
    print(["Run input file: ", INP])
    inp_file = 'networks/'+INP+'.inp'    
    
    print("Scenarios: "+str(scNum))
    
    wn = wntr.network.WaterNetworkModel(inp_file)
    inp = os.path.basename(wn.name)[0:-4]
    netName = benchmark+ inp#+'2'
    # Create folder with network name
    if scNum==1:
        try:
            if os.path.exists(netName):
                shutil.rmtree(netName)
            os.makedirs(netName)
            shutil.copyfile(inp_file, netName+'\\'+os.path.basename(wn.name))
        except:
            pass 
    
    ## Energy pattern remove
    #wn.energy.global_pattern = '""'
    # Set time parameters
    wn.options.time.duration = durationHours*3600
    wn.options.time.hydraulic_timestep = 60*sim_step_minutes
    wn.options.time.quality_timestep = 0
    wn.options.time.report_timestep = 60*sim_step_minutes
    wn.options.time.pattern_timestep = 60*sim_step_minutes
    
    results = {}
    # Set random seed
    f=open('wn.pickle','wb')
    pickle.dump(wn,f)
    f.close()
    
    # Create fodler scenarios
    # Number of leaks at the same junction in day
    LEAK_LIST_TANK_JUNCTIONS = wn.junction_name_list+wn.tank_name_list
    
    if scNum == 1:
        nmLeaksNode = 0
    else:
        nmLeaksNode = int(round(np.random.uniform(0,2)))#leak off =0
    
    qunc_index = int(round(np.random.uniform(len(qunc)-1)))
    uncertainty_Length = qunc[qunc_index]
    
    qunc_index = int(round(np.random.uniform(len(qunc)-1)))
    uncertainty_Diameter = qunc[qunc_index]
    
    qunc_index = int(round(np.random.uniform(len(qunc)-1)))
    uncertainty_Roughness = qunc[qunc_index]
    
    qunc_index = int(round(np.random.uniform(len(qunc)-1)))
    uncertainty_base_demand = qunc[qunc_index]
    
    # CREATE FOLDER EVERY SCENARIO-I
    labels = np.zeros(len(timeStamp))#.astype(int)
    Sc = netName+'\\Scenario-'+str(scNum)
    if os.path.exists(Sc):
        shutil.rmtree(Sc)
    os.makedirs(Sc)
    
    ###########################################################################  
    ## SET BASE DEMANDS AND PATTERNS      
    # Remove all patterns
    #        # Initial base demands SET ALL EQUAL 1
    #if "ky" in INP:
    wn._patterns= {}
    tempbase_demand = wn.query_node_attribute('base_demand')
    tempbase_demand = np.array([tempbase_demand[i] for i, line in enumerate(tempbase_demand)])
    
    tmp = list(map(lambda x: x * uncertainty_base_demand, tempbase_demand))
    ql=tempbase_demand-tmp
    qu=tempbase_demand+tmp
    mtempbase_demand=len(tempbase_demand)
    qext_mtempbase_demand=ql+np.random.rand(mtempbase_demand)*(qu-ql)
    
    for w, junction in enumerate(wn.junction_name_list):
        wn.get_node(junction).demand_timeseries_list[0].base_value = qext_mtempbase_demand[w] #wn.query_node_attribute('base_demand')
        pattern_name = 'P_'+junction
        patts = genDem()
        wn.add_pattern(pattern_name, patts)
        wn.get_node(junction).demand_pattern_name = pattern_name
    
    ###########################################################################
    ## SET UNCERTAINTY PARAMETER
    # Uncertainty Length
    tempLengths = wn.query_link_attribute('length')
    tempLengths = np.array([tempLengths[i] for i, line in enumerate(tempLengths)])
    tmp = list(map(lambda x: x * uncertainty_Length, tempLengths))
    ql=tempLengths-tmp
    qu=tempLengths+tmp
    mlength=len(tempLengths)
    qext=ql+np.random.rand(mlength)*(qu-ql)
        
    # Uncertainty Diameter
    tempDiameters = wn.query_link_attribute('diameter')
    tempDiameters = np.array([tempDiameters[i] for i, line in enumerate(tempDiameters)])
    tmp = list(map(lambda x: x * uncertainty_Diameter, tempDiameters))
    ql=tempDiameters-tmp
    qu=tempDiameters+tmp
    dem_diameter=len(tempDiameters)
    diameters=ql+np.random.rand(dem_diameter)*(qu-ql)
        
    # Uncertainty Roughness
    tempRoughness = wn.query_link_attribute('roughness')
    tempRoughness = np.array([tempRoughness[i] for i, line in enumerate(tempRoughness)])
    tmp = list(map(lambda x: x * uncertainty_Roughness, tempRoughness))
    ql=tempRoughness-tmp
    qu=tempRoughness+tmp
    dem_roughness=len(tempRoughness)
    qextR=ql+np.random.rand(dem_roughness)*(qu-ql)
    for w, line1 in enumerate(qextR):
        wn.get_link(wn.link_name_list[w]).roughness=line1
        wn.get_link(wn.link_name_list[w]).length=qext[w]
        wn.get_link(wn.link_name_list[w]).diameter=diameters[w]
        
    ###########################################################################    
    
    ## ADD A LEAK NODE 
    
    # Add leak node with 2 starttime end time
    leak_node = {}
    leak_diameter = {}
    leak_area = {}
    leak_type = {}
    time_of_failure = {}
    end_of_failure = {}
    leakStarts = {}
    leakEnds = {}
    leak_peak_time = {}
    i = int(round(np.random.uniform(wn.num_junctions+wn.num_tanks-1)))
    
    for leak_i in range(nmLeaksNode):
        
        i = int(round(np.random.uniform(wn.num_junctions+wn.num_tanks-1)))
        # Start Time of leak
        leak_node[leak_i] = wn.get_node(LEAK_LIST_TANK_JUNCTIONS[i])
    
        if leak_i>0:
            if leak_node[leak_i] == leak_node[leak_i-1]:
                time_of_failure[leak_i] = int(np.round(np.random.uniform(time_of_failure[leak_i-1],len(timeStamp))))
            else:
                time_of_failure[leak_i] = int(np.round(np.random.uniform(1,len(timeStamp))))
        else:
            time_of_failure[leak_i] = int(np.round(np.random.uniform(1,len(timeStamp))))
    
        # End Time of leak
        end_of_failure[leak_i] = len(timeStamp)#int(np.round(np.random.uniform(time_of_failure[leak_i],len(timeStamp))))
        
        
        # Labels for leak
        labels[time_of_failure[leak_i]:end_of_failure[leak_i]]=1
        leak_type[leak_i] = leak_time_profile[int(round(np.random.uniform(0,1)))]
        ST = time_of_failure[leak_i] 
        ET = end_of_failure[leak_i]
        MT = int(np.round(np.random.uniform(ST+1,ET)))
        if leak_type[leak_i] == 'incipient':
            maxHole = np.random.uniform(0.02, 0.2)
            increment = maxHole/(MT-ST) 
            leak_step_increment = np.arange(0, maxHole , increment)
            leak_step = 0
            while leak_step < MT-ST:
                step = leak_i#'Leak_'+str(leak_i)+'_step_'+str(leak_step)
                leak_diameter[step] = leak_step_increment[leak_step]
                leak_area[step]=3.14159*(leak_diameter[step]/2)**2 # na mpei sto leakArea excel file mono gia to maxHole
                leak_node[step] = wn.get_node(LEAK_LIST_TANK_JUNCTIONS[i])
                leak_start_time = (ST+leak_step)*sim_step_minutes*60
                leak_end_time =  len(timeStamp)#6(ST+leak_step+1)*sim_step_minutes*60
                leak_node[step]._leak_end_control_name=str(leak_i)+'end'+str(ST+leak_step)
                leak_node[step]._leak_start_control_name = str(leak_i)+'start'+str(ST+leak_step)
                leak_node[step].add_leak(wn, area = leak_area[step],
                                  start_time = leak_start_time,
                                  end_time = leak_end_time)
        
                leakStarts[step] = timeStamp[ST]
                leakStarts[step] = leakStarts[step]._date_repr + ' ' +leakStarts[step]._time_repr
                leakEnds[step] = timeStamp[end_of_failure[leak_i]-1]
                leakEnds[step] = leakEnds[step]._date_repr + ' ' +leakEnds[step]._time_repr
                leak_peak_time[leak_i] = timeStamp[MT-1]._date_repr+' '+timeStamp[MT-1]._time_repr

                leak_step = leak_step + 1
        else:     # abrupt  
            MT = ET
            leak_diameter[leak_i] = np.random.uniform(0.02, 0.2)
            leak_area[leak_i]=3.14159*(leak_diameter[leak_i]/2)**2
            leak_start_time = ST*sim_step_minutes*60
            leak_end_time = len(timeStamp)#ET*sim_step_minutes*60
            leak_node[leak_i]._leak_end_control_name=str(leak_i)+'end'
            leak_node[leak_i]._leak_start_control_name = str(leak_i)+'start'
            leak_node[leak_i].add_leak(wn, area = leak_area[leak_i],
                              start_time = leak_start_time,
                              end_time = leak_end_time)
            #if leak_type[leak_i] == 'abrupt':
            leakStarts[leak_i] = timeStamp[ST-1]
            leakStarts[leak_i] = leakStarts[leak_i]._date_repr + ' ' +leakStarts[leak_i]._time_repr
            leakEnds[leak_i] = timeStamp[ET-1]
            leakEnds[leak_i] = leakEnds[leak_i]._date_repr + ' ' +leakEnds[leak_i]._time_repr
            leak_peak_time[leak_i] = timeStamp[MT-1]._date_repr+' '+timeStamp[MT-1]._time_repr

        
    ## SAVE EPANET INPUT FILE 
    # Write inp file
    wn.write_inpfile(Sc+'\\'+inp+'_Scenario-'+str(scNum)+'.inp')
    
    ## RUN SIMULATION WITH WNTR SIMULATOR
    sim = wntr.sim.WNTRSimulator(wn, mode=Mode_Simulation)
    results = sim.run_sim()
    if ((all(results.node['pressure']> 0)) !=True)==True:
        print("not run")
        scNum = scNum + 1
        return -1
    #except:
    #    print 'error'
    #    return -1
        
    f=open('wn.pickle','rb')
    wn = pickle.load(f)
    f.close()
    
    def createFolder(path):
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)
    
    if results:
        ## CREATE FOLDERS FOR SCENARIOS
        pressures_Folder = Sc+'\\Pressures'
        createFolder(pressures_Folder)
        dem_Folder = Sc+'\\Demands'
        createFolder(dem_Folder)
        flows_Folder = Sc+'\\Flows'
        createFolder(flows_Folder)
        leaks_Folder = Sc+'\\Leaks'
        createFolder(leaks_Folder)
        
        ## CREATE CSV FILES     
        for leak_i in range(nmLeaksNode):
            fleaks2 = open(leaks_Folder+'\\Leak_'+str(leak_node[leak_i])+'_info.csv', 'w')
            fleaks2.write("{} , {}\n".format('Description', 'Value'))
            fleaks2.write("{} , {}\n".format('Leak Node', str(leak_node[leak_i])))
            fleaks2.write("{} , {}\n".format('Leak Area', str(leak_area[leak_i])))
            fleaks2.write("{} , {}\n".format('Leak Diameter', str(leak_diameter[leak_i])))
            fleaks2.write("{} , {}\n".format('Leak Type', leak_type[leak_i]))
            fleaks2.write("{} , {}\n".format('Leak Start', str(leakStarts[leak_i])))
            fleaks2.write("{} , {}\n".format('Leak End', str(leakEnds[leak_i])))
            fleaks2.write("{} , {}\n".format('Peak Time', str(leak_peak_time[leak_i])))
            fleaks2.close()
            
            # Leaks CSV
            leaks = results.node['leak_demand',:,str(leak_node[leak_i])][0:-1]
            leaks = [ round(elem, 6) *3600  for elem in leaks ]    
            fleaks = pandas.DataFrame(leaks)
            fleaks['Timestamp'] = timeStamp
            fleaks = fleaks.set_index(['Timestamp'])
            fleaks.columns.values[0]='Description'
            fleaks.to_csv(leaks_Folder+'\\Leak_'+str(leak_node[leak_i])+'_demand.csv')
            del fleaks
        
        # Labels scenarios
        flabels = pandas.DataFrame(labels)
        flabels['Timestamp'] = timeStamp
        flabels = flabels.set_index(['Timestamp'])
        flabels.columns.values[0]='Label'
        flabels.to_csv(Sc+'\\Labels.csv')
        del flabels
        
        for j in range(0, wn.num_nodes):
    
            pres = results.node['pressure'][wn.node_name_list[j]]
            pres = pres[:len(timeStamp)]
            pres = [ round(elem, 6) for elem in pres ]
            #if ((all(results.node['pressure',:,:]> 0)) !=True)==True:
                #print('Negative Pressures')
            fpres = pandas.DataFrame(pres)
            fpres['Timestamp'] = timeStamp
            fpres = fpres.set_index(['Timestamp'])
            fpres.columns.values[0]='Value'
            file_pres = pressures_Folder+'\\Node_'+str(wn.node_name_list[j])+'.csv'
            fpres.to_csv(file_pres)            
            del fpres, pres
            
            dem = results.node['demand'][wn.node_name_list[j]]
            dem = dem[:len(timeStamp)]

            dem = [ round(elem, 6) * 3600 for elem in dem ] 
            fdem = pandas.DataFrame(dem)
            fdem['Timestamp'] = timeStamp
            fdem = fdem.set_index(['Timestamp'])
            fdem.columns.values[0]='Value'
            fdem.to_csv(dem_Folder+'\\Node_'+str(wn.node_name_list[j])+'.csv')
            del fdem, dem
            
        for j in range(0, wn.num_links):
            flows = results.link['flowrate'][wn.link_name_list[j]]
            flows = flows[:len(timeStamp)]
            
            flows = [ round(elem, 6) * 3600 for elem in flows ]
            fflows = pandas.DataFrame(flows)
            fflows['Timestamp'] = timeStamp
            fflows = fflows.set_index(['Timestamp'])
            fflows.columns.values[0]='Value'
            fflows.to_csv(flows_Folder+'\\Link_'+str(wn.link_name_list[j])+'.csv')
            del fflows, flows
    
        fscenariosinfo = open(Sc+'\\Scenario-'+str(scNum)+'_info.csv', 'w')
        fscenariosinfo.write("Description , Value\n")     
        fscenariosinfo.write("{} , {}\n".format('Network_Name', inp))
        fscenariosinfo.write("{} , {}\n".format('Duration', str(durationHours)+' hours'))
        fscenariosinfo.write("{} , {}\n".format('Time_Step', str(wn.options.time.report_timestep/60)+' min'))
        fscenariosinfo.write("{} , {}\n".format('Uncertainty_Topology_(%)', uncertainty_Topology))
        fscenariosinfo.write("{} , {}\n".format('Uncertainty_Length_(%)', uncertainty_Length*100))
        fscenariosinfo.write("{} , {}\n".format('Uncertainty_Diameter_(%)', uncertainty_Diameter*100))
        fscenariosinfo.write("{} , {}\n".format('Uncertainty_Roughness_(%)', uncertainty_Roughness*100))
        #for j in range(0, wn.num_links):
        #    fscenariosinfo.write("{} , {}\n".format('Link_Status_'+wn.link_name_list[j], str(results.link['status', 0, wn.link_name_list[j]])))
        fscenariosinfo.close()
        #itsok = True 

        if sum(labels)>0:
            labelScenarios.append(1.0)
        else:
            labelScenarios.append(0.0)
    else:
        print('results empty')
        return -1
        #except:
            #itsok = False
        
    return 1
    
        
if __name__ == '__main__':

    t = time.time()
    
    NumScenarios = 1000
    scArray = range(1, NumScenarios+1)
    
    numCores = multiprocessing.cpu_count()
    p = multiprocessing.Pool(100)
    p.map(runScenarios, list(range(1, NumScenarios)))
    p.close()
    p.join()
    
    #runScenarios(4)
    
    labelScenarios = []
    for i in scArray:
        if len(os.listdir(benchmark + INP +'\\Scenario-'+str(i)+'\\')):
            labelScenarios.append(1.0)
        else:
            labelScenarios.append(0.0)

    flabels2 = pandas.DataFrame(labelScenarios)
    flabels2['Scenario'] = scArray
    flabels2 = flabels2.set_index(['Scenario'])
    flabels2.columns.values[0]='Label'
    flabels2.to_csv(benchmark+ INP+'\\Labels.csv')
    del flabels2, labelScenarios
    
    #scNum = 1
    #NumScenarios = 12
    #while scNum < NumScenarios+1:
    #    if runScenarios(scNum) ==1:
    #        scNum = scNum + 1
    #    else:
    #        print ('scenario warnings patts')
   
    print('Total Elapsed time is '+str(time.time() - t) + ' seconds.')

