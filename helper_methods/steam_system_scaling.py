from ahuora_builder.flowsheet_manager import FlowsheetManager
from idaes.core.util import DiagnosticsToolbox
from pyomo.environ import SolverFactory
from idaes.core.scaling.util import (
    get_jacobian, report_scaling_factors, unscaled_variables_generator, 
    unscaled_constraints_generator
)
from idaes.core.util.scaling import get_scaling_factor, set_scaling_factor, constraint_scaling_transform
from helper_methods.generate_graph import generate_graph
from idaes.core.util.scaling import badly_scaled_var_generator, extreme_jacobian_columns, extreme_jacobian_rows, calculate_scaling_factors
import pyomo.environ as pyo


def scale_steam_system(flowsheet: FlowsheetManager):
    m = flowsheet.model

    

    for var in unscaled_variables_generator(m):
        if var.local_name == "pressure":
            set_scaling_factor(var,1e-5)
        if var.local_name == "isentropic_pressure":
            set_scaling_factor(var,1e-6)
        if var.local_name == "deltaP[0.0]":
            set_scaling_factor(var,1e-6)
        if var.local_name == "deltaP_inverted[0.0]":
            set_scaling_factor(var,1e-6)
        if var.local_name.startswith("work"):
            set_scaling_factor(var,1e-7)
        if var.local_name == "flow_mol":
            set_scaling_factor(var,1e-2)
        if var.local_name == "temperature":
            set_scaling_factor(var,1e-2)
        if var.local_name == "enth_mol":
            set_scaling_factor(var,1e-5)
        if var.local_name == "heat[0.0]":
            set_scaling_factor(var,1e-7)
        if var.local_name == "heat_duty_inverted[0.0]":
            set_scaling_factor(var,1e-7)
        if var.local_name == "phase_frac[Liq]":
            set_scaling_factor(var,1e1)
        if var.local_name == "phase_frac[Vap]":
            set_scaling_factor(var,1e1)
        if var.local_name == "power":
            set_scaling_factor(var,1e-6)
        if var.local_name.startswith("work_electrical"):
            set_scaling_factor(var,1e-8)
        if var.local_name == "work_electrical":
            set_scaling_factor(var,1e-7)
        if var.local_name == "willians_intercept":
            set_scaling_factor(var,1e-5)
        if var.local_name == "minimum_pressure":
            set_scaling_factor(var,1e-5)
        if var.local_name.startswith("split_fraction"):
            set_scaling_factor(var,10)
        if var.local_name.startswith("_vap_out_enth_mol"):
            set_scaling_factor(var,1e-6)
        if var.local_name.startswith("_vap_out_enth_mol"):
            set_scaling_factor(var,1e-6)
        if var.local_name.startswith("_minimum_pressure"):
            set_scaling_factor(var,1e-5)
        if var.local_name.startswith("minimum_pressure"):
            set_scaling_factor(var,1e-5)
        if var.local_name.startswith("_willans_intercept"):
            set_scaling_factor(var,1e-6)
        if var.local_name.startswith("willans_intercept"):
            set_scaling_factor(var,1e-5)
        if var.local_name.startswith("willans_slope"):
            set_scaling_factor(var,1e-4)
    #     # else:
        #     print("No scaling factor for variable " + var.name)
    calculate_scaling_factors(m)
    

    print("BADLY SCALED VARIABLES:")
    for var, current_absolute_scaled in badly_scaled_var_generator(m):
        print(f"{var.local_name:<90}   {pyo.value(var):<14.4f}  {(get_scaling_factor(var) or 1) :<10.4f}   {current_absolute_scaled:<10.4f}")
    
    

    opt = SolverFactory('ipopt')
    opt.options["nlp_scaling_method"] = "user-scaling"
    opt.options["max_iter"] = 100
    #opt.options["mu_strategy"] = "adaptive"
    ##opt.options["linear_solver"] = "ma57"
    #opt.options["hessian_approximation"] = "limited-memory"
    #opt.options["expect_infeasible_problem"] = True
    ##opt.options["neg_curv_test_tol"] = 1e-11
    ##opt.options["linear_scaling_on_demand"] = True
    #opt.options["warm_start_init_point"] = "yes"
   

    dt = DiagnosticsToolbox(m)
    st = dt.prepare_svd_toolbox()
    dt.report_numerical_issues()
    dt.display_variables_with_extreme_jacobians()
    # dt.display_constraints_with_extreme_jacobians()

    st.display_constraints_including_variable(getattr(m.fs,"Phase Separator1_1627493").mixed_state[0.0].enth_mol)
    st.display_variables_in_constraint(getattr(m.fs,"Phase Separator1_1627493").molar_enthalpy_splitting_eqn[0.0,"outlet_1"])

    # generate_graph(m, graph_path="steam_system_scaled_graph.html")
    
    try:
        results = opt.solve(m, tee=True)
    except:
        print("Error occurred while solving the model.")
    

