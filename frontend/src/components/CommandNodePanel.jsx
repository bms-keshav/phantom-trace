export default function CommandNodePanel({ node, totalNodes }) {
  if (!node) {
    return <div className="font-mono text-xs text-slate-400">No node selected</div>
  }

  const conf = Number(node.confidence_pct || 0)
  const riskColor = conf >= 70 ? 'text-red-300' : conf >= 40 ? 'text-amber-300' : 'text-slate-300'

  return (
    <div>
      <div className="flex items-center justify-between">
        <h2 className="font-mono text-sm text-neon">COMMAND NODE CANDIDATE</h2>
        <span className={`font-mono text-xs ${riskColor}`}>{conf.toFixed(1)}%</span>
      </div>

      <div className="mt-3 rounded-lg border border-slate-800 bg-panelSoft p-3">
        <p className="font-mono text-lg text-slate-100">{node.node}</p>
        <div className="mt-2 h-2 w-full overflow-hidden rounded bg-slate-800">
          <div className="h-full bg-gradient-to-r from-amber-400 to-danger" style={{ width: `${Math.min(conf, 100)}%` }} />
        </div>
        <div className="mt-3 grid grid-cols-2 gap-2 font-mono text-xs text-slate-300">
          <div>Requests: {node.request_count}</div>
          <div>Destinations: {node.unique_destinations}</div>
          <div>Final Score: {node.final_score}</div>
          <div>Nodes in Graph: {totalNodes ?? '-'}</div>
        </div>
      </div>
    </div>
  )
}
