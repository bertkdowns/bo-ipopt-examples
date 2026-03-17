from ahuora_builder.flowsheet_manager import FlowsheetManager
from idaes.core.util import DiagnosticsToolbox
from pyomo.environ import SolverFactory
from idaes.core.scaling.util import (
    get_jacobian, report_scaling_factors, unscaled_variables_generator, 
    unscaled_constraints_generator
)
from idaes.core.util.scaling import get_scaling_factor, set_scaling_factor, constraint_scaling_transform
from helper_methods.generate_graph import generate_graph
from idaes.core.util.scaling import badly_scaled_var_generator, extreme_jacobian_columns, extreme_jacobian_rows
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
        if var.local_name == "work":
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
        if var.local_name == "work":
            set_scaling_factor(var,1e-7)
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
    #     # else:
        #     print("No scaling factor for variable " + var.name)
    
    # for cons in unscaled_constraints_generator(m):
    #     if cons.local_name == "overall_energy_balance[0.0]":
    #         set_scaling_factor(cons,1e-8)
    #     if cons.local_name == "enthalpy_balances[0.0]":
    #         set_scaling_factor(cons,1e-7)
    #     if cons.local_name.startswith("enthalpy_mixing_equations"):
    #         set_scaling_factor(cons,1e-7)
    #     if cons.local_name.startswith("molar_enthalpy_splitting_eqn"):
    #         set_scaling_factor(cons,1e-7)
    #     if cons.local_name.startswith("heat_duty"):
    #         set_scaling_factor(cons,1e-7)
    #     if cons.local_name.startswith("ratioP"):
    #         set_scaling_factor(cons,1e-5)
    #     if cons.local_name.startswith("ratioP_calculation"):
    #         set_scaling_factor(cons,1)
    #     if cons.local_name.startswith("pressure_balance"):
    #         set_scaling_factor(cons,1e-5)
    #     if cons.local_name.startswith("equality_constraint"):
    #         set_scaling_factor(cons,1e-2)
    #     if cons.local_name.startswith("pressure_equality"):
    #         set_scaling_factor(cons,1e-5)
    #     if cons.local_name.startswith("eq_temperature_bubble"):
    #         set_scaling_factor(cons,1e-5)
    #     if cons.local_name.startswith("eq_outlet_enth_mol"):
    #         set_scaling_factor(cons,1e-5)
    #     if cons.local_name.startswith("enth_mol_equality"):
    #         set_scaling_factor(cons,1e-5)
    #     if cons.local_name.startswith("flow_mol_equality"):
    #         set_scaling_factor(cons,1e-3)
    #     if cons.local_name.startswith("component_flow_balances"):
    #         set_scaling_factor(cons,1e-3)
    #     if cons.local_name.startswith("total_flow_balance"):
    #         set_scaling_factor(cons,1e-3)
    #     if cons.local_name.startswith("deltaP_inverted_constraint"):
    #         set_scaling_factor(cons,1e-4)
    #     if cons.local_name.startswith("eq_phase_frac"):
    #         set_scaling_factor(cons,1e-2)
    #     if cons.local_name.startswith("eq_mole_frac_tbub"):
    #         set_scaling_factor(cons,1e-3)
    #     if cons.local_name.startswith("equilibrium_constraint"):
    #         set_scaling_factor(cons,1e-5)
    #     if cons.local_name.startswith("eq_outlet_combined_enthalpy"):
    #         set_scaling_factor(cons,1e-5)
    #     if cons.local_name.startswith("eq_power_out"):
    #         set_scaling_factor(cons,1e-7)
    #     if cons.local_name.startswith("heat_transfer_equation"):
    #         set_scaling_factor(cons,1e-4)
    #     if cons.local_name.startswith("unit_heat_balance"):
    #         set_scaling_factor(cons,1e-8)
    #     if cons.local_name.startswith("saturated_vap_pressure_eq"):
    #         set_scaling_factor(cons,1e-6)
    #     if cons.local_name.startswith("eq_steam_cooled_pressure"):
    #         set_scaling_factor(cons,1e-6)
    #     if cons.local_name.startswith("eq_mixed_pressure"):
    #         set_scaling_factor(cons,1e-6)
    #     if cons.local_name.startswith("eq_outlet_pressure"):
    #         set_scaling_factor(cons,1e-6)
    #     if cons.local_name.startswith("eq_momentum_balance"):
    #         set_scaling_factor(cons,1e-6) # pressure balance
    #     if cons.local_name.startswith("intlet_water_momentum_balance"): # tim needs to fix his naming
    #         set_scaling_factor(cons,1e-6)
    #     if cons.local_name.startswith("ratioP_calculation"):
    #         set_scaling_factor(cons,1e-6) # pressure ratio is calculated as a function of pressure.
    #     if cons.local_name.startswith("saturated_vap_enthalpy"):
    #         set_scaling_factor(cons,1e-5) # pressure ratio is calculated as a function of pressure.
    #     if cons.local_name.startswith("overall_momentum_balance"):
    #         set_scaling_factor(cons,1e-6) # pressure ratio is calculated as a function of pressure.
    #     if cons.local_name.startswith("willans_line_eq"):
    #         set_scaling_factor(cons,1e-8) #similar scale to the amount of work being produced. 
    #     if cons.local_name.startswith("electrical_energy_balance"):
    #         set_scaling_factor(cons,1e-8) #similar scale to the amount of work being produced. 
    #     if cons.local_name.startswith("inlets_to_mixed_state_energy_balance"):
    #         set_scaling_factor(cons,1e-8) #similar scale to the amount of work being produced. 
    #     if cons.local_name.startswith("mixed_state_to_out"):
    #         set_scaling_factor(cons,1e-8) #similar scale to the amount of work being produced. 
    #     if cons.local_name.startswith("zero_work_equation"):
    #         set_scaling_factor(cons,1e-6) # this equation constraints the work to be zero. 
    #     if cons.local_name.startswith("actual_work"):
    #         set_scaling_factor(cons,1e-6) 
    #     if cons.local_name.startswith("willans_slope_calculation"):
    #         set_scaling_factor(cons,1e0) # TODO: Double check appropriate scale for this.
    #     if cons.local_name.startswith("equality_constraint"):
    #         set_scaling_factor(cons,1e-3) # this is a generic equality constraint, which can be on a range of scales, but 1e-2 is probably a good starting point.
    #     if cons.local_name.startswith("molar_enthalpy_equality_eqn"):
    #         set_scaling_factor(cons,1e-4)
    #     scaling_factor = get_scaling_factor(cons)

    

    print("BADLY SCALED VARIABLES:")
    for var, current_absolute_scaled in badly_scaled_var_generator(m):
        print(f"{var.local_name:<90}   {pyo.value(var):<14.4f}  {(get_scaling_factor(var) or 1) :<10.4f}   {current_absolute_scaled:<10.4f}")
    

    # opt = SolverFactory('ipopt')
    # opt.options["nlp_scaling_method"] = "user-scaling"
    #opt.options["mu_strategy"] = "adaptive"
    ##opt.options["linear_solver"] = "ma57"
    #opt.options["hessian_approximation"] = "limited-memory"
    #opt.options["expect_infeasible_problem"] = True
    ##opt.options["neg_curv_test_tol"] = 1e-11
    ##opt.options["linear_scaling_on_demand"] = True
    #opt.options["warm_start_init_point"] = "yes"
    # try:
    #     results = opt.solve(m, tee=True)
    # except:
    #     print("Error occurred while solving the model.")

    # dt = DiagnosticsToolbox(m)
    # st = dt.prepare_svd_toolbox()
    # dt.report_numerical_issues()
    # dt.display_variables_with_extreme_jacobians()
    # dt.display_constraints_with_extreme_jacobians()

    # st.display_constraints_including_variable(getattr(m.fs,"Phase Separator1_1627493").mixed_state[0.0].pressure)
    # st.display_variables_in_constraint(getattr(m.fs,"Phase Separator1_1627493").molar_enthalpy_splitting_eqn[0.0,"outlet_1"])

    # generate_graph(m, graph_path="steam_system_scaled_graph.html")
    
    

