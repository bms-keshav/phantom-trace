export default function MetadataPanel({ node }) {
  if (!node) return null

  const fp = node.fingerprint_detail || {}
  const beacon = node.beacon_detail || {}

  return (
    <div>
      <h3 className="font-mono text-xs text-slate-300">METADATA PATTERN ANALYSIS</h3>
      <div className="mt-2 rounded-lg border border-slate-800 bg-panelSoft p-3 font-mono text-xs text-slate-300">
        <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
          <div>Header repetition: {fp.header_repetition_score}</div>
          <div>UA score: {fp.ua_score}</div>
          <div>Top UA: {fp.top_ua || '-'}</div>
          <div>Unique UAs: {fp.unique_user_agents}</div>
          <div>Dominant period: {beacon.dominant_period_sec ?? '-'}s</div>
          <div>IAT std: {beacon.iat_std ?? '-'}</div>
          <div>Spectral ratio: {beacon.spectral_ratio ?? '-'}</div>
          <div>Dominant freq: {beacon.dominant_freq_hz ?? '-'} Hz</div>
        </div>
      </div>
    </div>
  )
}
