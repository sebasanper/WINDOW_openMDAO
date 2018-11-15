from builtins import zip
from builtins import range
from WINDOW_openMDAO.input_params import cable_types, turbine_rated_current
import numpy as np


def choose_cables(number_turbines_per_cable):
    cables_info = cable_types
    cable_list = []
    for number in number_turbines_per_cable:
        for cable in cables_info:
            if turbine_rated_current * number <= cable[1]:
                cable_list.append([number, cable[2] + 365.0])
                break
    return cable_list


def cable_design(WT_List, central_platform_locations, number_turbines_per_cable, cable_list):
    from math import hypot
    from copy import deepcopy
    from heapq import heappush, heappop, heapify

    NT = len(WT_List)

    Crossing_penalty = 0
    Area = []
    Transmission = []
    option = 1  # POS2
    'Remove and return the lowest priority task. Raise KeyError if empty.'
    REMOVED = '<removed-task>'  # placeholder for a removed task

    # ---------------------------------------Main----------------------------------------------
    def set_cable_topology(NT, WT_List, central_platform_locations, Cable_List):
        Wind_turbines = []
        for WT in WT_List:
            Wind_turbines.append([WT[0] + 1, WT[1], WT[2]])
        # initialize the parameters
        Wind_turbinesi, Costi, Cost0i, Costij, Savingsi, Savingsi_finder, distancefromsubstationi, substationi, Routingi, Routing_redi, Routing_greeni, Pathsi, Capacityi, Cable_Costi, Crossings_finder = dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict()
        i = 1
        for substation in central_platform_locations:
            Wind_turbinesi[i], Costi[i], distancefromsubstationi[i] = initial_values(Wind_turbines, substation)
            substationi[i] = substation
            i = i + 1
        # splits the Wind_turbines list in the closest substation
        for j in range(NT):
            empty = []
            for key, value in distancefromsubstationi.items():
                empty.append(value[j])
            index = empty.index(min(empty, key=lambda x: x[2])) + 1
            Wind_turbinesi[index].append([value[j][1], Wind_turbines[j][1], Wind_turbines[j][2]])
        for j in range(len(Cable_List)):
            Capacityi[j + 1] = Cable_List[j][0]
            Cable_Costi[j + 1] = Cable_List[j][1]
        # initialize routes and Saving matrix
        for key, value in Wind_turbinesi.items():
            Pathsi[key], Routingi[key], Routing_redi[key], Routing_greeni[key] = initial_routes(value)
            Cost0i[key], Costij[key] = costi(value, substationi[key])
            Savingsi[key], Savingsi_finder[key], Crossings_finder[key] = savingsi(Cost0i[key], Costij[key], value,
                                                                                  Cable_Costi[1], substationi[key], Area,
                                                                                  Crossing_penalty)
        cable_length = 0
        total_cost = 0
        crossings = 0
        for key in Wind_turbinesi:
            if option == 1:
                Pathsi[key], Routingi[key], Routing_redi[key], Routing_greeni[key] = POS1_Cable_Choice(Savingsi[key],
                                                                                                       Savingsi_finder[key],
                                                                                                       Crossings_finder[
                                                                                                           key],
                                                                                                       Wind_turbinesi[key],
                                                                                                       Pathsi[key],
                                                                                                       Routingi[key],
                                                                                                       substationi[key],
                                                                                                       Capacityi,
                                                                                                       Routing_redi[key],
                                                                                                       Routing_greeni[key],
                                                                                                       Cable_Costi)
            else:
                Pathsi[key], Routingi[key], Routing_redi[key], Routing_greeni[key] = POS2_Cable_Choice(Savingsi[key],
                                                                                                       Savingsi_finder[key],
                                                                                                       Crossings_finder[
                                                                                                           key],
                                                                                                       Wind_turbinesi[key],
                                                                                                       Pathsi[key],
                                                                                                       Routingi[key],
                                                                                                       substationi[key],
                                                                                                       Capacityi,
                                                                                                       Routing_redi[key],
                                                                                                       Routing_greeni[key],
                                                                                                       Costi[key],
                                                                                                       Cable_Costi)
            Pathsi[key], Routingi[key] = RouteOpt(Routingi[key], substationi[key], Costi[key], Capacityi, Pathsi[key],
                                                  Wind_turbinesi[key])
            length, cost = plotting(substationi[key], Wind_turbinesi[key], Routingi[key], Routing_redi[key],
                                        Routing_greeni[key], Capacityi, Cable_Costi)
            cable_length +=length
            total_cost += cost
            for route in Routingi[key]:
                if edge_crossings_area([route[0], route[1]], Wind_turbinesi[key], substationi[key], Area)[0]:
                    crossings += edge_crossings_area([route[0], route[1]], Wind_turbinesi[key], substationi[key], Area)[1]

        return total_cost, Pathsi, cable_length


    def POS1_Cable_Choice(Savingsi, Savingsi_finder, Crossingsi_finder, Wind_turbinesi, Paths, Routing,
                          central_platform_location, Capacityi, Routing_red, Routing_green, Cable_Costi):
        total_update_red = []
        total_update_green = []
        while True:
            if Savingsi:
                Savingsi, Savingsi_finder, saving = pop_task(Savingsi, Savingsi_finder)
            else:
                break
            if saving is None or saving[0] > 0:
                break
            arc = [saving[1], saving[2]]
            if check_same_path(arc, Paths) is False and any(
                    [True for e in [[arc[0], 0]] if e in Routing]) and one_neighbor(arc[1], Paths) is False:
                condition4 = dict()
                for key, value in Capacityi.items():
                    condition4[key] = check_capacity(arc, Paths, Capacityi[key])
                if condition4[1] is False and edge_crossings(arc, Wind_turbinesi, central_platform_location,
                                                             Routing) is False and \
                                edge_crossings_area(arc, Wind_turbinesi, central_platform_location, Transmission)[
                                    0] is False:
                    Routing = []
                    for index1, path in enumerate(Paths):
                        if arc[0] == path[1]:
                            Paths[index1].remove(0)
                            break
                    for index2, path in enumerate(Paths):
                        if arc[1] == path[-1]:
                            break
                    Paths[index2] = Paths[index2] + Paths[index1]
                    Paths[index1] = []
                    Paths = [path for path in Paths if path != []]
                    for i in Paths:
                        for j in range(len(i) - 1):
                            Routing.append([i[j + 1], i[j]])

                if len(condition4) > 1 and condition4[1] == True and condition4[2] == False:
                    if edge_crossings_area(arc, Wind_turbinesi, central_platform_location, Transmission)[
                        0] == False and edge_crossings(arc, Wind_turbinesi, central_platform_location, Routing) == False:
                        Paths_temp = deepcopy(Paths)
                        Routing_temp = []
                        total_update_red_temp = []
                        Routing_red_temp = Routing_red
                        for index1, path in enumerate(Paths_temp):
                            if arc[0] == path[1]:
                                Paths_temp[index1].remove(0)
                                break
                        for index2, path in enumerate(Paths_temp):
                            if arc[1] == path[-1]:
                                break
                        Paths_temp[index2] = Paths_temp[index2] + Paths_temp[index1]
                        Paths_temp[index1] = []
                        for i in Paths_temp:
                            if len(i) >= 2:
                                for j in range(len(i) - 1):
                                    Routing_temp.append([i[j + 1], i[j]])
                        overcapacity = len(Paths_temp[index2]) - 1 - Capacityi[1]
                        index3 = overcapacity
                        for i in range(index3):
                            total_update_red_temp.append([Paths_temp[index2][i + 1], Paths_temp[index2][i]])
                        total_update_red_temp = renew_update(total_update_red, total_update_red_temp,
                                                             Paths_temp) + total_update_red_temp

                        Routing_red_temp = []
                        for route in total_update_red_temp:
                            for z in range(len(route) - 1):
                                Routing_red_temp.append([route[z], route[z + 1]])
                        new = -(cable_cost(central_platform_location, Wind_turbinesi, Routing, Routing_red, Routing_green,
                                           Cable_Costi) - cable_cost(central_platform_location, Wind_turbinesi,
                                                                     Routing_temp, Routing_red_temp, Routing_green,
                                                                     Cable_Costi))
                        arc1 = [arc[0], 0]
                        new = new + Crossing_penalty * (
                        Crossingsi_finder[(arc[0], arc[1])] - Crossingsi_finder[(arc1[0], arc1[1])])
                        Savingsi, Savingsi_finder = add_task(Savingsi, Savingsi_finder, (arc[0], arc[1]), new)
                        Savingsi, Savingsi_finder, max_saving = pop_task(Savingsi, Savingsi_finder)
                        if max_saving[0] == new:
                            Paths = Paths_temp
                            Paths = [path for path in Paths if path != []]
                            Routing = Routing_temp
                            Routing_red = Routing_red_temp
                            total_update_red = total_update_red_temp
                        else:
                            Savingsi, Savingsi_finder = add_task(Savingsi, Savingsi_finder, (max_saving[1], max_saving[2]),
                                                                 max_saving[0])

                if len(condition4) > 2 and condition4[1] == True and condition4[2] == True and condition4[3] == False:
                    if edge_crossings_area(arc, Wind_turbinesi, central_platform_location, Transmission)[
                        0] == False and edge_crossings(arc, Wind_turbinesi, central_platform_location, Routing) == False:
                        Paths_temp = deepcopy(Paths)
                        Routing_temp = []
                        total_update_green_temp = []
                        total_update_red_temp = []
                        Routing_green_temp = Routing_green
                        for index1, path in enumerate(Paths_temp):
                            if arc[0] == path[1]:
                                Paths_temp[index1].remove(0)
                                break
                        for index2, path in enumerate(Paths_temp):
                            if arc[1] == path[-1]:
                                break
                        Paths_temp[index2] = Paths_temp[index2] + Paths_temp[index1]
                        Paths_temp[index1] = []
                        for i in Paths_temp:
                            if len(i) >= 2:
                                for j in range(len(i) - 1):
                                    Routing_temp.append([i[j + 1], i[j]])

                        overcapacity1 = len(Paths_temp[index2]) - 1 - Capacityi[1]
                        overcapacity2 = len(Paths_temp[index2]) - 1 - Capacityi[2]
                        index3 = overcapacity1
                        index4 = overcapacity2
                        for i in range(index4):
                            total_update_green_temp.append([Paths_temp[index2][i + 1], Paths_temp[index2][i]])
                        for i in range(index4, index3):
                            total_update_red_temp.append([Paths_temp[index2][i + 1], Paths_temp[index2][i]])
                        total_update_red_temp = renew_update(total_update_red, total_update_red_temp,
                                                             Paths_temp) + total_update_red_temp
                        total_update_green_temp = renew_update(total_update_green, total_update_green_temp,
                                                               Paths_temp) + total_update_green_temp
                        Routing_red_temp = []
                        for route in total_update_red_temp:
                            for z in range(len(route) - 1):
                                Routing_red_temp.append([route[z], route[z + 1]])
                        Routing_green_temp = []
                        for route in total_update_green_temp:
                            for z in range(len(route) - 1):
                                Routing_green_temp.append([route[z], route[z + 1]])
                        new = -(cable_cost(central_platform_location, Wind_turbinesi, Routing, Routing_red, Routing_green,
                                           Cable_Costi) - cable_cost(central_platform_location, Wind_turbinesi,
                                                                     Routing_temp, Routing_red_temp, Routing_green_temp,
                                                                     Cable_Costi))
                        arc1 = [arc[0], 0]
                        new = new + Crossing_penalty * (
                        Crossingsi_finder[(arc[0], arc[1])] - Crossingsi_finder[(arc1[0], arc1[1])])
                        Savingsi, Savingsi_finder = add_task(Savingsi, Savingsi_finder, (arc[0], arc[1]), new)
                        Savingsi, Savingsi_finder, max_saving = pop_task(Savingsi, Savingsi_finder)
                        if max_saving[0] == new:
                            Paths = Paths_temp
                            Paths = [path for path in Paths if path != []]
                            Routing = Routing_temp
                            Routing_red = Routing_red_temp
                            Routing_green = Routing_green_temp
                            total_update_red = total_update_red_temp
                            total_update_green = total_update_green_temp
                        else:
                            Savingsi, Savingsi_finder = add_task(Savingsi, Savingsi_finder, (max_saving[1], max_saving[2]),
                                                                 max_saving[0])
        return Paths, Routing, Routing_red, Routing_green


    def POS2_Cable_Choice(Savingsi, Savingsi_finder, Crossingsi_finder, Wind_turbinesi, Paths, Routing,
                          central_platform_location, Capacityi, Routing_red, Routing_green, Costi, Cable_Costi):
        total_update_red = []
        total_update_green = []
        while True:
            if Savingsi:
                Savingsi, Savingsi_finder, saving = pop_task(Savingsi, Savingsi_finder)
            else:
                break
            if saving is None or saving[0] > 0:
                break
            arc = [saving[1], saving[2]]
            condition1 = check_same_path(arc, Paths)
            condition21 = any([True for e in [[arc[0], 0]] if e in Routing])
            condition22 = one_neighbor(arc[0], Paths)
            condition3 = one_neighbor(arc[1], Paths)
            if condition1 is False and (condition21 or (condition22 is False)) and condition3 is False:
                condition4 = dict()
                for key, value in Capacityi.items():
                    condition4[key] = check_capacity(arc, Paths, Capacityi[key])
                if condition4[1] is False and edge_crossings(arc, Wind_turbinesi, central_platform_location, Routing) is False and edge_crossings_area(arc, Wind_turbinesi, central_platform_location, Transmission)[0] is False:
                    Routing = []
                    for index1, path in enumerate(Paths):
                        if arc[0] in path:
                            index1 = Paths.index(path)
                            break
                    for index2, path in enumerate(Paths):
                        if arc[1] in path:
                            index2 = Paths.index(path)
                            break
                    Paths[index1].remove(0)
                    if condition21:
                        Paths[index2] = Paths[index2] + Paths[index1]
                        Paths[index1] = []
                    elif condition22 is False and condition21 is False:
                        Paths[index1].reverse()
                        Paths[index2] = Paths[index2] + Paths[index1]
                        Paths[index1] = []
                        #               reinsertions start
                        first_client = Paths[index2][-1]
                        for k in Wind_turbinesi:
                            Savingsi, Savingsi_finder = add_task(Savingsi, Savingsi_finder, (k[0], first_client),
                                                                 -(Costi[k[0]][0] - Costi[k[0]][first_client]) *
                                                                 Cable_Costi[1])
                    u = Paths[index2][-1]
                    w = Paths[index2][1]
                    Paths = [path for path in Paths if path != []]
                    for i in Paths:
                        for j in range(len(i) - 1):
                            Routing.append([i[j + 1], i[j]])
                    for n in Wind_turbinesi:
                        value = -(Costi[w][0] - Costi[u][n[0]]) * Cable_Costi[1]
                        if u != n[0]:
                            value = value + Crossing_penalty * (Crossingsi_finder[(u, n[0])] - Crossingsi_finder[(w, 0)])
                        Savingsi, Savingsi_finder = add_task(Savingsi, Savingsi_finder, (u, n[0]), value)
                    heapify(Savingsi)

                if len(condition4) > 1 and condition4[1] == True and condition4[2] == False:
                    if edge_crossings_area(arc, Wind_turbinesi, central_platform_location, Transmission)[
                        0] == False and edge_crossings(arc, Wind_turbinesi, central_platform_location, Routing) == False:
                        Paths_temp = deepcopy(Paths)
                        Routing_temp = []
                        total_update_red_temp = []
                        Routing_red_temp = Routing_red
                        for index1, path in enumerate(Paths_temp):
                            if arc[0] in path:
                                index1 = Paths_temp.index(path)
                                break
                        for index2, path in enumerate(Paths_temp):
                            if arc[1] in path:
                                index2 = Paths_temp.index(path)
                                break
                        Paths_temp[index1].remove(0)
                        if condition21 == True:
                            Paths_temp[index2] = Paths_temp[index2] + Paths_temp[index1]
                        elif condition22 == False and condition21 == False:
                            Paths_temp[index1].reverse()
                            Paths_temp[index2] = Paths_temp[index2] + Paths_temp[index1]
                        Paths_temp[index1] = []
                        for i in Paths_temp:
                            if len(i) >= 2:
                                for j in range(len(i) - 1):
                                    Routing_temp.append([i[j + 1], i[j]])
                        overcapacity = len(Paths_temp[index2]) - 1 - Capacityi[1]
                        index3 = overcapacity
                        for i in range(0, index3):
                            total_update_red_temp.append([Paths_temp[index2][i + 1], Paths_temp[index2][i]])
                        total_update_red_temp = renew_update(total_update_red, total_update_red_temp,
                                                             Paths_temp) + total_update_red_temp
                        Routing_red_temp = []
                        for route in total_update_red_temp:
                            for z in range(0, len(route) - 1):
                                Routing_red_temp.append([route[z], route[z + 1]])
                        new = -(cable_cost(central_platform_location, Wind_turbinesi, Routing, Routing_red, Routing_green,
                                           Cable_Costi) - cable_cost(central_platform_location, Wind_turbinesi,
                                                                     Routing_temp, Routing_red_temp, Routing_green,
                                                                     Cable_Costi))
                        w = Paths_temp[index2][1]
                        new += Crossing_penalty * (Crossingsi_finder[(arc[0], arc[1])] - Crossingsi_finder[(w, 0)])
                        Savingsi, Savingsi_finder = add_task(Savingsi, Savingsi_finder, (arc[0], arc[1]), new)
                        Savingsi, Savingsi_finder, max_saving = pop_task(Savingsi, Savingsi_finder)
                        if max_saving[0] == new:
                            Paths = Paths_temp
                            Routing = Routing_temp
                            Routing_red = Routing_red_temp
                            total_update_red = total_update_red_temp
                            u = Paths[index2][-1]
                            w = Paths[index2][1]
                            Paths = [path for path in Paths if path != []]
                            for n in Wind_turbinesi:
                                if one_neighbor(n[0], Paths) == False:
                                    value = -(Costi[w][0] - Costi[u][n[0]]) * Cable_Costi[1]
                                    if u != n[0]:
                                        value = value + Crossing_penalty * (
                                        Crossingsi_finder[(u, n[0])] - Crossingsi_finder[(w, 0)])
                                    Savingsi, Savingsi_finder = add_task(Savingsi, Savingsi_finder, (u, n[0]), value)
                            heapify(Savingsi)
                        else:
                            Savingsi, Savingsi_finder = add_task(Savingsi, Savingsi_finder, (max_saving[1], max_saving[2]),
                                                                 max_saving[0])

                if len(condition4) > 2 and condition4[1] == True and condition4[2] == True and condition4[3] == False:
                    if edge_crossings_area(arc, Wind_turbinesi, central_platform_location, Transmission)[
                        0] == False and edge_crossings(arc, Wind_turbinesi, central_platform_location, Routing) == False:
                        Paths_temp = deepcopy(Paths)
                        Routing_temp = []
                        total_update_green_temp = []
                        total_update_red_temp = []
                        Routing_green_temp = Routing_green
                        for index1, path in enumerate(Paths_temp):
                            if arc[0] in path:
                                index1 = Paths_temp.index(path)
                                break
                        for index2, path in enumerate(Paths_temp):
                            if arc[1] in path:
                                index2 = Paths_temp.index(path)
                                break
                        Paths_temp[index1].remove(0)
                        if condition21 == True:
                            Paths_temp[index2] = Paths_temp[index2] + Paths_temp[index1]
                        elif condition22 == False and condition21 == False:
                            Paths_temp[index1].reverse()
                            Paths_temp[index2] = Paths_temp[index2] + Paths_temp[index1]
                        Paths_temp[index1] = []
                        for i in Paths_temp:
                            if len(i) >= 2:
                                for j in range(len(i) - 1):
                                    Routing_temp.append([i[j + 1], i[j]])
                        overcapacity1 = len(Paths_temp[index2]) - 1 - Capacityi[1]
                        overcapacity2 = len(Paths_temp[index2]) - 1 - Capacityi[2]
                        index3 = overcapacity1
                        index4 = overcapacity2
                        for i in range(0, index4):
                            total_update_green_temp.append([Paths_temp[index2][i + 1], Paths_temp[index2][i]])
                        for i in range(index4, index3):
                            total_update_red_temp.append([Paths_temp[index2][i + 1], Paths_temp[index2][i]])
                        total_update_red_temp = renew_update(total_update_red, total_update_red_temp,
                                                             Paths_temp) + total_update_red_temp
                        total_update_green_temp = renew_update(total_update_green, total_update_green_temp,
                                                               Paths_temp) + total_update_green_temp
                        Routing_red_temp = []
                        for route in total_update_red_temp:
                            for z in range(0, len(route) - 1):
                                Routing_red_temp.append([route[z], route[z + 1]])
                        Routing_green_temp = []
                        for route in total_update_green_temp:
                            for z in range(0, len(route) - 1):
                                Routing_green_temp.append([route[z], route[z + 1]])
                        new = -(cable_cost(central_platform_location, Wind_turbinesi, Routing, Routing_red, Routing_green,
                                           Cable_Costi) - cable_cost(central_platform_location, Wind_turbinesi,
                                                                     Routing_temp, Routing_red_temp, Routing_green_temp,
                                                                     Cable_Costi))
                        w = Paths_temp[index2][1]
                        new = new + Crossing_penalty * (Crossingsi_finder[(arc[0], arc[1])] - Crossingsi_finder[(w, 0)])
                        Savingsi, Savingsi_finder = add_task(Savingsi, Savingsi_finder, (arc[0], arc[1]), new)
                        Savingsi, Savingsi_finder, max_saving = pop_task(Savingsi, Savingsi_finder)
                        if max_saving[0] == new:
                            Paths = Paths_temp
                            Routing = Routing_temp
                            Routing_red = Routing_red_temp
                            Routing_green = Routing_green_temp
                            total_update_red = total_update_red_temp
                            total_update_green = total_update_green_temp
                            u = Paths[index2][-1]
                            w = Paths[index2][1]
                            Paths = [path for path in Paths if path != []]
                            for n in Wind_turbinesi:
                                if one_neighbor(n[0], Paths) == False:
                                    value = -(Costi[w][0] - Costi[u][n[0]]) * Cable_Costi[1]
                                    if u != n[0]:
                                        value = value + Crossing_penalty * (
                                        Crossingsi_finder[(u, n[0])] - Crossingsi_finder[(w, 0)])
                                    Savingsi, Savingsi_finder = add_task(Savingsi, Savingsi_finder, (u, n[0]), value)
                            heapify(Savingsi)
                        else:
                            Savingsi, Savingsi_finder = add_task(Savingsi, Savingsi_finder, (max_saving[1], max_saving[2]),
                                                                 max_saving[0])
        return Paths, Routing, Routing_red, Routing_green


    def renew_update(total_update, total_update_temp, Paths_temp):
        indeces = []
        for indexerase, route in enumerate(total_update):
            for turbine in route:
                if turbine != 0:
                    for pair in total_update_temp:
                        if (pair[0] != 0 and pair[1] == 0) or (pair[0] == 0 and pair[1] != 0):
                            same1 = [turbine, pair[0]]
                        if pair[0] != 0 and pair[1] != 0:
                            same1 = [turbine, pair[0]]
                            same2 = [turbine, pair[1]]
                            if check_same_path(same1, Paths_temp) == True or check_same_path(same2, Paths_temp) == True:
                                if indexerase not in indeces:
                                    indeces.append(indexerase)
        if indeces != []:
            for i in indeces:
                total_update[i] = []
        for pair in total_update[:]:
            if pair == []:
                total_update.remove(pair)
        return total_update


    def RouteOpt(Routing, central_platform_location, Costi, Capacityi, Paths, Wind_turbinesi):
        list = []
        for index, path in enumerate(Paths):
            if len(path) - 1 <= Capacityi[1]:
                path.reverse()
                cond = True
                while cond == True:
                    for l in range(1, len(path)):
                        list.append([Costi[path[l - 1]][path[l]] - Costi[path[l]][path[0]], path[0], path[l]])
                    s = max(list, key=lambda x: x[0])
                    if s[0] > 0 and edge_crossings([s[1], s[2]], Wind_turbinesi, central_platform_location,
                                                   Routing) == False and \
                                    edge_crossings_area([s[1], s[2]], Wind_turbinesi, central_platform_location,
                                                        Transmission)[0] == False:
                        for lamd, k in enumerate(list):
                            if k == s:
                                xmm = lamd + 1
                                path1 = path[:xmm]
                                path2 = path[xmm:]
                                path1.reverse()
                                path = path1 + path2
                                Paths[index] = path
                                list = []
                                cond = True
                    else:
                        list = []
                        cond = False
            elif len(path) - 1 > Capacityi[1]:
                path.reverse()
                cond = True
                while cond == True:
                    for l in range(1, len(path)):
                        list.append([Costi[path[l - 1]][path[l]] - Costi[path[l]][path[0]], path[0], path[l]])
                    s = max(list, key=lambda x: x[0])
                    if s[0] > 0 and edge_crossings([s[1], s[2]], Wind_turbinesi, central_platform_location,
                                                   Routing) == False:
                        for lamd, k in enumerate(list):
                            if k == s:
                                xmm = lamd + 1
                                path1 = path[:xmm]
                                path2 = path[xmm:]
                                path1.reverse()
                                path = path1 + path2
                                Paths[index] = path
                                list = []
                                cond = True
                    else:
                        list = []
                        cond = False
        Routing = []
        for i in Paths:
            i.reverse()
            for j in range(len(i) - 1):
                Routing.append([i[j + 1], i[j]])
        return Paths, Routing


    def initial_values(Wind_turbines, central_platform_location):
        Costi = [[0 for i in range(NT + 1)] for j in range(NT + 1)]
        set_cost_matrix(Costi, Wind_turbines, central_platform_location)
        distancefromsubstationi = [[0, i + 1, Costi[0][i + 1]] for i in range(len(Costi[0]) - 1)]
        Wind_turbinesi = []
        return Wind_turbinesi, Costi, distancefromsubstationi


    def initial_routes(Wind_turbinesi):
        Routing_greeni = []
        Routing_redi = []
        Routingi = []
        Pathsi = []
        for WT in Wind_turbinesi:
            Routingi.append([WT[0], 0])
            Pathsi.append([0, WT[0]])
        return Pathsi, Routingi, Routing_redi, Routing_greeni


    def costi(Wind_turbinesi, central_platform_location):
        Cost0i = []
        Costij = []
        for i in Wind_turbinesi:
            Cost0i.append([0, i[0], hypot(central_platform_location[0] - i[1], central_platform_location[1] - i[2])])
            for j in Wind_turbinesi:
                if i != j:
                    Costij.append([i[0], j[0], hypot(i[1] - j[1], i[2] - j[2])])
        return Cost0i, Costij


    def savingsi(Cost0i, Costij, Wind_turbinesi, Cable_Cost1, central_platform_location, Area, Crossing_penalty):
        Savingsi = []
        Savingsi_finder = {}
        Crossingsi_finder = {}
        counter = 0
        for i in zip(*Wind_turbinesi)[0]:
            k = Cost0i[counter]
            step = (len(Wind_turbinesi) - 1) * counter
            for j in range(step, step + len(Wind_turbinesi) - 1):
                saving = -(k[2] - Costij[j][2]) * Cable_Cost1
                arc1 = [i, 0]
                arc2 = [i, Costij[j][1]]
                crossings_arc1 = edge_crossings_area(arc1, Wind_turbinesi, central_platform_location, Area)[1]
                crossings_arc2 = edge_crossings_area(arc2, Wind_turbinesi, central_platform_location, Area)[1]
                Crossingsi_finder[(arc1[0], arc1[1])] = crossings_arc1
                Crossingsi_finder[(arc2[0], arc2[1])] = crossings_arc2
                saving = saving + Crossing_penalty * (crossings_arc2 - crossings_arc1)
                if saving < 0:
                    add_task(Savingsi, Savingsi_finder, (i, Costij[j][1]), saving)
            counter += 1
        return Savingsi, Savingsi_finder, Crossingsi_finder


    def add_task(Savings, entry_finder, task, priority):
        'Add a new task or update the priority of an existing task'
        if task in entry_finder:
            entry_finder = remove_task(entry_finder, task)
        entry = [priority, task[0], task[1]]
        entry_finder[(task[0], task[1])] = entry
        heappush(Savings, entry)
        return Savings, entry_finder


    def remove_task(entry_finder, task):
        entry = entry_finder.pop(task)
        entry[0] = REMOVED
        return entry_finder


    def pop_task(Savings, entry_finder):
        while Savings:
            saving = heappop(Savings)
            if saving[0] is not REMOVED:
                del entry_finder[(saving[1], saving[2])]
                return Savings, entry_finder, saving


    def set_cost_matrix(Cost, Wind_turbines, central_platform_location):
        Cost[0][0] = float('inf')
        for i in Wind_turbines:
            Cost[0][i[0]] = hypot(central_platform_location[0] - i[1], central_platform_location[1] - i[2])
            Cost[i[0]][0] = hypot(central_platform_location[0] - i[1], central_platform_location[1] - i[2])
            for j in Wind_turbines:
                if i == j:
                    Cost[i[0]][j[0]] = float('inf')
                else:
                    Cost[i[0]][j[0]] = hypot(i[1] - j[1], i[2] - j[2])


    # Subroutine 4, check if two turbines in the same arc are in the same path
    def check_same_path(arc, Paths):
        same_path = False
        for path in Paths:
            if arc[0] in path and arc[1] in path:
                same_path = True
                break
        return same_path


    # Subroutine 5, check if turbine u has only one neighbor in Routing
    def one_neighbor(turbine, Paths):
        more_than_one = False
        for path in Paths:
            if turbine in path and turbine != path[-1]:
                more_than_one = True
                break
        return more_than_one


    def check_capacity(arc, Paths, Capacity):
        cap_exceeded = False
        turbines_in_branch = 0
        for path in Paths:
            if arc[0] in path or arc[1] in path:
                turbines_in_branch = turbines_in_branch + (len(path) - 1)
                if turbines_in_branch > Capacity:
                    cap_exceeded = True
                    break
        return cap_exceeded


    def edge_crossings(arc, Wind_turbines, central_platform_location, Routing):
        x1, y1 = give_coordinates(arc[0], Wind_turbines, central_platform_location)
        x2, y2 = give_coordinates(arc[1], Wind_turbines, central_platform_location)
        intersection = False
        # Left - 0
        # Right - 1
        # Colinear - 2
        for route in Routing:
            if arc[0] not in route:
                x3, y3 = give_coordinates(route[0], Wind_turbines, central_platform_location)
                x4, y4 = give_coordinates(route[1], Wind_turbines, central_platform_location)
                counter = 0
                Area = [0, 0, 0, 0]
                Position = [0, 0, 0, 0]
                Area[0] = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
                Area[1] = (x2 - x1) * (y4 - y1) - (x4 - x1) * (y2 - y1)
                Area[2] = (x4 - x3) * (y1 - y3) - (x1 - x3) * (y4 - y3)
                Area[3] = (x4 - x3) * (y2 - y3) - (x2 - x3) * (y4 - y3)
                for i in range(4):
                    if Area[i] > 0:
                        Position[i] = 0
                    elif Area[i] < 0:
                        Position[i] = 1
                    else:
                        Position[i] = 2
                        counter = counter + 1
                if Position[0] != Position[1] and Position[2] != Position[3] and counter <= 1:
                    intersection = True
                    break
        return intersection


    def edge_crossings_area(arc, Wind_turbines, central_platform_location, Area_cross):
        x1, y1 = give_coordinates(arc[0], Wind_turbines, central_platform_location)
        x2, y2 = give_coordinates(arc[1], Wind_turbines, central_platform_location)
        intersection = False
        crossings = 0
        for area in Area_cross:
            counter = 0
            x3, y3 = area[0][0], area[0][1]
            x4, y4 = area[1][0], area[1][1]
            Area = [0, 0, 0, 0]
            Position = [0, 0, 0, 0]
            Area[0] = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
            Area[1] = (x2 - x1) * (y4 - y1) - (x4 - x1) * (y2 - y1)
            Area[2] = (x4 - x3) * (y1 - y3) - (x1 - x3) * (y4 - y3)
            Area[3] = (x4 - x3) * (y2 - y3) - (x2 - x3) * (y4 - y3)
            for i in range(4):
                if Area[i] > 0:
                    Position[i] = 0
                elif Area[i] < 0:
                    Position[i] = 1
                else:
                    Position[i] = 2
                    counter = counter + 1
            if Position[0] != Position[1] and Position[2] != Position[3] and counter <= 1:
                intersection = True
                crossings = crossings + 1
        return intersection, crossings


    # Plotting+Cable_length
    def plotting(central_platform_location1, Wind_turbines1, Routing, Routing_red, Routing_green, Capacityi,
                 Cable_Costi):
        central_platform_location1_1 = [[0, central_platform_location1[0], central_platform_location1[1]]]
        Full_List = central_platform_location1_1 + Wind_turbines1
        Routing_blue = [i for i in Routing if i not in Routing_red]
        Routing_blue = [i for i in Routing_blue if i not in Routing_green]
        cable_length1blue = 0
        index, x, y = list(zip(*Full_List))
        arcs1 = []
        arcs2 = []
        for i in Routing_blue:
            for j in Full_List:
                if j[0] == i[0]:
                    arcs1.append([j[1], j[2]])
                if j[0] == i[1]:
                    arcs2.append([j[1], j[2]])
        for i in range(len(arcs1)):
            arcs1.insert(2 * i + 1, arcs2[i])
        for j in range(len(arcs1) - len(Routing_blue)):
            cable_length1blue = cable_length1blue + hypot(arcs1[2 * j][0] - arcs1[2 * j + 1][0],
                                                          arcs1[2 * j][1] - arcs1[2 * j + 1][1])
        cable_cost = Cable_Costi[1] * (cable_length1blue)
        cable_length = cable_length1blue

        if len(Cable_Costi) == 2:
            cable_length1red = 0
            arcs1 = []
            arcs2 = []
            for i in Routing_red:
                for j in Full_List:
                    if j[0] == i[0]:
                        arcs1.append([j[1], j[2]])
                    if j[0] == i[1]:
                        arcs2.append([j[1], j[2]])
            for i in range(len(arcs1)):
                arcs1.insert(2 * i + 1, arcs2[i])
            for j in range(len(arcs1) - len(Routing_red)):
                cable_length1red = cable_length1red + hypot(arcs1[2 * j][0] - arcs1[2 * j + 1][0],
                                                            arcs1[2 * j][1] - arcs1[2 * j + 1][1])
            cable_cost = Cable_Costi[1] * (cable_length1blue) + Cable_Costi[2] * (cable_length1red)
            cable_length = cable_length1blue + cable_length1red

        if len(Cable_Costi) == 3:

            cable_length1red = 0
            arcs1 = []
            arcs2 = []
            for i in Routing_red:
                for j in Full_List:
                    if j[0] == i[0]:
                        arcs1.append([j[1], j[2]])
                    if j[0] == i[1]:
                        arcs2.append([j[1], j[2]])
            for i in range(len(arcs1)):
                arcs1.insert(2 * i + 1, arcs2[i])
            for j in range(len(arcs1) - len(Routing_red)):
                cable_length1red = cable_length1red + hypot(arcs1[2 * j][0] - arcs1[2 * j + 1][0],
                                                            arcs1[2 * j][1] - arcs1[2 * j + 1][1])

            cable_length1green = 0
            arcs1 = []
            arcs2 = []
            for i in Routing_green:
                for j in Full_List:
                    if j[0] == i[0]:
                        arcs1.append([j[1], j[2]])
                    if j[0] == i[1]:
                        arcs2.append([j[1], j[2]])
            for i in range(len(arcs1)):
                arcs1.insert(2 * i + 1, arcs2[i])
            for j in range(len(arcs1) - len(Routing_green)):
                cable_length1green = cable_length1green + hypot(arcs1[2 * j][0] - arcs1[2 * j + 1][0],
                                                                arcs1[2 * j][1] - arcs1[2 * j + 1][1])
            cable_length = cable_length1blue + cable_length1red + cable_length1green
            cable_cost = Cable_Costi[1] * (cable_length1blue) + Cable_Costi[2] * (cable_length1red) + Cable_Costi[3] * (
            cable_length1green)
        return cable_length, cable_cost


    def cable_cost(central_platform_location, Wind_turbinesi, Routing, Routing_red, Routing_green, Cable_Costi):
        Routing_blue = [i for i in Routing if i not in Routing_red]
        Routing_blue = [i for i in Routing_blue if i not in Routing_green]
        cable_length1blue = 0
        for route in Routing_blue:
            x1, y1 = give_coordinates(route[0], Wind_turbinesi, central_platform_location)
            x2, y2 = give_coordinates(route[1], Wind_turbinesi, central_platform_location)
            cable_length1blue = cable_length1blue + hypot(x2 - x1, y2 - y1)
        cable_cost = Cable_Costi[1] * (cable_length1blue)

        if len(Cable_Costi) == 2:
            cable_length1red = 0
            for route in Routing_red:
                x1, y1 = give_coordinates(route[0], Wind_turbinesi, central_platform_location)
                x2, y2 = give_coordinates(route[1], Wind_turbinesi, central_platform_location)
                cable_length1red = cable_length1red + hypot(x2 - x1, y2 - y1)
            cable_cost = Cable_Costi[1] * (cable_length1blue) + Cable_Costi[2] * (cable_length1red)

        if len(Cable_Costi) == 3:
            cable_length1red = 0
            for route in Routing_red:
                x1, y1 = give_coordinates(route[0], Wind_turbinesi, central_platform_location)
                x2, y2 = give_coordinates(route[1], Wind_turbinesi, central_platform_location)
                cable_length1red = cable_length1red + hypot(x2 - x1, y2 - y1)
            cable_length1green = 0
            for route in Routing_green:
                x1, y1 = give_coordinates(route[0], Wind_turbinesi, central_platform_location)
                x2, y2 = give_coordinates(route[1], Wind_turbinesi, central_platform_location)
                cable_length1green = cable_length1green + hypot(x2 - x1, y2 - y1)
            cable_cost = Cable_Costi[1] * (cable_length1blue) + Cable_Costi[2] * (cable_length1red) + Cable_Costi[3] * (
            cable_length1green)
        return cable_cost


    # Submethods return x and y coordinates of a turbine if it's ID is known. The OHVS must also be included
    def give_coordinates(turbineID, Wind_turbines, central_platform_location):
        if turbineID == 0:
            x = central_platform_location[0]
            y = central_platform_location[1]
        else:
            turbine = WT_List[turbineID - 1]
            x = turbine[1]
            y = turbine[2]
        return x, y

    return set_cable_topology(NT, WT_List, central_platform_locations, cable_list)

    # ------------------------------------Run------------------------------------------------------------------
