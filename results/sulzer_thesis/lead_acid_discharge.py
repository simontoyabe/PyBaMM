#
# Simulations: discharge of a lead-acid battery
#
import matplotlib.pyplot as plt
import numpy as np
import pybamm


def asymptotics_comparison(models, Crates):
    # load parameter values and geometry
    geometry = models[0].default_geometry
    param = models[0].default_parameter_values

    # Process parameters (same parameters for all models)
    for model in models:
        param.process_model(model)
    param.process_geometry(geometry)

    # set mesh
    var = pybamm.standard_spatial_vars
    var_pts = {var.x_n: 5, var.x_s: 5, var.x_p: 5}
    mesh = pybamm.Mesh(geometry, models[-1].default_submesh_types, var_pts)

    # discretise models
    discs = {}
    for model in models:
        disc = pybamm.Discretisation(mesh, model.default_spatial_methods)
        disc.process_model(model)
        # Store discretisation
        discs[model] = disc

    # solve model for range of Crates
    all_variables = {}
    for Crate in Crates:
        all_variables[Crate] = {}
        current = Crate * 17
        param.update({"Typical current [A]": current})
        t_eval = np.linspace(0, 1, 100)
        for model in models:
            param.update_model(model, discs[model])
            solver = model.default_solver
            solver.solve(model, t_eval)
            all_variables[Crate][model] = pybamm.post_process_variables(
                model.variables, solver.t, solver.y, mesh
            )

    return all_variables, t_eval


def plot_voltages(all_variables, t_eval):
    # Plot
    for Crate, models_variables in all_variables.items():
        plt.figure()
        for model, variables in models_variables.items():
            plt.plot(
                variables["Time [h]"](t_eval),
                variables["Terminal voltage [V]"](t_eval),
                label=model.name,
            )
    plt.legend(loc="upper right")
    plt.show()


if __name__ == "__main__":
    models = [
        pybamm.lead_acid.LOQS(),
        pybamm.lead_acid.Composite(),
        # pybamm.lead_acid.NewmanTiedemann(),
    ]
    Crates = [1]
    all_variables, t_eval = asymptotics_comparison(models, Crates)
    plot_voltages(all_variables, t_eval)
