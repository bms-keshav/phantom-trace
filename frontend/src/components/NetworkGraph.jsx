import { useMemo, useRef } from 'react'
import ForceGraph2D from 'react-force-graph-2d'

function scoreToColor(score) {
  if (score > 0.7) return '#ff4a5e'
  if (score >= 0.4) return '#ffb454'
  return '#95a0ad'
}

export default function NetworkGraph({ graphData, topNode, selectedNodeId, setSelectedNode, scrubPercent }) {
  const fgRef = useRef(null)

  const filteredGraph = useMemo(() => {
    if (!graphData?.nodes?.length) return { nodes: [], links: [] }

    const links = graphData.links || []
    const minTs = Math.min(...links.map((l) => l.first_seen_ts || 0))
    const maxTs = Math.max(...links.map((l) => l.first_seen_ts || 0))
    const scrubTs = minTs + ((maxTs - minTs) * scrubPercent) / 100

    const visibleLinks = links.filter((e) => (e.first_seen_ts || 0) <= scrubTs)
    const visibleNodeSet = new Set()
    visibleLinks.forEach((l) => {
      visibleNodeSet.add(l.source)
      visibleNodeSet.add(l.target)
    })

    const visibleNodes = graphData.nodes.filter((n) => visibleNodeSet.has(n.id) || n.id === topNode)
    return { nodes: visibleNodes, links: visibleLinks }
  }, [graphData, scrubPercent, topNode])

  if (!graphData?.nodes?.length) {
    return (
      <div className="flex h-[500px] items-center justify-center font-mono text-sm text-slate-400">
        Upload logs to render attack graph
      </div>
    )
  }

  return (
    <div className="h-[520px]">
      <ForceGraph2D
        ref={fgRef}
        graphData={filteredGraph}
        nodeLabel={(n) => `${n.id} | Score: ${Number(n.score || 0).toFixed(3)}`}
        nodeColor={(n) => (n.id === selectedNodeId ? '#0ef3b8' : scoreToColor(n.score || 0))}
        nodeVal={(n) => Math.max(2, Number(n.out_degree || 1))}
        linkWidth={(l) => Math.log((l.weight || 1) + 1)}
        linkColor={() => 'rgba(180,190,205,0.28)'}
        onNodeClick={(node) => setSelectedNode(node.id)}
        cooldownTicks={100}
        backgroundColor="rgba(0,0,0,0)"
        nodeCanvasObject={(node, ctx, globalScale) => {
          const label = node.id
          const fontSize = 10 / globalScale

          if (node.id === topNode) {
            ctx.beginPath()
            ctx.arc(node.x, node.y, 10, 0, 2 * Math.PI)
            ctx.strokeStyle = 'rgba(255,74,94,0.45)'
            ctx.lineWidth = 2
            ctx.stroke()
          }

          if (node.id === selectedNodeId) {
            ctx.beginPath()
            ctx.arc(node.x, node.y, 13, 0, 2 * Math.PI)
            ctx.strokeStyle = 'rgba(14,243,184,0.55)'
            ctx.lineWidth = 2
            ctx.stroke()
          }

          ctx.font = `${fontSize}px JetBrains Mono`
          ctx.fillStyle = 'rgba(240,245,250,0.65)'
          ctx.fillText(label, node.x + 6, node.y + 3)
        }}
      />
    </div>
  )
}
