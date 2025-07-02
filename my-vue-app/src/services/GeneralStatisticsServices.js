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