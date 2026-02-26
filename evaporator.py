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

INPUT_FILE = "models/evaporator.json"

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


# This model currently fails to solve in ipopt: it says the problem is infeasible.
# However, it is very close to the correct solution, and could be solved with a homotopy method.
# It would be very interesting and useful for us if BO-IPOPT can solve this problem.


m = flowsheet.model
opt = SolverFactory('ipopt')
results = opt.solve(m, tee=True)