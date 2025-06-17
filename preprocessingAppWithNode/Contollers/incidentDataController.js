const validateIncident = require('../Services/validateData');
const kafkaProducer = require('../Services/kafkaProducer');

export const validateAndSendData = async (req, res) => {
  const body = req.body;

  let incidents = [];

  if (Array.isArray(body.data)) {
    incidents = body.data;
  } else if (body && typeof body === 'object') {
    incidents = [body];
  } else {
    return res.status(400).json({ error: "Invalid format. Expected array of incidents or single object." });
  }

  try {
    const validatedIncidents = [];

    for (const incident of incidents) {
      const valid = validateIncident.validateIncident(incident);
      validatedIncidents.push(valid);
    }

    await kafkaProducer.sendMessage(validatedIncidents); 

    res.status(200).json({ message: ` ${validatedIncidents.length} incident(s) accepted and sent to Kafka` });
  } catch (e) {
    console.error(" Validation or Kafka error:", e.message);
    res.status(400).json({ error: "Invalid data", details: e.message });
  }
};
