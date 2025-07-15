const baseURL =import.meta.env.VITE_API_URL;

export async function fetchaccidentCountOfTopFactorForTheDay() {
  const res = await fetch('http://localhost:3000/accidentCountOfTopFactorOfDay');
  if (!res.ok) throw new Error('Failed to fetch The top Factor of the day accident Count');
  return res.json();
}

export async function fetchaccidentCountOfTopFactorForTheWeek() {
  const res = await fetch(`${baseURL}/accidentCountOfTopFactorOfWeek`);
  if (!res.ok) throw new Error('Failed to fetch the top factor of the week accident count');
  return res.json();
}

export async function fetchaccidentCountOfTopFactorForTheMonth() {
  const res = await fetch(`${baseURL}/accidentCountOfTopFactorOfMonth`);
  if (!res.ok) throw new Error('Failed to fetch the top factor of the month accident count');
  return res.json();
}

export async function fetchaccidentCountOfTopFactorForTheYear() {
  const res = await fetch(`${baseURL}/accidentCountOfTopFactorOfYear`);
  if (!res.ok) throw new Error('Failed to fetch the top factor of the year accident count');
  return res.json();
}

export async function fetchPeakAccidentTimeStats(period, factor) {
  const res = await fetch(`${baseURL}/accidents/peakTimeStatistics?period=${period}&factor=${factor}`);
  if (!res.ok) throw new Error(`Failed to fetch peak accident time statistics for ${factor} during ${period}`);
  const data = await res.json();
  return data;
}

