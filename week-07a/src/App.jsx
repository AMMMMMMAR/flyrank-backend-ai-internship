import { useState, useCallback } from 'react'
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

export default function App() {
  const [nodes, setNodes] = useState(initialNodes)
  const [edges, setEdges] = useState(initialEdges)
  const [selectedNode, setSelectedNode] = useState(null)
  const [editText, setEditText] = useState('')
  const [running, setRunning] = useState(false)
  const [executionLog, setExecutionLog] = useState([])
  const [nodeStates, setNodeStates] = useState({})

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
    setSelectedNode(node)
    setEditText(node.data.label)
  }, [])

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
        setExecutionLog(prev => [...prev, `🤔 Thinking: node ${step.nodeId}`])
      } else if (step.type === 'answered') {
        setNodeStates(prev => ({ ...prev, [step.nodeId]: step.answer }))
        setExecutionLog(prev => [...prev, `✅ Node ${step.nodeId}: ${step.answer}`])
      } else if (step.type === 'done') {
        setExecutionLog(prev => [...prev, '🎉 Workflow complete!'])
      } else if (step.type === 'error') {
        setExecutionLog(prev => [...prev, `❌ Error: ${step.message}`])
      }
    })

    setRunning(false)
  }

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative' }}>
      {/* Toolbar */}
      <div style={{
        position: 'absolute', top: 10, left: 10, zIndex: 10,
        display: 'flex', gap: '8px'
      }}>
        <button
          onClick={addNode}
          style={{
            padding: '8px 16px',
            background: '#6366f1',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          + Add Node
        </button>

        <button
          onClick={handleRunWorkflow}
          disabled={running}
          style={{
            padding: '8px 16px',
            background: running ? '#94a3b8' : '#22c55e',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: running ? 'not-allowed' : 'pointer',
            fontWeight: 'bold'
          }}
        >
          {running ? 'Running...' : '▶ Run Workflow'}
        </button>
      </div>

      {/* Edit panel */}
      {selectedNode && (
        <div style={{
          position: 'absolute', top: 10, right: 10, zIndex: 10,
          background: 'white', padding: '16px', borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.2)', width: '280px'
        }}>
          <h3 style={{ margin: '0 0 8px', fontSize: '14px', fontWeight: 'bold' }}>
            Edit Node Prompt
          </h3>
          <textarea
            value={editText}
            onChange={(e) => setEditText(e.target.value)}
            rows={4}
            style={{
              width: '100%', padding: '8px', borderRadius: '4px',
              border: '1px solid #ccc', fontSize: '13px',
              boxSizing: 'border-box'
            }}
          />
          <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
            <button
              onClick={saveNodeLabel}
              style={{
                flex: 1, padding: '6px',
                background: '#22c55e', color: 'white',
                border: 'none', borderRadius: '4px', cursor: 'pointer'
              }}
            >
              Save
            </button>
            <button
              onClick={() => setSelectedNode(null)}
              style={{
                flex: 1, padding: '6px',
                background: '#ef4444', color: 'white',
                border: 'none', borderRadius: '4px', cursor: 'pointer'
              }}
            >
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
          boxShadow: '0 2px 8px rgba(0,0,0,0.2)', width: '300px',
          maxHeight: '200px', overflowY: 'auto'
        }}>
          <h3 style={{ margin: '0 0 8px', fontSize: '14px', fontWeight: 'bold' }}>
            Execution Log
          </h3>
          {executionLog.map((log, i) => (
            <div key={i} style={{ fontSize: '12px', marginBottom: '4px' }}>
              {log}
            </div>
          ))}
        </div>
      )}

      <ReactFlow
        nodes={nodes}
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