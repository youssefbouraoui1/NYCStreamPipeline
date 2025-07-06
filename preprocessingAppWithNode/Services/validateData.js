const { v4: uuidv4 } = require('uuid');


function validateData(data) {

  const requiredFields = [
    "crash_date", "crash_time", "borough", "on_street_name", "off_street_name", "cross_street_name",
    "number_of_persons_injured", "number_of_persons_killed",
    "number_of_pedestrians_injured", "number_of_pedestrians_killed",
    "number_of_cyclist_injured", "number_of_cyclist_killed",
    "number_of_motorist_injured", "number_of_motorist_killed",
    "contributing_factor_vehicle_1", "contributing_factor_vehicle_2", "contributing_factor_vehicle_3",
    "collision_id", "vehicle_type_code1", "vehicle_type_code2", "vehicle_type_code_3"
  ];

  for (let field of requiredFields) {
    if (!(field in data)) {
      return `Missing required field: ${field}`;
    }
  }

  const isValidDate = /^\d{4}-\d{2}-\d{2}T/.test(data.crash_date);
  if (!isValidDate) return "Invalid crash_date format. Expected ISO 8601.";

  const validateTime = /^\d{1,2}:\d{2}$/.test(data.crash_time)
  if (!validateTime) return "Invalid crash_time format. Use HH:MM.";

  const numFields = [
    "number_of_persons_injured", "number_of_persons_killed",
    "number_of_pedestrians_injured", "number_of_pedestrians_killed",
    "number_of_cyclist_injured", "number_of_cyclist_killed",
    "number_of_motorist_injured", "number_of_motorist_killed"
  ];


  for (let field of numFields) {
    if (parseInt(data[field])) {
      return field + "must be a number"
    }
  }

  const totalInjured =
    parseInt(data.number_of_pedestrians_injured) +
    parseInt(data.number_of_cyclist_injured) +
    parseInt(data.number_of_motorist_injured);

  if (parseInt(data.number_of_persons_injured) !== totalInjured) {
    return `Injury mismatch: number_of_persons_injured (${data.number_of_persons_injured}) != sum of categories (${totalInjured})`;
  }

  return "Crash data is valid";
}

function validateIncident(data) {
  if (!data.crash_date || !data.crash_time) {
    throw new Error("Missing crash date or time");
  }
  return {
    incident_id: uuidv4(),
    timestamp: data.crash_date && data.crash_time
      ? `${data.crash_date}T${data.crash_time}:00Z` : null,
    crash_date: data.crash_date,
    crash_time: data.crash_time,
    location_id: uuidv4(),
    borough: data.borough || 'UNKNOWN',
    zip_code: data.zip_code || null,
    on_street_name: data.on_street_name || 'UNKNOWN',
    off_street_name: data.off_street_name || 'UNKNOWN',
    cross_street_name: data.cross_street_name || 'UNKNOWN',
    vehicle_type_id: uuidv4(),
    vehicle_types: [
      data.vehicle_type_code1, data.vehicle_type_code2,
      data.vehicle_type_code_3, data.vehicle_type_code_4,
      data.vehicle_type_code_5
    ].filter(v => v),
    cont_factors_id: uuidv4(),
    contributing_factors: [
      data.contributing_factor_vehicle_1, data.contributing_factor_vehicle_2,
      data.contributing_factor_vehicle_3, data.contributing_factor_vehicle_4,
      data.contributing_factor_vehicle_5
    ].filter(f => f),
    number_of_persons_injured: parseInt(data.number_of_persons_injured || 0),
    number_of_persons_killed: parseInt(data.number_of_persons_killed || 0),
    number_of_motorist_injured: parseInt(data.number_of_motorist_injured || 0),
    number_of_motorist_killed: parseInt(data.number_of_motorist_killed || 0),
    number_of_cyclist_injured: parseInt(data.number_of_cyclist_injured || 0),
    number_of_cyclist_killed: parseInt(data.number_of_cyclist_killed || 0),
    number_of_pedestrians_injured: parseInt(data.number_of_pedestrians_injured || 0),
    number_of_pedestrians_killed: parseInt(data.number_of_pedestrians_killed || 0)
  };
}


module.exports = { validateData, validateIncident };
