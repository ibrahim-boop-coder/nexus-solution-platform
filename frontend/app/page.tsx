"use client";
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Login() {
  const [pin, setPin] = useState("");
  const router = useRouter();

  const verify = (e: any) => {
    e.preventDefault();
    // Static verification - Use process.env.NEXT_PUBLIC_PIN in production
    if (pin === "nexus2024") {
      router.push('/dashboard');
    } else {
      alert("Access Denied");
    }
  };

  return (
    <div className="h-screen bg-black flex items-center justify-center">
      <form onSubmit={verify} className="text-center">
        <h2 className="text-indigo-500 font-bold mb-4 tracking-tighter text-xl">NEXUS_ENCRYPTED_GATE</h2>
        <input 
          type="password" 
          autoFocus
          className="bg-transparent border-b-2 border-indigo-900 outline-none text-center text-2xl tracking-widest w-64 focus:border-indigo-500 transition-all text-white"
          onChange={(e) => setPin(e.target.value)}
        />
      </form>
    </div>
  );
}