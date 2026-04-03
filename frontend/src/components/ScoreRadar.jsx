import { PolarAngleAxis, PolarGrid, Radar, RadarChart, ResponsiveContainer } from 'recharts'

export default function ScoreRadar({ node }) {
  if (!node) return null

  const bd = node.breakdown || {}
  const data = [
    { metric: 'Centrality', value: Number(bd.centrality || 0) },
    { metric: 'Beaconing', value: Number(bd.beacon || 0) },
    { metric: 'Fingerprint', value: Number(bd.fingerprint || 0) },
    { metric: 'Coordination', value: Number(bd.coordination || 0) },
    { metric: 'Volume', value: Number(bd.volume || 0) },
  ]

  return (
    <div>
      <h3 className="mb-2 font-mono text-xs text-slate-300">ATTRIBUTION BREAKDOWN</h3>
      <div className="h-[220px] rounded-lg border border-slate-800 bg-panelSoft p-2">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data} outerRadius="72%">
            <PolarGrid stroke="rgba(148,163,184,0.3)" />
            <PolarAngleAxis dataKey="metric" tick={{ fill: '#cbd5e1', fontSize: 11 }} />
            <Radar name="score" dataKey="value" stroke="#0ef3b8" fill="#0ef3b8" fillOpacity={0.35} />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
