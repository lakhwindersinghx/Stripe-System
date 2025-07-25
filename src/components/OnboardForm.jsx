import { useState } from 'react';
import axios from 'axios';

export default function OnboardForm() {
  const [email, setEmail] = useState('');

  const handleSubmit = async e => {
    e.preventDefault();
    const res = await axios.post(`${import.meta.env.VITE_BACKEND_URL}/onboard`, { email });
    window.location.href = res.data.url;
  };

  return (
    <div className="p-6 max-w-md mx-auto">
      <h2 className="text-xl font-semibold mb-4">Onboard as a Temp</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          className="border p-2 w-full"
          type="email"
          placeholder="you@example.com"
          value={email}
          onChange={e => setEmail(e.target.value)}
        />
        <button type="submit" className="bg-indigo-600 text-white px-4 py-2 rounded">
          Start Onboarding
        </button>
      </form>
    </div>
  );
}
