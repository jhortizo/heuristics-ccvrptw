from itertools import product

import pandas as pd
from tqdm import tqdm

from heuristics_ccvrptw.algorithms import (
    apply_repair_method,
    nearest_neighbors_heuristic,
)
from heuristics_ccvrptw.constants import CASES_PER_TYPE
from heuristics_ccvrptw.parse_instances import parse_instance
from heuristics_ccvrptw.plotter import plot_routes
from heuristics_ccvrptw.utils import (
    calculate_cost_function,
    calculate_times_matrix,
    check_routes_are_feasible,
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

    cases = product(
        kinds,
        kind_types,
        range(1, max(CASES_PER_TYPE[k][t] for k in kinds for t in kind_types) + 1),
    )
    instance_names = []
    costs = []
    vehicle_nrs = []
    for kind, kind_type, case_number in tqdm(cases, desc="Running instances"):
        if case_number > CASES_PER_TYPE[kind][kind_type]:
            continue
        instance_name = f"{kind.upper()}{kind_type}{case_number:02d}"
        ref_vehicle_nr = reference_data.loc[
            reference_data["Instance"] == instance_name, "k"
        ].values[0]
        cost, vehicle_nr_obtained, original_vehicle_nr = get_single_solution(
            kind,
            kind_type,
            case_number,
            ref_vehicle_nr=ref_vehicle_nr,
            plot_instance=False,
        )

        instance_names.append(instance_name)
        costs.append(cost)
        vehicle_nrs.append(vehicle_nr_obtained)

    # create dataframe with results
    results = pd.DataFrame(
        {
            "Instance": instance_names,
            "Cost": costs,
            "Vehicle number": vehicle_nrs,
        }
    )
    results.to_csv("results/single_solution.csv", index=False)


if __name__ == "__main__":
    main()