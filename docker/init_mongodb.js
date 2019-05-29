db.getCollection('simulation_step').createIndex({simulation_id:-1});
db.getCollection('agents').createIndex({simulation_step_id:-1});
