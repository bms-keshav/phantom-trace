import { useMemo, useState } from 'react'
import CommandNodePanel from './components/CommandNodePanel'
import KillChainTimeline from './components/KillChainTimeline'
import MetadataPanel from './components/MetadataPanel'
import NetworkGraph from './components/NetworkGraph'
import ScoreRadar from './components/ScoreRadar'
import ThreatDossier from './components/ThreatDossier'

export default function App() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [analysis, setAnalysis] = useState(null)
  const [selectedNodeId, setSelectedNodeId] = useState('')
  const [scrub, setScrub] = useState(100)

  const ranked = analysis?.ranked_nodes ?? []
  const allNodes = analysis?.all_nodes ?? ranked
  const topNode = analysis?.top_node?.node ?? ''

  const selectedNode = useMemo(() => {
    if (!analysis) return null
    const id = selectedNodeId || topNode
    return allNodes.find((n) => n.node === id) || analysis.top_node
  }, [analysis, allNodes, selectedNodeId, topNode])

  async function handleUpload(file) {
    if (!file) return
    setError('')
    setLoading(true)

    try {
      const form = new FormData()
      form.append('file', file)
      const res = await fetch('/api/analyze', {
        method: 'POST',
        body: form,
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || 'Analysis failed')
      }

      const data = await res.json()
      setAnalysis(data)
      setSelectedNodeId(data?.top_node?.node || '')
      setScrub(100)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-4 md:p-6">
      <div className="mx-auto max-w-[1500px]">
        <header className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold tracking-wide">PHANTOM TRACE</h1>
            <p className="text-slate-300 font-mono text-xs md:text-sm">
              Investigation System · Shadow Controller Attribution
            </p>
          </div>
          <div className="flex items-center gap-3">
            <label className="cursor-pointer rounded-lg border border-neon/40 bg-panelSoft px-4 py-2 font-mono text-xs hover:border-neon">
              {loading ? 'ANALYZING...' : 'UPLOAD LOGS'}
              <input
                type="file"
                accept=".json,.csv,.log,.txt"
                className="hidden"
                onChange={(e) => handleUpload(e.target.files?.[0])}
                disabled={loading}
              />
            </label>
          </div>
        </header>

        {error && (
          <div className="mb-4 rounded-lg border border-danger/50 bg-danger/10 px-3 py-2 font-mono text-xs text-red-200">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 gap-4 xl:grid-cols-5">
          <section className="panel scanline xl:col-span-3 min-h-[520px] p-3">
            <NetworkGraph
              graphData={analysis?.graph}
              topNode={topNode}
              selectedNodeId={selectedNode?.node}
              setSelectedNode={setSelectedNodeId}
              scrubPercent={scrub}
            />
          </section>

          <section className="xl:col-span-2 flex flex-col gap-4">
            <div className="panel p-4">
              <CommandNodePanel node={selectedNode} totalNodes={analysis?.summary_stats?.total_nodes} />
              <div className="mt-4">
                <ScoreRadar node={selectedNode} />
              </div>
              <div className="mt-4">
                <ThreatDossier node={selectedNode} analysisId={analysis?.analysis_id} />
              </div>
            </div>

            <div className="panel p-4">
              <KillChainTimeline scrubPercent={scrub} setScrubPercent={setScrub} timeline={analysis?.timeline || []} />
              <div className="mt-4">
                <MetadataPanel node={selectedNode} />
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}
