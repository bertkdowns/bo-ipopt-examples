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
from evaporator_manual_scaling import apply_manual_scaling

INPUT_FILE = "models/hthp_with_effect.json"

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
opt = SolverFactory('ipopt')
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
