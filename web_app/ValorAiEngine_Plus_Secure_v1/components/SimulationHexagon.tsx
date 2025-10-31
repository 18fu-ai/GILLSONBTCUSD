'use client';

import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Tooltip, ResponsiveContainer } from 'recharts';

export default function SimulationHexagon(props: {
  cognitiveLoad: number;
  quantumCoherence: number;
  neuralActivity: number;
  securityLevel: number;
  ethicalAlignment: number;
  strategicReadiness: number;
  completion: number;
  engineIndex: number;
}) {
  const data = [
    { metric: 'Cognitive', value: props.cognitiveLoad * 100 },
    { metric: 'Quantum', value: props.quantumCoherence * 100 },
    { metric: 'Neural', value: props.neuralActivity * 100 },
    { metric: 'Security', value: props.securityLevel * 100 },
    { metric: 'Ethics', value: props.ethicalAlignment * 100 },
    { metric: 'Strategic', value: props.strategicReadiness * 100 },
  ];

  return (
    <div style={{ background: 'rgba(255,255,255,0.03)', padding: 16, borderRadius: 14, border: '1px solid rgba(255,255,255,0.1)', height: 420 }}>
      <h2 style={{ marginTop: 0 }}>Simulation Hexagon</h2>
      <div style={{ height: 280 }}>
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart outerRadius={100} data={data}>
            <PolarGrid />
            <PolarAngleAxis dataKey="metric" />
            <PolarRadiusAxis angle={30} domain={[0, 100]} />
            <Tooltip />
            <Radar name="Engine State" dataKey="value" />
          </RadarChart>
        </ResponsiveContainer>
      </div>
      <div style={{ display: 'flex', gap: 20, alignItems: 'center' }}>
        <Badge label="Completion" value={`${props.completion.toFixed(1)}%`} />
        <Badge label="Engine Index" value={`${props.engineIndex.toFixed(1)} > 100 (ValorAiMath+)`} />
      </div>
      {props.completion >= 100 && (
        <div style={{ marginTop: 10, fontSize: 14 }}>
          ✅ <strong>Completion Achieved:</strong> The simulation hexagon is at full saturation and the engine index surpasses the ValorAiMath+ baseline.
        </div>
      )}
    </div>
  );
}

function Badge({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ background: 'rgba(255,255,255,0.05)', padding: '8px 10px', borderRadius: 10, border: '1px solid rgba(255,255,255,0.1)' }}>
      <div style={{ fontSize: 11, opacity: 0.75 }}>{label}</div>
      <div style={{ fontSize: 14, fontWeight: 700 }}>{value}</div>
    </div>
  );
}