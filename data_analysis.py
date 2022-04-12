'''
Created on Oct 01, 2021
@author: Young Min Kim
'''

import pandas as pd 
from os import path

import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_Timeseries(main_list, main_file, sub_file, Y1_Axis, Y2_1_Axis,  Y2_2_Axis, Y2_3_Axis, Y2_4_Axis, Y1_log_OX, Y2_log_OX, progress):

    progress["maximum"] = 100

    # check is it logarithm ?
    if Y1_log_OX == 1:
        Y1_log_OX = "log"
    else:
        Y1_log_OX = "linear"

    if Y2_log_OX == 1:
        Y2_log_OX = "log"
    else:
        Y2_log_OX = "linear"



    # preparation of figure structure
    fig = make_subplots(rows=1, cols=1, subplot_titles=('Graph of ' + str(Y1_Axis) + ' and ' + str(Y2_1_Axis)), specs=[[{"secondary_y": True}]])

    progress["value"] = 10   # increment progressbar
    progress.update() 



    # make variable list for data clean
    variable = [Y1_Axis, Y2_1_Axis, Y2_2_Axis, Y2_3_Axis, Y2_4_Axis]

    main_var = []
    sub_var = []

    for i in range(len(variable)):
        if variable[i] in main_list:
            main_var.append(variable[i])
        else:
            sub_var.append(variable[i])

    main_var.append("Time")
    main_var = list(filter(None, main_var))
    sub_var.append("Time")
    sub_var = list(filter(None, sub_var))

    progress["value"] = 20   # increment progressbar
    progress.update() 



    # Preparation of figure data
    temp_main = pd.read_csv(main_file, index_col=None, header=0, usecols=main_var)
    temp_main["Time"] = pd.to_datetime(temp_main["Time"], format = '%Y-%m-%d %H:%M:%S.%f')

    progress["value"] = 30   # increment progressbar
    progress.update() 

    
    if len(sub_var) == 1:
        pass    
    else:    
        temp_sub = pd.read_csv(sub_file, index_col=None, header=0, usecols=sub_var)
        temp_sub["Time"] = pd.to_datetime(temp_sub["Time"], format = '%Y-%m-%d %H:%M:%S.%f')

    progress["value"] = 40   # increment progressbar
    progress.update() 



    # make figures axies
    if Y1_Axis in main_var:
        fig.add_trace(go.Scatter(x=temp_main["Time"], y=temp_main[Y1_Axis], mode='lines', name=str(Y1_Axis), opacity=0.9), row=1, col=1)
        main_var.remove(str(Y1_Axis))
    elif Y1_Axis in sub_var:
        fig.add_trace(go.Scatter(x=temp_sub["Time"], y=temp_sub[Y1_Axis], mode='lines', name=str(Y1_Axis), opacity=0.9), row=1, col=1)
        sub_var.remove(str(Y1_Axis))
    else:
        pass

    # decoration of figure
    fig.update_yaxes(title_text=str(Y1_Axis), type=Y1_log_OX, row=1, col=1)

    progress["value"] = 60   # increment progressbar
    progress.update() 


    
    if len(main_var) != 0:

        pro_num = progress["value"]
        a = 0

        main_var.remove(str("Time"))

        for i in main_var:
            fig.add_trace(go.Scatter(x=temp_main["Time"], y=temp_main[i], mode='lines', name=str(i), opacity=0.5), row=1, col=1, secondary_y=True)
            fig.update_yaxes(title_text=str(i), type=Y2_log_OX, row=1, col=1, secondary_y=True) 

            a += 1
            progress["value"] = pro_num + (a / int(len(main_var)) * 80)   # increment progressbar
            progress.update()       # have to call update() in loop

    else:
        pass


    if len(sub_var) != 0:

        pro_num = progress["value"]
        a = 0

        sub_var.remove(str("Time"))    

        for i in sub_var:
            fig.add_trace(go.Scatter(x=temp_sub["Time"], y=temp_sub[i], mode='lines', name=str(i), opacity=0.5), row=1, col=1, secondary_y=True)
            fig.update_yaxes(title_text=str(i), type=Y2_log_OX, row=1, col=1, secondary_y=True) 

            a += 1
            progress["value"] = pro_num + (a / int(len(sub_var)) * 95)   # increment progressbar
            progress.update()       # have to call update() in loop

    else:
        print("NG3")
        pass


    fig.update_xaxes(title_text="<b>Process time ( hh-mm-ss )<b>", row=1, col=1)
    fig.update_layout(title= " Monitoring @MURI", hovermode="x unified") 
    fig.show(config={'modeBarButtonsToAdd':['drawline',
                                            'drawopenpath',
                                            'drawclosedpath',
                                            'drawcircle',
                                            'drawrect',
                                            'eraseshape',
                                            'lasso2d'
                                           ], "displaylogo": False},)

    progress["value"] = 100   # increment progressbar
    progress.update() 




