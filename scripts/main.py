from heuristics_ccvrptw.parse_instances import parse_instance
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def plot_instance(depot, customers):
    plt.figure()
    plt.plot(depot["x"], depot["y"], "ko")
    plt.plot(customers["x"], customers["y"], "bo")
    plt.show()


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


def nearest_neighbors_heuristic(all_times, customers, capacity):
    routes = []
    t_k_i = []
    pending_customers = customers.copy()

    while len(pending_customers) > 0:
        # print("-- Doing route: ", len(routes) + 1)
        new_route = [0]
        service_start_times = []
        current_time = 0
        current_capacity = 0
        can_add_new_point = True
        while can_add_new_point and (len(pending_customers) > 0):
            times_from_prev = all_times.loc[
                pending_customers.index, new_route[-1]
            ].sort_values(ascending=True)
            for idx in times_from_prev.index:
                this_time = times_from_prev[idx]
                this_customer = customers.loc[idx]
                if (
                    (this_customer["latest"] > current_time + this_time)
                    and (current_capacity + this_customer["demand"] < capacity)
                ):  # if it arrives on time to that place and has enough capacity to supply
                    new_route.append(idx)
                    pending_customers.drop(index=idx, inplace=True)
                    # print("Remaining customers to visit:", len(pending_customers))

                    if current_time + this_time < this_customer["earliest"]:
                        current_time = this_customer[
                            "earliest"
                        ]  # if it arrives earlier than start of the window, needs to wait until it opens
                    else:
                        current_time += (
                            this_time  # else, it just rides and starts the service
                        )

                    service_start_times.append(current_time)
                    current_time += +this_customer["cost"]  # add the service time
                    current_capacity += this_customer["demand"]

                    can_add_new_point = (
                        len(pending_customers) > 0
                    )  # we managed to add a point, so we can move on to the next test only if there are any other points to add
                    break
                else:
                    can_add_new_point = (
                        False  # didn't add a point in any case, we go back to depot
                    )

        new_route.append(0)
        routes.append(new_route)
        t_k_i.append(service_start_times)
    
    return routes, t_k_i


def check_routes_are_feasible(routes, t_k_i, customers, capacity):
    for route, service_start_times in zip(routes, t_k_i):
        feasible = check_route_is_feasible(
            route, service_start_times, customers, capacity
        )
        if not feasible:
            break
    print("Route is feasible" if feasible else "Route is not feasible")
    return feasible


def t_k_i_from_routes(routes, all_times, customers):
    reconstructed_t_k_i = []
    for route in routes:
        current_time = 0
        service_start_times = []
        for i in range(len(route) - 2):
            current_time += all_times.loc[route[i], route[i + 1]]
            if current_time < customers.loc[route[i + 1], "earliest"]:
                current_time = customers.loc[route[i + 1], "earliest"]
            service_start_times.append(current_time)
            current_time += customers.loc[route[i + 1], "cost"]
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


def main():
    # Parse instance
    kind = "rc"
    kind_type = "1"
    case_number = 1
    data = parse_instance(kind, kind_type, case_number)
    _, _, capacity, all_points = data
    customers = all_points.iloc[1:]

    # Plot instance
    # depot = all_points.iloc[0]
    # plot_instance(depot, customers)

    all_times = calculate_times_matrix(all_points)

    # Apply nearest neighbor heuristic
    routes, t_k_i = nearest_neighbors_heuristic(all_times, customers, capacity)

    # Check if routes are indeed feasible
    check_routes_are_feasible(routes, t_k_i, customers, capacity)


if __name__ == "__main__":
    main()
