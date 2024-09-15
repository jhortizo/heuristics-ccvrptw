import pandas as pd

from heuristics_ccvrptw.constants import CASES_PER_TYPE
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


def get_single_solution(
    kind, kind_type, case_number, ref_vehicle_nr=-1, plot_instance=False
):
    data = parse_instance(kind, kind_type, case_number)
    _, vehicle_nr, capacity, all_points = data

    if ref_vehicle_nr == -1:
        ref_vehicle_nr = vehicle_nr  # use the original vehicle number

    customers = all_points.iloc[1:]

    all_times = calculate_times_matrix(all_points)

    routes, t_k_i = nearest_neighbors_heuristic(all_times, customers, capacity)

    check_routes_are_feasible(routes, t_k_i, customers, capacity)

    if len(routes) > vehicle_nr:
        # print("Applying repair method")
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
    # print("Cost:", cost)
    # print("Number of routes:", len(repaired_routes), "Vehicle number:", vehicle_nr)
    if plot_instance:
        plot_routes(repaired_routes, all_points)

    return cost, len(repaired_routes), vehicle_nr


def main():
    reference_data = pd.read_csv("reference_data/instances.csv")
    kinds = ["c", "r", "rc"]
    kind_types = ["1", "2"]

    for kind in kinds:
        for kind_type in kind_types:
            for case_number in range(1, CASES_PER_TYPE[kind][kind_type] + 1):
                instance_name = f"{kind.upper()}{kind_type}{case_number:02d}"
                ref_vehicle_nr = reference_data.loc[
                    reference_data["Instance"] == instance_name, "k"
                ].values[0]
                print(f"Running {instance_name}")
                cost, vehicle_nr_obtained, original_vehicle_nr = get_single_solution(
                    kind,
                    kind_type,
                    case_number,
                    ref_vehicle_nr=ref_vehicle_nr,
                    plot_instance=False,
                )

                reference_data.loc[
                    reference_data["Instance"] == instance_name, "Cost achieved"
                ] = cost

                reference_data.loc[
                    reference_data["Instance"] == instance_name,
                    "Vehicle number obtained",
                ] = vehicle_nr_obtained

                reference_data.loc[
                    reference_data["Instance"] == instance_name,
                    "Original vehicle number",
                ] = original_vehicle_nr

    reference_data.to_csv("results_data/instances.csv", index=False)


if __name__ == "__main__":
    main()
