'use client';

import { useState } from 'react';

type EngineState = {
  epoch: number;
  cognitiveLoad: number;
  quantumCoherence: number;
  neuralActivity: number;
  securityLevel: number;
  ethicalAlignment: number;
  strategicReadiness: number;
  timestamp: string;
};

export default function AttestationTerminal(props: {
  state: EngineState;
  completion: number;
  engineIndex: number;
  onAttested: (att: { signature: string; publicKeyPem: string; digestHex: string; }) => void;
  onRandomize: () => void;
  onComplete: () => void;
}) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const guardianToken = typeof window !== 'undefined' ? localStorage.getItem('GUARDIAN_TOKEN') || '' : '';

  async function attest() {
    setBusy(true);
    setError(null);
    try {
      const res = await fetch('/api/attest', {
        method: 'POST',
        headers: {
          'content-type': 'application/json',
          'x-guardian-token': guardianToken || ''
        },
        body: JSON.stringify(props.state)
      });
      if (!res.ok) {
        const j = await res.json().catch(() => ({}));
        throw new Error(j.error || `HTTP ${res.status}`);
      }
      const j = await res.json();
      props.onAttested(j);
    } catch (e: any) {
      setError(e.message || 'Unknown error');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={{ background: 'rgba(255,255,255,0.03)', padding: 16, borderRadius: 14, border: '1px solid rgba(255,255,255,0.1)' }}>
      <h2 style={{ marginTop: 0 }}>Cognitive Attestation</h2>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
        <Meter label="Cognitive Load" value={props.state.cognitiveLoad} />
        <Meter label="Quantum Coherence" value={props.state.quantumCoherence} />
        <Meter label="Neural Activity" value={props.state.neuralActivity} />
        <Meter label="Security Level" value={props.state.securityLevel} />
        <Meter label="Ethical Alignment" value={props.state.ethicalAlignment} />
        <Meter label="Strategic Readiness" value={props.state.strategicReadiness} />
      </div>

      <div style={{ display: 'flex', gap: 10, marginTop: 14 }}>
        <button onClick={props.onRandomize} disabled={busy} style={btnStyle}>Randomize</button>
        <button onClick={props.onComplete} disabled={busy} style={btnStyle}>Advance to Completion</button>
        <button onClick={attest} disabled={busy} style={btnStylePrimary}>
          {busy ? 'Attesting…' : 'Generate Cognitive Attestation'}
        </button>
      </div>

      <div style={{ marginTop: 12, display: 'flex', gap: 20, alignItems: 'center' }}>
        <Stat label="Simulation Completion" value={`${props.completion.toFixed(1)}%`} />
        <Stat label="Engine Index" value={`${props.engineIndex.toFixed(1)} (baseline 100)`} />
      </div>

      {error && <p style={{ color: '#ff8080', marginTop: 10 }}>Error: {error}</p>}
      <p style={{ fontSize: 12, opacity: 0.75, marginTop: 8 }}>
        Tip: Set your <code>GUARDIAN_TOKEN</code> in <code>localStorage</code> to call APIs in protected mode.
      </p>
    </div>
  );
}

function Meter({ label, value }: { label: string; value: number }) {
  const pct = Math.round(value * 100);
  return (
    <div style={{ background: 'rgba(255,255,255,0.04)', padding: 10, borderRadius: 12 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
        <span style={{ fontSize: 12, opacity: 0.8 }}>{label}</span>
        <span style={{ fontSize: 12, opacity: 0.9 }}>{pct}%</span>
      </div>
      <div style={{ width: '100%', height: 10, background: 'rgba(255,255,255,0.08)', borderRadius: 9999 }}>
        <div style={{ width: `${pct}%`, height: '100%', background: 'linear-gradient(90deg, #2fd6ff, #30f5a4)', borderRadius: 9999 }} />
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ background: 'rgba(255,255,255,0.05)', padding: '8px 10px', borderRadius: 10, border: '1px solid rgba(255,255,255,0.1)' }}>
      <div style={{ fontSize: 11, opacity: 0.75 }}>{label}</div>
      <div style={{ fontSize: 14, fontWeight: 700 }}>{value}</div>
    </div>
  );
}

const btnStyle: React.CSSProperties = {
  background: 'rgba(255,255,255,0.08)',
  border: '1px solid rgba(255,255,255,0.15)',
  color: 'white',
  padding: '8px 10px',
  borderRadius: 10,
  cursor: 'pointer'
};

const btnStylePrimary: React.CSSProperties = {
  ...btnStyle,
  background: 'linear-gradient(120deg, rgba(50,180,255,0.3), rgba(50,255,210,0.25))',
  border: '1px solid rgba(255,255,255,0.2)'
};