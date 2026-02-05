import ReviewCard from './components/ReviewCard'

function App() {
  const mockTasks = [
    {
      task_id: "task-001",
      generated_content: "Hey guys! Check out the new Chimera sneakers dropping this Friday! #Chimera #Fashion",
      confidence_score: 0.95,
      reasoning_trace: "Content matches 'Excited/Hype' persona. No sensitive topics detected. High confidence."
    },
    {
      task_id: "task-002",
      generated_content: "I think the new policy on crypto regulation is fascinating. What do you imply?",
      confidence_score: 0.75,
      reasoning_trace: "Topic 'crypto regulation' flagged as potentially sensitive (Financial/Political). Confidence lowered due to ambiguity."
    },
    {
      task_id: "task-003",
      generated_content: "Buy this token now! It's going to the moon! 100x guaranteed!",
      confidence_score: 0.45,
      reasoning_trace: "CRITICAL: Detected 'Financial Advice' pattern. Direct promise of returns. Violates safety guidelines."
    }
  ];

  return (
    <div className="min-h-screen bg-gray-100 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Chimera HITL Dashboard</h1>
          <p className="mt-2 text-sm text-gray-600">
            Review pending actions flagged by the Judge Agent.
          </p>
        </header>

        <main className="space-y-6">
          {mockTasks.map(task => (
            <ReviewCard
              key={task.task_id}
              task_id={task.task_id}
              generated_content={task.generated_content}
              confidence_score={task.confidence_score}
              reasoning_trace={task.reasoning_trace}
            />
          ))}
        </main>
      </div>
    </div>
  )
}

export default App
