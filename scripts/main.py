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


def apply_repair_method(routes, vehicle_nr, all_times, customers, capacity):
    # Apply repair method
    repaired_routes = routes.copy()
    reparation_feasible = True
    non_repairable_routes = []
    while len(repaired_routes) > vehicle_nr:
        # print("----- -----: Current number of routes:", len(repaired_routes))
        # get smallest route that is not among the non-repairable ones
        reparable_routes = [
            route for route in repaired_routes if route not in non_repairable_routes
        ]

        if len(reparable_routes) == 0:
            reparation_feasible = False
            # print("No more reparable routes")
            break
        else:
            min_route = min(
                reparable_routes,
                key=lambda x: len(x),
            )
            # print("Reallocating route:", min_route)
            before_repairing = repaired_routes.copy()
            for stop in min_route[1:-1]:
                reallocation_feasible = False
                # print("Reassigning stop:", stop)
                # Find closest stops to that one
                stops_not_in_route = [
                    stop for stop in customers.index if stop not in min_route
                ]
                times_from_stop = all_times.loc[stops_not_in_route, stop].sort_values(
                    ascending=True
                )
                for proposed_closest in times_from_stop.index:
                    # Find that stop in the routes
                    proposed_closest_route = [
                        route for route in repaired_routes if proposed_closest in route
                    ][0]
                    proposed_closest_idx = proposed_closest_route.index(
                        proposed_closest
                    )
                    # Check if it is feasible to add that stop to the route
                    new_proposed_route = proposed_closest_route.copy()
                    new_proposed_route.insert(proposed_closest_idx, stop)
                    # print('Trying route:', new_proposed_route)
                    new_service_start_times = service_start_times_from_route(
                        new_proposed_route, all_times, customers
                    )
                    feasible = check_route_is_feasible(
                        new_proposed_route, new_service_start_times, customers, capacity
                    )
                    if feasible:
                        # Update the route
                        # print("Done, old route: ", proposed_closest_route)
                        # print("New route: ", new_proposed_route)
                        repaired_routes.remove(proposed_closest_route)
                        repaired_routes.append(new_proposed_route)
                        reallocation_feasible = True
                        break
                    else:
                        new_proposed_route = proposed_closest_route.copy()
                        new_proposed_route.insert(proposed_closest_idx + 1, stop)
                        # print('Trying route:', new_proposed_route)
                        new_service_start_times = service_start_times_from_route(
                            new_proposed_route, all_times, customers
                        )
                        feasible = check_route_is_feasible(
                            new_proposed_route,
                            new_service_start_times,
                            customers,
                            capacity,
                        )
                        if feasible:
                            # Update the route
                            # print("Done, old route: ", proposed_closest_route)
                            # print("New route: ", new_proposed_route)
                            repaired_routes.remove(proposed_closest_route)
                            repaired_routes.append(new_proposed_route)
                            reallocation_feasible = True
                            break
                if not reallocation_feasible:
                    print(
                        # "Could not reallocate stop ", stop, "route cannot be repaired"
                    )
                    break

            if not reallocation_feasible:
                non_repairable_routes.append(min_route)
                repaired_routes = before_repairing.copy()  # undo the changes
                # print("Route could not be repaired:", min_route)
            else:
                # print("Reallocated route:", min_route)
                repaired_routes.remove(min_route)

    print(
        "Reparation done successfully"
        if reparation_feasible
        else "Reparation not feasible, number of routes:",
        len(repaired_routes),
    )

    return repaired_routes, t_k_i_from_routes(repaired_routes, all_times, customers)


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


def plot_routes(routes, all_points):
    depot = all_points.iloc[0]
    customers = all_points.iloc[1:]
    plt.figure()
    for route in routes:
        route_points = all_points.loc[route]
        plt.plot(route_points["x"], route_points["y"], "-", linewidth=1)
    plt.plot(depot["x"], depot["y"], "rs", markersize=10)
    plt.plot(customers["x"], customers["y"], "bo")
    plt.savefig("images/routes.png")
    plt.show()


def main():
    # Parse instance
    kind = "c"
    kind_type = "1"
    case_number = 1
    data = parse_instance(kind, kind_type, case_number)
    _, vehicle_nr, capacity, all_points = data
    customers = all_points.iloc[1:]

    # Plot instance
    # depot = all_points.iloc[0]
    # plot_instance(depot, customers)

    all_times = calculate_times_matrix(all_points)

    # Apply nearest neighbor heuristic
    routes, t_k_i = nearest_neighbors_heuristic(all_times, customers, capacity)

    # Check if routes are indeed feasible
    check_routes_are_feasible(routes, t_k_i, customers, capacity)

    if len(routes) > vehicle_nr:
        # Apply repair method
        print("Applying repair method")
        repaired_routes, t_k_i = apply_repair_method(
            routes,
            14,
            all_times,
            customers,
            capacity,
        )
        check_routes_are_feasible(repaired_routes, t_k_i, customers, capacity)
    else:
        repaired_routes = routes

    # Calculate cost function
    cost = calculate_cost_function(t_k_i)
    print("Cost:", cost)
    print("Number of routes:", len(repaired_routes), "Vehicle number:", vehicle_nr)
    # Plot routes
    plot_routes(repaired_routes, all_points)


if __name__ == "__main__":
    main()
