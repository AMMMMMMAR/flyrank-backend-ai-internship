import OpenAI from 'openai'

const client = new OpenAI({
  baseURL: import.meta.env.VITE_OPENROUTER_BASE_URL,
  apiKey: import.meta.env.VITE_OPENROUTER_API_KEY,
  dangerouslyAllowBrowser: true
})

export async function runWorkflow(nodes, edges, onStep) {
  // Find the starting node (no incoming edges)
  const targetIds = new Set(edges.map(e => e.target))
  const startNode = nodes.find(n => !targetIds.has(n.id))
  
  if (!startNode) {
    onStep({ type: 'error', message: 'No start node found' })
    return
  }

  let currentNode = startNode
  const visited = new Set()
  const executionLog = []

  while (currentNode) {
    // prevent infinite loops
    if (visited.has(currentNode.id)) {
      onStep({ type: 'error', message: 'Loop detected!' })
      break
    }
    visited.add(currentNode.id)

    onStep({ type: 'thinking', nodeId: currentNode.id })

    // Ask the LLM
    const answer = await askLLM(currentNode.data.label)
    
    executionLog.push({
      nodeId: currentNode.id,
      prompt: currentNode.data.label,
      answer
    })

    onStep({ type: 'answered', nodeId: currentNode.id, answer })

    // Find the matching edge (YES or NO)
    const outgoingEdges = edges.filter(e => e.source === currentNode.id)
    
    if (outgoingEdges.length === 0) {
      // leaf node — end of workflow
      onStep({ type: 'done', log: executionLog })
      break
    }

    const matchingEdge = outgoingEdges.find(
      e => e.label?.toUpperCase() === answer.toUpperCase()
    )

    if (!matchingEdge) {
      onStep({ type: 'error', message: `No ${answer} edge found from node ${currentNode.id}` })
      break
    }

    // Move to next node
    currentNode = nodes.find(n => n.id === matchingEdge.target)
  }
}

async function askLLM(prompt) {
  const response = await client.chat.completions.create({
    model: import.meta.env.VITE_OPENROUTER_MODEL,
    messages: [
      {
        role: 'system',
        content: 'You are a decision engine. Answer ONLY with YES or NO. No explanation, no punctuation, just YES or NO.'
      },
      {
        role: 'user',
        content: prompt
      }
    ],
    temperature: 0.1
  })

  const answer = response.choices[0].message.content.trim().toUpperCase()
  return answer.includes('YES') ? 'YES' : 'NO'
}