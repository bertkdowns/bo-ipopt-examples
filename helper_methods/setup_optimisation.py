from idaes.core.util.model_diagnostics import Constraint, DiagnosticsToolbox
from pyomo.environ import SolverFactory
from pyomo.core.base.constraint import ConstraintData, IndexedConstraint, ScalarConstraint
import pyomo.environ as pyo
from math import log
from ahuora_builder.methods.adapter import deactivate_components
from pyomo.core.base.expression import ExpressionData, IndexedExpression
from pyomo.core.base.var import IndexedVar, Var, ScalarVar
from ahuora_builder.flowsheet_manager import FlowsheetManager


def setup_optimisation(m: pyo.ConcreteModel, flowsheet: FlowsheetManager, dofs):
    # For the type of dofs see optimisation_degrees_of_freedom.json. 

    # This code is kinda bad, this is mostly taken from our internal code and then amalgamated to use optimisation
    # as we don't support it cleanly in the library yet and in exports.
    decision_variables = []

    for dof in dofs:
        comp = flowsheet.properties_map.get(dof["propertyValue"])

        c = comp.corresponding_constraint

        if c is not None:
            if isinstance(c, ScalarConstraint) or isinstance(c, IndexedConstraint):
                c.deactivate()
            else:
                deactivate_components(c)
        else:
            for i in comp.component.values():
                if isinstance(i, ScalarVar):
                    i.unfix()
                    decision_variables.append(i)
                # Because if not, it is ExpressionData, meaning it is already an expression and doesn't need to be unfixed. (we've already checked if there is a constraint for it above too.)

        
        # TODO: set attributes for upper and lower bounds of property infos. i.e. use propertyinfo id.
        # Var is either a Variable or Expression
        # set the minimum or maximum bounds for this variable if they are enabled
        #self.model.upper_bound_12 =   Constraint(expr= var <= upper_bound_value )

        upper_bound = dof["upper_bound"]
        lower_bound = dof["lower_bound"]

        c = comp.component

        if upper_bound is not None:
            def upper_bound_rule(model,index):
                return c[index] <= upper_bound
            upper_bound_constraint = Constraint(c.index_set(),rule=upper_bound_rule)
            setattr(m,"upper_bound_" + str(dof["id"]), upper_bound_constraint)

        if lower_bound is not None:
            def lower_bound_rule(model,index):
                return c[index] >= lower_bound
            lower_bound_constraint = Constraint(c.index_set(),rule=lower_bound_rule)
            setattr(m,"lower_bound_" + str(dof["id"]), lower_bound_constraint)
        
        if comp.corresponding_constraint is not None:
            # This is a new degree of freedom. add it to our list.
            for property in c.values():
                if isinstance(property, ExpressionData):
                    # if it's an expression, we want to add it to the model as a Var, so that it can be a decision variable in the optimization.
                    var = Var()
                    m.add_component("var_" + str(dof["id"]), var)
                    m.add_component("constraint_" + str(dof["id"]), Constraint(expr=var == property))
                    decision_variables.append(var)
                elif isinstance(property, ScalarVar):
                    # if it's already a Var, and will be unfixed, we can just add it to the decision variables.
                    decision_variables.append(property)
    
    return decision_variables