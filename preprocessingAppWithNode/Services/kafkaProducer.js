import { Kafka, logLevel } from 'kafkajs';

const KAFKA_BROKER_ADDRESS = process.env.KAFKA_BROKER_ADDRESS || 'kafka:9092';
const KAFKA_TOPIC = process.env.KAFKA_TOPIC || 'crashes';

const kafka = new Kafka({
  clientId: 'incident-producer',
  brokers: [KAFKA_BROKER_ADDRESS],
  logLevel: logLevel.ERROR,
});

const producer = kafka.producer();
let isConnected = false;

async function connectProducer() {
  if (!isConnected) {
    await producer.connect();
    isConnected = true;
    console.log('Kafka producer connected');
  }
}

export const kafkaProducer = async (data) => {
  await connectProducer();

  const messages = Array.isArray(data)
    ? data.map(d => ({ value: JSON.stringify(d) }))
    : [{ value: JSON.stringify(data) }];

  await producer.send({
    topic: KAFKA_TOPIC,
    messages,
  });

  console.log(`Sent ${messages.length} message(s) to Kafka`);
};
