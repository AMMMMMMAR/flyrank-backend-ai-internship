import { useState, useCallback, useEffect } from 'react'
import {
  ReactFlow,
  addEdge,
  applyNodeChanges,
  applyEdgeChanges,
  Background,
  Controls,
  MiniMap,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { runWorkflow } from './workflow'

const initialNodes = [
  {
    id: '1',
    position: { x: 250, y: 100 },
    data: { label: 'Is this a support request?' },
  },
  {
    id: '2',
    position: { x: 100, y: 300 },
    data: { label: 'Route to Support Team' },
  },
  {
    id: '3',
    position: { x: 400, y: 300 },
    data: { label: 'Route to Sales Team' },
  },
]

const initialEdges = [
  { id: 'e1-2', source: '1', target: '2', label: 'YES', style: { stroke: 'green' } },
  { id: 'e1-3', source: '1', target: '3', label: 'NO', style: { stroke: 'red' } },
]

let nodeId = 4

// Get node style based on execution state
function getNodeStyle(nodeId, nodeStates) {
  const state = nodeStates[nodeId]
  if (state === 'thinking') return {
    background: '#fef08a',
    border: '2px solid #eab308',
    borderRadius: '8px',
    padding: '10px',
    minWidth: '160px',
    textAlign: 'center',
    fontWeight: 'bold',
    fontSize: '13px'
  }
  if (state === 'YES') return {
    background: '#bbf7d0',
    border: '2px solid #22c55e',
    borderRadius: '8px',
    padding: '10px',
    minWidth: '160px',
    textAlign: 'center',
    fontWeight: 'bold',
    fontSize: '13px'
  }
  if (state === 'NO') return {
    background: '#fecaca',
    border: '2px solid #ef4444',
    borderRadius: '8px',
    padding: '10px',
    minWidth: '160px',
    textAlign: 'center',
    fontWeight: 'bold',
    fontSize: '13px'
  }
  return {
    background: 'white',
    border: '2px solid #6366f1',
    borderRadius: '8px',
    padding: '10px',
    minWidth: '160px',
    textAlign: 'center',
    fontSize: '13px'
  }
}

export default function App() {
  const [nodes, setNodes] = useState(() => {
    const saved = localStorage.getItem('workflow-nodes')
    return saved ? JSON.parse(saved) : initialNodes
  })
  const [edges, setEdges] = useState(() => {
    const saved = localStorage.getItem('workflow-edges')
    return saved ? JSON.parse(saved) : initialEdges
  })
  const [selectedNode, setSelectedNode] = useState(null)
  const [editText, setEditText] = useState('')
  const [running, setRunning] = useState(false)
  const [executionLog, setExecutionLog] = useState([])
  const [nodeStates, setNodeStates] = useState({})

  // Auto-save to localStorage whenever nodes or edges change
  useEffect(() => {
    localStorage.setItem('workflow-nodes', JSON.stringify(nodes))
  }, [nodes])

  useEffect(() => {
    localStorage.setItem('workflow-edges', JSON.stringify(edges))
  }, [edges])

  // Apply visual styles based on execution state
  const styledNodes = nodes.map(node => ({
    ...node,
    style: getNodeStyle(node.id, nodeStates)
  }))

  const onNodesChange = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
    []
  )

  const onEdgesChange = useCallback(
    (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    []
  )

  const onConnect = useCallback(
    (connection) => {
      const edge = {
        ...connection,
        label: 'YES',
        style: { stroke: 'green' }
      }
      setEdges((eds) => addEdge(edge, eds))
    },
    []
  )

  const addNode = () => {
    const newNode = {
      id: String(nodeId++),
      position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
      data: { label: 'New decision node' },
    }
    setNodes((nds) => [...nds, newNode])
  }

  const onNodeClick = useCallback((event, node) => {
    if (running) return
    setSelectedNode(node)
    setEditText(node.data.label)
  }, [running])

  const saveNodeLabel = () => {
    setNodes((nds) =>
      nds.map((n) =>
        n.id === selectedNode.id
          ? { ...n, data: { ...n.data, label: editText } }
          : n
      )
    )
    setSelectedNode(null)
  }

  const handleRunWorkflow = async () => {
    setRunning(true)
    setExecutionLog([])
    setNodeStates({})

    await runWorkflow(nodes, edges, (step) => {
      if (step.type === 'thinking') {
        setNodeStates(prev => ({ ...prev, [step.nodeId]: 'thinking' }))
        setExecutionLog(prev => [...prev, `🤔 Thinking: "${nodes.find(n => n.id === step.nodeId)?.data.label}"`])
      } else if (step.type === 'answered') {
        setNodeStates(prev => ({ ...prev, [step.nodeId]: step.answer }))
        setExecutionLog(prev => [...prev, `${step.answer === 'YES' ? '✅' : '❌'} Answer: ${step.answer}`])
      } else if (step.type === 'done') {
        setExecutionLog(prev => [...prev, '🎉 Workflow complete!'])
      } else if (step.type === 'error') {
        setExecutionLog(prev => [...prev, `⚠️ Error: ${step.message}`])
      }
    })

    setRunning(false)
  }

  const resetWorkflow = () => {
    if (confirm('Reset to default workflow?')) {
      setNodes(initialNodes)
      setEdges(initialEdges)
      setExecutionLog([])
      setNodeStates({})
      localStorage.removeItem('workflow-nodes')
      localStorage.removeItem('workflow-edges')
    }
  }

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative' }}>

      {/* Toolbar */}
      <div style={{
        position: 'absolute', top: 10, left: 10, zIndex: 10,
        display: 'flex', gap: '8px', alignItems: 'center'
      }}>
        <button onClick={addNode} style={{
          padding: '8px 16px', background: '#6366f1', color: 'white',
          border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold'
        }}>
          + Add Node
        </button>

        <button
          onClick={handleRunWorkflow}
          disabled={running}
          style={{
            padding: '8px 16px',
            background: running ? '#94a3b8' : '#22c55e',
            color: 'white', border: 'none', borderRadius: '6px',
            cursor: running ? 'not-allowed' : 'pointer', fontWeight: 'bold'
          }}
        >
          {running ? '⏳ Running...' : '▶ Run Workflow'}
        </button>

        <button onClick={resetWorkflow} style={{
          padding: '8px 16px', background: '#ef4444', color: 'white',
          border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold'
        }}>
          🔄 Reset
        </button>

        <span style={{
          fontSize: '12px', color: '#64748b', background: 'white',
          padding: '4px 8px', borderRadius: '4px', border: '1px solid #e2e8f0'
        }}>
          💾 Auto-saved
        </span>
      </div>

      {/* Edit panel */}
      {selectedNode && (
        <div style={{
          position: 'absolute', top: 10, right: 10, zIndex: 10,
          background: 'white', padding: '16px', borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.2)', width: '280px'
        }}>
          <h3 style={{ margin: '0 0 8px', fontSize: '14px', fontWeight: 'bold' }}>
            ✏️ Edit Node Prompt
          </h3>
          <textarea
            value={editText}
            onChange={(e) => setEditText(e.target.value)}
            rows={4}
            style={{
              width: '100%', padding: '8px', borderRadius: '4px',
              border: '1px solid #ccc', fontSize: '13px',
              boxSizing: 'border-box', resize: 'vertical'
            }}
          />
          <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
            <button onClick={saveNodeLabel} style={{
              flex: 1, padding: '6px', background: '#22c55e',
              color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer'
            }}>
              Save
            </button>
            <button onClick={() => setSelectedNode(null)} style={{
              flex: 1, padding: '6px', background: '#ef4444',
              color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer'
            }}>
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Execution Log */}
      {executionLog.length > 0 && (
        <div style={{
          position: 'absolute', bottom: 10, left: 10, zIndex: 10,
          background: 'white', padding: '12px', borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.2)', width: '320px',
          maxHeight: '220px', overflowY: 'auto'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <h3 style={{ margin: 0, fontSize: '14px', fontWeight: 'bold' }}>
              📋 Execution Log
            </h3>
            <button
              onClick={() => setExecutionLog([])}
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#94a3b8' }}
            >
              ✕
            </button>
          </div>
          {executionLog.map((log, i) => (
            <div key={i} style={{
              fontSize: '12px', marginBottom: '6px',
              padding: '4px 8px', background: '#f8fafc',
              borderRadius: '4px', borderLeft: '3px solid #6366f1'
            }}>
              {log}
            </div>
          ))}
        </div>
      )}

      <ReactFlow
        nodes={styledNodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  )
}