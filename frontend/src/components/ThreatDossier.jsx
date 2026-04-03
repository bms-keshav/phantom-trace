export default function ThreatDossier({ node }) {
  if (!node?.node) return null

  async function downloadPdf() {
    const res = await fetch(`/api/node/${encodeURIComponent(node.node)}/dossier`)
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
    const res = await fetch(`/api/node/${encodeURIComponent(node.node)}/sigma`)
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
        <button onClick={downloadPdf} className="rounded-md border border-danger/50 bg-danger/15 px-3 py-2 font-mono text-xs text-red-100 hover:bg-danger/25">
          DOWNLOAD PDF
        </button>
        <button onClick={downloadSigma} className="rounded-md border border-neon/50 bg-neon/10 px-3 py-2 font-mono text-xs text-green-100 hover:bg-neon/20">
          EXPORT SIGMA
        </button>
      </div>
    </div>
  )
}
