from heuristics_ccvrptw.parse_instances import parse_instance
from heuristics_ccvrptw.plotter import plot_routes
from heuristics_ccvrptw.utils import (
    calculate_times_matrix,
    check_routes_are_feasible,
    calculate_cost_function,
)

from heuristics_ccvrptw.algorithms import (
    nearest_neighbors_heuristic,
    apply_repair_method,
)


def main():
    kind = "c"
    kind_type = "1"
    case_number = 1
    data = parse_instance(kind, kind_type, case_number)
    _, vehicle_nr, capacity, all_points = data
    customers = all_points.iloc[1:]

    all_times = calculate_times_matrix(all_points)

    routes, t_k_i = nearest_neighbors_heuristic(all_times, customers, capacity)

    check_routes_are_feasible(routes, t_k_i, customers, capacity)

    if len(routes) > vehicle_nr:
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

    cost = calculate_cost_function(t_k_i)
    print("Cost:", cost)
    print("Number of routes:", len(repaired_routes), "Vehicle number:", vehicle_nr)
    plot_routes(repaired_routes, all_points)


if __name__ == "__main__":
    main()