def plot_Unit(main_list, op_file, main_file, sub_file, step_start, step_end, X_Axis, Y1_Axis, Y2_Axis, Y1_log_OX, Y2_log_OX, sum_CSV, save_path, progress):
    
    progress["maximum"] = 100

    # check is it logarithm ?
    if Y1_log_OX == 1:
        Y1_log_OX = "log"
    else:
        Y1_log_OX = "linear"

    if Y2_log_OX == 1:
        Y2_log_OX = "log"
    else:
        Y2_log_OX = "linear"



    # make variable list for data clean
    variable = [X_Axis, Y1_Axis, Y2_Axis]

    main_var = []
    sub_var = []

    for i in range(len(variable)):
        if variable[i] in main_list:
            main_var.append(variable[i])
        else:
            sub_var.append(variable[i])

    
    if "Time" in main_var:
        pass
    else:
        main_var.append("Time")

    if "Time" in sub_var:
        pass
    else:
        sub_var.append("Time")
    
    main_var = list(filter(None, main_var))
    sub_var = list(filter(None, sub_var))

    progress["value"] = 2   # increment progressbar
    progress.update() 



    # Preparation of figure data
    temp_main = pd.read_csv(main_file, index_col=None, header=0, usecols=main_var)
    temp_main["Time"] = pd.to_datetime(temp_main["Time"], format = '%Y-%m-%d %H:%M:%S.%f')

    progress["value"] = 4   # increment progressbar
    progress.update() 

    
    if len(sub_var) == 1:
        pass    
    else:    
        temp_sub = pd.read_csv(sub_file, index_col=None, header=0, usecols=sub_var)
        temp_sub["Time"] = pd.to_datetime(temp_sub["Time"], format = '%Y-%m-%d %H:%M:%S.%f')

        temp_main = pd.merge(temp_main, temp_sub, on= 'Time', how='outer').sort_values('Time')
        temp_main.reset_index(inplace = True)

        temp_main = temp_main.fillna(method = 'bfill') 

    progress["value"] = 6   # increment progressbar
    progress.update() 
   


    # Cleaning Operation log
    key_word_REMOVE = ("Semi-", "DryRun")
    temp_op = pd.read_csv(op_file, index_col=None, header=None, sep='\t', names=['RAW'])

    for i in range(int(len(key_word_REMOVE))):
        temp_op = temp_op[temp_op.RAW.str.contains(key_word_REMOVE[i]) == False]

    # Clieaning Operation log
    temp_op = temp_op[temp_op.RAW.str.contains(step_start) | temp_op.RAW.str.contains(step_end) == True].reset_index(drop=True)
    temp_op["Time"], temp_op["PRO"] = temp_op.RAW.str.split(',').str[0], temp_op.RAW.str.split(',').str[1]
    temp_op['Time'] = pd.to_datetime(temp_op['Time'], format = '%Y-%m-%d %H:%M:%S.%f')

    progress["value"] = 8   # increment progressbar
    progress.update()       # have to call update() in loop



    # Remove duplicate order of Section

    restart = 0
    i = 0
    repeats = int(len(temp_op.PRO)/2)
    
    while restart < repeats:
        if temp_op.loc[i*2+1, ("PRO")].find(step_start) != -1:
            temp_op = temp_op.drop(temp_op.index[i*2])
            temp_op = temp_op.reset_index(drop=True)

            i -= 1
            restart -= 1
            repeats = int(len(temp_op.PRO)/2)

        else:
            if temp_op.loc[i*2, ("PRO")].find(step_end) != -1:
                temp_op = temp_op.drop(temp_op.index[i*2])
                temp_op = temp_op.reset_index(drop=True) 

                i -= 1
                restart -= 1
                repeats = int(len(temp_op.PRO)/2)

            else:
                pass

        i += 1
        restart += 1



    progress["value"] = 10   # increment progressbar
    progress.update()       # have to call update() in loop



    # Make CNT col and remove out of range
    pro_num = progress["value"]
    temp_main["CNT"] = -1

    for i in range(int(len(temp_op.Time)/2)):

        try:
            [c, d] = [temp_main.index[temp_main.Time >= temp_op.loc[i*2, ('Time')]][0], temp_main.index[temp_main.Time < temp_op.loc[i*2+1, ('Time')]][-1]]
            temp_main.loc[c:d, ('CNT')] = i
        
            progress["value"] = pro_num + ((i / int(len(temp_op.Time)/2)) * 3)   # increment progressbar
            progress.update()       # have to call update() in loop
        
        except KeyError as e:
            continue
    
        except IndexError as e:
            continue        
    
    temp_main = temp_main[temp_main['CNT'] != -1]



    # Initial figure data
    temp_main_ini = temp_main[temp_main.CNT == int(temp_main.CNT.iloc[0])]
    temp_main_ini = temp_main_ini.reset_index(drop=True)
    
    time_origin_1 = temp_main_ini.Time.iloc[0]
    
    temp_main_ini.Time = temp_main_ini.Time - temp_main_ini.Time.iloc[0] + time_origin_1

    progress["value"] = 13   # increment progressbar
    progress.update() 



    # make figure structure
    fig_dict = {
        "data": [],
        "layout": {},
        "frames": []
    }

    frame_speed = 300
    trans_speed = 150
  


    # Mske structure of figure
    fig_dict["layout"]["xaxis"] = {"title": str(X_Axis)}
    fig_dict["layout"]["yaxis"] = {"title": str(Y1_Axis), "type": Y1_log_OX}

    if Y2_Axis in temp_main:
        fig_dict["layout"]["yaxis2"] = {"title": str(Y2_Axis), "side": 'right', "overlaying": 'y', "anchor": 'x', "type": Y2_log_OX}
    else:
        pass
    
    fig_dict["layout"]["hovermode"] = "closest"
    fig_dict["layout"]["updatemenus"] = [
        {
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": frame_speed, "redraw": False},
                                    "fromcurrent": True, 
                                    "transition": {"duration": trans_speed,
                                                "easing": "quadratic-in-out"}}],
                    "label": "Play",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": frame_speed, "redraw": False},
                                    "mode": "immediate",
                                    "transition": {"duration": trans_speed}}],
                    "label": "Pause",
                    "method": "animate"
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top"
        }
    ]

    sliders_dict = {
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {"size": 20},
            "prefix": "Process time:",
            "visible": True,
            "xanchor": "right"
        },
        "transition": {"duration": trans_speed, "easing": "cubic-in-out"},
        "pad": {"b": 10, "t": 50},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": []
    }

    if Y1_Axis in temp_main:   
        data_dict = {
            "x": list(temp_main_ini[X_Axis]),
            "y": list(temp_main_ini[Y1_Axis]),
            "mode": "lines",
            # "type": Y1_log_OX,
            "text": Y1_Axis,
            "name": Y1_Axis
        }
        fig_dict["data"].append(data_dict)
    else:
        pass

    if Y2_Axis in temp_main:    
        data_dict = {   
            "x": list(temp_main_ini[X_Axis]),
            "y": list(temp_main_ini[Y2_Axis]),
            "yaxis": "y2",
            "mode": "lines",
            # "type": Y2_log_OX,                   
            "text": Y2_Axis,
            "name": Y2_Axis
        }
        fig_dict["data"].append(data_dict)
    else:
        pass

    progress["value"] = 15   # increment progressbar
    progress.update() 



    # Make figure strucuture of Animation
    pro_num = progress["value"]
    a = 0

    # Make frames
    for CNT in range(max(temp_main.CNT)+1):

        try:
            temp_main_cnt = temp_main[temp_main.CNT == CNT]
            temp_main_cnt = temp_main_cnt.reset_index(drop=True)
            
            temp_main_cnt.Time = temp_main_cnt.Time - temp_main_cnt.Time.iloc[0] + time_origin_1
        

            frame = {"data": [], "name": str(CNT)}

            if Y1_Axis in temp_main:
                data_dict = {
                    "x": list(temp_main_cnt[X_Axis]),
                    "y": list(temp_main_cnt[Y1_Axis]),
                    "mode": "lines",
                    # "type": Y1_log_OX,
                    "text": Y1_Axis,
                    "name": Y1_Axis
                }
                frame["data"].append(data_dict)

                fig_dict["frames"].append(frame)
            else:
                pass
            

            if Y2_Axis in temp_main:
                data_dict = {
                    "x": list(temp_main_cnt[X_Axis]),
                    "y": list(temp_main_cnt[Y2_Axis]),
                    "mode": "lines",
                    "yaxis": "y2",
                    # "type": Y2_log_OX,
                    "text": Y2_Axis,
                    "name": Y2_Axis
                }
                frame["data"].append(data_dict)

                fig_dict["frames"].append(frame)
            else:
                pass    


            slider_step = {"args": [
                [CNT],
                {"frame": {"duration": frame_speed, "redraw": False},
                "mode": "immediate",
                "transition": {"duration": trans_speed}}
            ],
                "label": str(CNT),
                "method": "animate"}
            sliders_dict["steps"].append(slider_step)
                        

        except KeyError as e:
            continue
    
        except IndexError as e:
            continue

        fig_dict["layout"]["sliders"] = [sliders_dict]

        fig = go.Figure(fig_dict)

        a += 1

        progress["value"] = pro_num + (a / int(int(len(temp_op.Time)/2)) * 90)   # increment progressbar
        progress.update()       # have to call update() in loop


    fig.update_layout(title= " Monitoring @MURI", hovermode="x unified") 
    fig.show(config={'modeBarButtonsToAdd':['drawline',
                                            'drawopenpath',
                                            'drawclosedpath',
                                            'drawcircle',
                                            'drawrect',
                                            'eraseshape',
                                            'lasso2d'
                                           ], "displaylogo": False},)



    if sum_CSV == 1:
        temp_col = ["Time"]

        if Y1_Axis in temp_main:
            temp_col += [str(Y1_Axis)+"_Max", str(Y1_Axis)+"_Mean", str(Y1_Axis)+"_Min", str(Y1_Axis)+"_Std"]
        else:
            pass

        if Y2_Axis in temp_main:
            temp_col += [str(Y2_Axis)+"_Max", str(Y2_Axis)+"_Mean", str(Y2_Axis)+"_Min", str(Y2_Axis)+"_Std"]
        else:
            pass
        
        temp = pd.DataFrame(index=range(0,int(max(temp_main.CNT)+1)), columns=temp_col)
        
        if "Time" in variable:
            variable.remove("Time")
            variable = list(filter(None, variable))
        else:
            pass


        for CNT in range(max(temp_main.CNT)+1):

            try:
                temp_main_cnt = temp_main[temp_main.CNT == CNT]
                temp_main_cnt = temp_main_cnt.reset_index(drop=True)

                temp.loc[CNT, ('Time')] = temp_main_cnt["Time"][0]

                for i in range(len(variable)):
                    temp.loc[CNT, (str(variable[i])+"_Max")] = temp_main_cnt[variable[i]].max()
                    temp.loc[CNT, (str(variable[i])+"_Min")] = temp_main_cnt[variable[i]].min()
                    temp.loc[CNT, (str(variable[i])+"_Mean")] = temp_main_cnt[variable[i]].mean()
                    temp.loc[CNT, (str(variable[i])+"_Std")] = temp_main_cnt[variable[i]].std()                          

            except KeyError as e:
                continue
        
            except IndexError as e:
                continue
        
        temp.to_csv(save_path + "/summary.csv")

    else:
        return
