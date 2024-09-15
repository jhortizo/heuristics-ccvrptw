import pandas as pd
import numpy as np


def calculate_times_matrix(all_points):
    all_times = pd.DataFrame(index=all_points.index, columns=all_points.index)
    for i in all_points.index:
        for j in all_points.index:
            all_times.loc[i, j] = np.sqrt(
                (all_points.loc[i, "x"] - all_points.loc[j, "x"]) ** 2
                + (all_points.loc[i, "y"] - all_points.loc[j, "y"]) ** 2
            )
    return all_times


def check_route_is_feasible(route, service_start_times, customers, capacity):
    arrived_within_time_window = True
    capacity_required = customers.loc[route[1:-1], "demand"].sum()
    capacity_is_doable = capacity_required < capacity
    if capacity_is_doable:
        for stop, service_start_time in enumerate(service_start_times):
            this_customer = route[stop + 1]
            arrived_within_time_window = (
                service_start_time >= customers.loc[this_customer, "earliest"]
                and service_start_time < customers.loc[this_customer, "latest"]
            )
            if not arrived_within_time_window:
                break
    feasible = capacity_is_doable and arrived_within_time_window
    return feasible


def check_routes_are_feasible(routes, t_k_i, customers, capacity):
    for route, service_start_times in zip(routes, t_k_i):
        feasible = check_route_is_feasible(
            route, service_start_times, customers, capacity
        )
        if not feasible:
            break
    # print("Route is feasible" if feasible else "Route is not feasible")
    return feasible


def service_start_times_from_route(route, all_times, customers):
    current_time = 0
    service_start_times = []
    for i in range(len(route) - 2):
        current_time += all_times.loc[route[i], route[i + 1]]
        if current_time < customers.loc[route[i + 1], "earliest"]:
            current_time = customers.loc[route[i + 1], "earliest"]
        service_start_times.append(current_time)
        current_time += customers.loc[route[i + 1], "cost"]
    return service_start_times


def t_k_i_from_routes(routes, all_times, customers):
    reconstructed_t_k_i = []
    for route in routes:
        service_start_times = service_start_times_from_route(
            route, all_times, customers
        )
        reconstructed_t_k_i.append(service_start_times)
    return reconstructed_t_k_i


def compare_t_k_is(t_k_i_1, t_k_i_2):
    are_the_same = True
    for k in range(len(t_k_i_1)):
        t_i_1 = t_k_i_1[k]
        t_i_2 = t_k_i_2[k]
        for i in range(len(t_i_1)):
            if t_i_1[i] != t_i_2[i]:
                are_the_same = False
    print("The lists are the same" if are_the_same else "The lists differ")


def calculate_cost_function(t_k_i):
    cost = 0
    for service_start_times in t_k_i:
        cost += sum(service_start_times)
    return cost
