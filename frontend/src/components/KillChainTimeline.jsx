import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

export default function KillChainTimeline({ scrubPercent, setScrubPercent, timeline }) {
  return (
    <div>
      <div className="flex items-center justify-between">
        <h3 className="font-mono text-xs text-slate-300">KILL-CHAIN TIMELINE</h3>
        <span className="font-mono text-xs text-neon">{scrubPercent}%</span>
      </div>

      <input
        type="range"
        min={0}
        max={100}
        value={scrubPercent}
        onChange={(e) => setScrubPercent(Number(e.target.value))}
        className="mt-3 w-full accent-neon"
      />

      <div className="mt-3 h-[140px] rounded-lg border border-slate-800 bg-panelSoft p-2">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={timeline.slice(-80)}>
            <XAxis dataKey="timestamp" hide />
            <YAxis hide />
            <Tooltip
              contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', fontSize: '11px' }}
              labelStyle={{ color: '#cbd5e1' }}
            />
            <Area type="monotone" dataKey="request_count" stroke="#ff4a5e" fill="#ff4a5e" fillOpacity={0.25} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
