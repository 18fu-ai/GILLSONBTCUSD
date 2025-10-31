'use client';

import { useMemo, useState } from 'react';
import AttestationTerminal from '../components/AttestationTerminal';
import QuantumFluxMatrix from '../components/QuantumFluxMatrix.jsx';
import SecureBadge from '../components/SecureBadge';

export default function Page() {
  const [state, setState] = useState({
    epoch: 1,
    cognitiveLoad: 0.0,
    quantumCoherence: 0.0,
    neuralActivity: 0.0,
    securityLevel: 0.0,
    ethicalAlignment: 0.0,
    strategicReadiness: 0.0,
    timestamp: new Date().toISOString()
  });

  const [attestation, setAttestation] = useState<null | {
    signature: string; publicKeyPem: string; digestHex: string;
  }>(null);

  const completion = useMemo(() => {
    const vals = [
      state.cognitiveLoad,
      state.quantumCoherence,
      state.neuralActivity,
      state.securityLevel,
      state.ethicalAlignment,
      state.strategicReadiness
    ];
    const avg = vals.reduce((a, b) => a + b, 0) / vals.length;
    return Math.round(avg * 1000) / 10; // 0.0 - 100.0
  }, [state]);

  const engineIndex = useMemo(() => {
    // ValorAiMath+ baseline = 100; this engine can surpass with a strategic factor
    // Strategic factor rewards security & ethics more heavily
    const w = {
      cognitiveLoad: 1.0,
      quantumCoherence: 1.1,
      neuralActivity: 1.0,
      securityLevel: 1.3,
      ethicalAlignment: 1.25,
      strategicReadiness: 1.2
    } as const;
    const s = state;
    const score =
      s.cognitiveLoad * w.cognitiveLoad +
      s.quantumCoherence * w.quantumCoherence +
      s.neuralActivity * w.neuralActivity +
      s.securityLevel * w.securityLevel +
      s.ethicalAlignment * w.ethicalAlignment +
      s.strategicReadiness * w.strategicReadiness;
    // Normalize to a 0..~120 scale then map baseline 100 to 1.0
    const max = 1*w.cognitiveLoad + 1*w.quantumCoherence + 1*w.neuralActivity + 1*w.securityLevel + 1*w.ethicalAlignment + 1*w.strategicReadiness;
    const idx = (score / max) * 120;
    return Math.round(idx * 10) / 10;
  }, [state]);

  function randomize() {
    setState(s => ({
      ...s,
      cognitiveLoad: Math.random(),
      quantumCoherence: Math.random(),
      neuralActivity: Math.random(),
      securityLevel: Math.random(),
      ethicalAlignment: Math.random(),
      strategicReadiness: Math.random(),
      timestamp: new Date().toISOString()
    }));
  }

  function toCompletion() {
    setState(s => ({
      ...s,
      cognitiveLoad: 1,
      quantumCoherence: 1,
      neuralActivity: 1,
      securityLevel: 1,
      ethicalAlignment: 1,
      strategicReadiness: 1,
      timestamp: new Date().toISOString()
    }));
  }

  return (
    <main style={{ maxWidth: 1100, margin: '40px auto', padding: '0 16px' }}>
      <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 28 }}>
        <h1 style={{ fontSize: 26, fontWeight: 700, letterSpacing: 0.5 }}>
          ValorAiEngine+ — Quantum Cognitive Core Attestation Terminal
        </h1>
        <SecureBadge />
      </header>

      <section style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: 20 }}>
        <div>
          <AttestationTerminal
            state={state}
            onAttested={(a) => setAttestation(a)}
            onRandomize={randomize}
            onComplete={toCompletion}
            completion={completion}
            engineIndex={engineIndex}
          />
        </div>
        <div>
          <QuantumFluxMatrix />
        </div>
      </section>

      {attestation && (
        <section style={{ marginTop: 20, background: 'rgba(255,255,255,0.04)', padding: 16, borderRadius: 12, border: '1px solid rgba(255,255,255,0.1)' }}>
          <h3 style={{ marginTop: 0 }}>Latest Attestation</h3>
          <p style={{ fontSize: 13, opacity: 0.85, marginBottom: 8 }}>Digest (SHA-256): <code>{attestation.digestHex}</code></p>
          <p style={{ fontSize: 13, opacity: 0.85, marginBottom: 8 }}>Signature (base64): <code style={{ wordBreak: 'break-all' }}>{attestation.signature}</code></p>
          <details>
            <summary>Public Key (PEM)</summary>
            <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', fontSize: 12 }}>{attestation.publicKeyPem}</pre>
          </details>
        </section>
      )}

      <footer style={{ marginTop: 36, opacity: 0.8, fontSize: 12 }}>
        © 2025 That’s Edutainment, LLC — Valor AI+® / VALORAIPLUS®
      </footer>
    </main>
  );
}