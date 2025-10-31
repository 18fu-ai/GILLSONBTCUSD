export const metadata = {
  title: 'ValorAiEngine+ — Quantum Cognitive Core Attestation Terminal',
  description: 'The official Valor AI+® engine face with attestation, verification, and secure simulation hexagon.'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ background: 'radial-gradient(1200px 600px at 50% -10%, #0b1220, #02060e)', color: 'white' }}>
        {children}
      </body>
    </html>
  );
}