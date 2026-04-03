export default function ThreatDossier({ node, analysisId }) {
  if (!node?.node) return null
  const query = `analysis_id=${encodeURIComponent(analysisId || '')}`

  async function downloadPdf() {
    if (!analysisId) return
    const res = await fetch(`/api/node/${encodeURIComponent(node.node)}/dossier?${query}`)
    if (!res.ok) return
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `phantom_trace_${node.node}.pdf`
    a.click()
    URL.revokeObjectURL(url)
  }

  async function downloadSigma() {
    if (!analysisId) return
    const res = await fetch(`/api/node/${encodeURIComponent(node.node)}/sigma?${query}`)
    if (!res.ok) return
    const text = await res.text()
    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `phantom_trace_${node.node}.yml`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div>
      <h3 className="font-mono text-xs text-slate-300">THREAT DOSSIER</h3>
      <div className="mt-2 flex gap-2">
        <button onClick={downloadPdf} disabled={!analysisId} className="rounded-md border border-danger/50 bg-danger/15 px-3 py-2 font-mono text-xs text-red-100 hover:bg-danger/25 disabled:cursor-not-allowed disabled:opacity-40">
          DOWNLOAD PDF
        </button>
        <button onClick={downloadSigma} disabled={!analysisId} className="rounded-md border border-neon/50 bg-neon/10 px-3 py-2 font-mono text-xs text-green-100 hover:bg-neon/20 disabled:cursor-not-allowed disabled:opacity-40">
          EXPORT SIGMA
        </button>
      </div>
    </div>
  )
}
