import matplotlib.pyplot as plt


def plot_instance(depot, customers):
    plt.figure()
    plt.plot(depot["x"], depot["y"], "ko")
    plt.plot(customers["x"], customers["y"], "bo")
    plt.show()


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
