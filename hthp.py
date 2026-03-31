import os
import json
import io
from ahuora_builder.flowsheet_manager import FlowsheetManager
from ahuora_builder_types.flowsheet_schema import FlowsheetSchema
from idaes.core.util.model_diagnostics import DiagnosticsToolbox
from ahuora_builder.methods.property_map_manipulation import update_property
from pyomo.environ import SolverFactory
from idaes.core.solvers.homotopy import homotopy
from pyomo.contrib.community_detection.community_graph import generate_model_graph
from pyomo.core.base.constraint import ConstraintData
import pyomo.environ as pyo
from math import log
from idaes.core.util.scaling import get_scaling_factor
from idaes.core.scaling import AutoScaler
from idaes.core.util.scaling import constraint_scaling_transform
# This uses Keegan's High Temperature Heat Pump model.
INPUT_FILE = "models/hthp.json"

# Get current location (so that we can retrieve .json file with the model data)
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


with open(os.path.join(__location__, INPUT_FILE), 'r') as file:

    data = json.load(file)


# Use the Ahuora Flowsheet builder to build the pyomo model.
flowsheet_schema = FlowsheetSchema.model_validate(data)
flowsheet = FlowsheetManager(flowsheet_schema)
flowsheet.load()
flowsheet.initialise()
assert flowsheet.degrees_of_freedom() == 0, "Degrees of freedom is not 0: " + str(flowsheet.degrees_of_freedom())
flowsheet.report_statistics()


m = flowsheet.model


# We need to scale this constraint in order for IPOPT to solve successfully.
constraint_scaling_transform(m.fs.equality_constraint_341300[0], 1e-5)


opt = SolverFactory('ipopt')
# opt.options["tol"] = 1e-3
results = opt.solve(m, tee=True)
# This doesn't have an objective function or decision variables, because we are solving for an exact solution.


fixed_variables = [
    item 
      for id, prop in flowsheet.properties_map.items()
      if prop.corresponding_constraint != None
      for item in prop.corresponding_constraint
      if item is not None
      and hasattr(item, "name")
]

print("==*************** MODEL INFORMATION *****************==")
print("Fixed variables:")
print([var.name for var in fixed_variables])
for var in fixed_variables:
    print(f"{pyo.value(var):>20}", var)

dt = DiagnosticsToolbox(m)
dt.display_variables_near_bounds()
dt.display_constraints_with_large_residuals()

svd_toolbox = dt.prepare_svd_toolbox()
svd_toolbox.display_variables_in_constraint(m.fs.equality_constraint_341300[0])