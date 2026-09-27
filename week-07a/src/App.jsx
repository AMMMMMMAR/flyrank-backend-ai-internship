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

const initialNodes = [
  {
    id: '1',
    position: { x: 250, y: 100 },
    data: { label: 'Is this a support request?' },
    type: 'default'
  },
  {
    id: '2',
    position: { x: 100, y: 300 },
    data: { label: 'Route to Support Team' },
    type: 'default'
  },
  {
    id: '3',
    position: { x: 400, y: 300 },
    data: { label: 'Route to Sales Team' },
    type: 'default'
  },
]

const initialEdges = [
  { id: 'e1-2', source: '1', target: '2', label: 'YES', style: { stroke: 'green' } },
  { id: 'e1-3', source: '1', target: '3', label: 'NO', style: { stroke: 'red' } },
]

export default function App() {
  const [nodes, setNodes] = useState(initialNodes)
  const [edges, setEdges] = useState(initialEdges)

  const onNodesChange = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
    []
  )

  const onEdgesChange = useCallback(
    (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    []
  )

  const onConnect = useCallback(
    (connection) => setEdges((eds) => addEdge(connection, eds)),
    []
  )

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  )
}