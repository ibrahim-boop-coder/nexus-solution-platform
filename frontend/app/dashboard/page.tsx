"use client";
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const categories = [
  { id: 'Development', title: 'Software Development', icon: '💻' },
  { id: 'Design', title: 'UI/UX Design', icon: '🎨' },
  { id: 'Defense', title: 'Cybersecurity Defense', icon: '🛡️' },
];

export default function Dashboard() {
  const [loading, setLoading] = useState(false);
  const [leads, setLeads] = useState<any[]>([]);

  const fetchLeads = async (category: string) => {
    setLoading(true);
    try {
      // Jab backend live hoga toh yahan Render ka link aayega
      const res = await axios.post('https://nexus-solution-platform.onrender.com/api/generate-leads', { category });
      setLeads(res.data);
    } catch (err) {
      console.error("Scraping failed", err);
    } finally {
      setLoading(false);
    }
  };

  const exportToCSV = () => {
    const csvContent = "data:text/csv;charset=utf-8," 
      + ["Name,Company,Email", ...leads.map(l => `${l.name},${l.company},${l.email}`)].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "nexus_leads.csv");
    document.body.appendChild(link);
    link.click();
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <header className="mb-12 flex justify-between items-center">
        <h1 className="text-3xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400">
          NEXUS SOLUTION - COMMAND CENTER
        </h1>
        {leads.length > 0 && (
          <button onClick={exportToCSV} className="bg-emerald-600 px-4 py-2 rounded-md hover:bg-emerald-500 transition-colors font-bold">
            Export CSV
          </button>
        )}
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        {categories.map((cat) => (
          <motion.div
            key={cat.id} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
            onClick={() => fetchLeads(cat.id)}
            className="cursor-pointer bg-slate-900 border border-slate-800 p-6 rounded-xl text-center hover:border-indigo-500 transition-colors shadow-lg"
          >
            <span className="text-4xl mb-4 block">{cat.icon}</span>
            <h3 className="text-xl font-bold">{cat.title}</h3>
          </motion.div>
        ))}
      </div>

      <AnimatePresence>
        {loading ? (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-indigo-500 mx-auto mb-4"></div>
            <p className="text-slate-400 tracking-widest animate-pulse">EXTRACTING VERIFIED LEADS...</p>
          </motion.div>
        ) : (
          leads.length > 0 && (
            <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900/50 shadow-2xl">
              <table className="w-full text-left">
                <thead className="bg-slate-800/80">
                  <tr>
                    <th className="p-4 font-semibold text-indigo-300">Name</th>
                    <th className="p-4 font-semibold text-indigo-300">Company</th>
                    <th className="p-4 font-semibold text-indigo-300">Verified Email</th>
                    <th className="p-4 font-semibold text-indigo-300">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {leads.map((lead, i) => {
                    // Check if email ends with premium domains
                    const isPremium = lead.email.endsWith('.io') || lead.email.endsWith('.ai') || lead.email.endsWith('.tech');
                    return (
                      <tr key={i} className="border-t border-slate-800/50 hover:bg-slate-800/40 transition-colors">
                        <td className="p-4">{lead.name}</td>
                        <td className="p-4">{lead.company}</td>
                        <td className="p-4 text-cyan-400 font-mono text-sm">{lead.email}</td>
                        <td className="p-4">
                          {isPremium ? (
                            <span className="bg-amber-500/10 text-amber-400 px-3 py-1 rounded-full text-xs font-bold border border-amber-500/20">
                              🔥 High Priority
                            </span>
                          ) : (
                            <span className="bg-slate-800 text-slate-300 px-3 py-1 rounded-full text-xs border border-slate-700">
                              Standard
                            </span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )
        )}
      </AnimatePresence>
    </div>
  );
}