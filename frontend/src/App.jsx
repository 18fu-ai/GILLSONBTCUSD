// frontend/src/App.jsx
import React, { useEffect, useState } from 'react';
import Chart from 'chart.js/auto';

function ProgressDashboard() {
  const [status, setStatus] = useState(null);
  const [audit, setAudit] = useState({});
  const [rand, setRand] = useState(0);
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    fetch('/api/status')
      .then(r => r.json())
      .then(data => {
        setStatus(data.status);
        setAudit(data.audit);
        setRand(data.audit.quantum_rand);
      });
  }, []);

  useEffect(() => {
    if (status && status.resource_allocation) {
        const ctx = document.getElementById('resourceChart').getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: status.resource_allocation.map(i => i.name),
                datasets: [{
                    data: status.resource_allocation.map(i => i.percent),
                    backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6']
                }]
            }
        });
    }
  }, [status]);

  useEffect(() => {
    const setupWebSocket = () => {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const ws = new WebSocket(`${wsProtocol}//${window.location.host}/ws`);

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.active_users !== undefined) {
                setAnalytics(data);
            } else {
                setStatus(data.status);
                setAudit(data.audit);
            }
        };

        ws.onclose = () => {
            setTimeout(setupWebSocket, 5000);
        };
    };
    setupWebSocket();
  }, []);


  // Secure browser-side quantum/CSPRNG fallback (never Math.random!)
  const browserRand = window.crypto.getRandomValues(new Uint32Array(1))[0] / 2**32;

  if (!status) {
    return <div className="bg-gray-900 text-white min-h-screen flex items-center justify-center">Loading Sovereign Data...</div>;
  }

  const formatUptime = (seconds) => {
    if (seconds === null || seconds === undefined) return '00:00:00';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="bg-gray-900 text-white min-h-screen">
      <header className="p-6 bg-gray-800 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">ValorAI Plus Progress Dashboard</h1>
          <div className="text-blue-200 text-sm">Complete Quantum Chain Audit</div>
        </div>
        <div>
          <div className="bg-green-600 px-3 py-1 rounded">STATUS: ACTIVE DEVELOPMENT</div>
          <div className="text-xs text-blue-200 mt-1">Quantum-RNG: {rand.toFixed(6)} | SHA3: {audit.root_hash?.slice(0,10)}...</div>
        </div>
      </header>

      <main className="p-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {/* Legal */}
            <div className="bg-gray-800 p-6 rounded-lg">
                <h2 className="text-xl font-bold mb-4">Legal</h2>
                <ul>{status.legal.map(item => <li key={item.label}>{item.label}: {item.status}</li>)}</ul>
            </div>
            {/* Technical */}
            <div className="bg-gray-800 p-6 rounded-lg">
                <h2 className="text-xl font-bold mb-4">Technical</h2>
                <ul>{status.technical.map(item => <li key={item.label}>{item.label}: {item.status}</li>)}</ul>
            </div>
            {/* Business */}
            <div className="bg-gray-800 p-6 rounded-lg">
                <h2 className="text-xl font-bold mb-4">Business</h2>
                <ul>{status.business.map(item => <li key={item.label}>{item.label}: {item.status}</li>)}</ul>
            </div>
            {/* Analytics */}
            <div className="bg-gray-800 p-6 rounded-lg">
                <h2 className="text-xl font-bold mb-4">Real-time Analytics</h2>
                {analytics ? (
                    <ul>
                        <li>Active Users: {analytics.active_users}</li>
                        <li>API Calls: {analytics.api_calls}</li>
                        <li>Uptime: {formatUptime(analytics.uptime_seconds)}</li>
                    </ul>
                ) : <p>Connecting to real-time analytics...</p>}
            </div>
        </div>
        <div className="mt-8">
            <canvas id="resourceChart" width="400" height="100"></canvas>
        </div>
      </main>

      <footer className="py-4 bg-gray-800 text-center">
        <span>
          Dashboard SHA3-512 Root: <code>{audit.root_hash}</code> | QuantumRNG: <code>{browserRand.toFixed(8)}</code>
        </span>
        <button
          className="ml-4 p-2 bg-blue-700 rounded"
          onClick={() => window.open('/api/pdf', '_blank')}
        >
          Download Audit PDF/A Evidence
        </button>
      </footer>
    </div>
  );
}

export default ProgressDashboard;
