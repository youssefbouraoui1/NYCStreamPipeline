const baseURL =import.meta.env.VITE_API_URL;

export async function fetchAccidentsCount() {
  const res = await fetch('http://localhost:3000/accidents-count');
  if (!res.ok) throw new Error('Failed to fetch accidents count');
  return res.json();
}

export async function fetchInjuriesCount() {
    const res = await fetch('http://localhost:3000/injured-count');
    if(!res.ok) throw new Error('Failed to fetch injured counts');
    return res.json();
    
}


export async function fetchKilledCount() {
    const res = await fetch('http://localhost:3000/killed-count');
    if(!res.ok) throw new Error('Failed to fetch killed count');
    return res.json();
}

export async function fetchPeakTime() {
    const res = await fetch('http://localhost:3000/peak-time');
    if(!res.ok) throw new Error('Failed to fecth peak time');
    return res.json();
}


export async function fecthAccidentCountOverTime(){
    const res = await fetch(`${baseURL}/accidentCountOverTime`);
    if(!res.ok) throw new Error("Failed to fetch accident count over time data");
    return res.json();
}


export async function fecthAccidentCountInjuredAndKilledOverTime(){
    const res = await fetch(`${baseURL}/accidentCountOverTimeAndInjuriesAndKilled`);
    if(!res.ok) throw new Error("Failed to fetch  data");
    return res.json();
}