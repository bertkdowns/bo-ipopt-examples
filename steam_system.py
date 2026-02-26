import os
import json
from ahuora_builder.flowsheet_manager import FlowsheetManager
from ahuora_builder_types.flowsheet_schema import FlowsheetSchema
from pyomo.environ import SolverFactory
import pyomo.environ as pyo
from idaes.core.util.model_statistics import degrees_of_freedom
from helper_methods.setup_optimisation import setup_optimisation

# Get current location (so that we can retrieve .json file with the model data)
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


with open(os.path.join(__location__, "models/steam_system.json"), 'r') as file:
    data = json.load(file)


# Use the Ahuora Flowsheet builder to build the pyomo model.
flowsheet_schema = FlowsheetSchema.model_validate(data)
flowsheet = FlowsheetManager(flowsheet_schema)
flowsheet.load()
flowsheet.initialise()
assert flowsheet.degrees_of_freedom() == 0, "Degrees of freedom is not 0: " + str(flowsheet.degrees_of_freedom())
flowsheet.report_statistics()


# This model does solve in ipopt, but the optimisation fails to solve.

m = flowsheet.model
opt = SolverFactory('ipopt')
results = opt.solve(m, tee=True)




electrical_work_property_ids = [178784, 178800, 178819, 177231, 177269, 177313, 177357, 177538, 177706, 177876, 177974, 178002, 177985, 179307, 179372]
electrical_work_properties = [next(iter(flowsheet.properties_map.get(p_id).component.values())) for p_id in electrical_work_property_ids]


m.fs.objective = pyo.Objective(expr=sum(electrical_work_properties),sense=pyo.minimize)
# This objective should be negative, as we are producing electrical work, and should get more negative as it optimises.


# Load the DoFs from the platform data file:
with open(os.path.join(__location__, "models/optimisation_degrees_of_freedom.json"), 'r') as file:
    dofs = json.load(file)



decision_variables = setup_optimisation(m,flowsheet, dofs)


print("Model",m)
print("Objective function:", m.fs.objective)
print("Decision variables: ", decision_variables)
print("Degrees of freedom before optimisation: ", degrees_of_freedom(m))
print("Number of decision variables: ", len(decision_variables), "(Should be the same as the DOF)")



