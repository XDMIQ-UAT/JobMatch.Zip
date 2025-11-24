'use client'

import { useState, useEffect } from 'react'

export default function ForumsPage() {
  const [topics] = useState(['AI Tools', 'LLC Management', 'Job Search', 'Capabilities'])
  const [selectedTopic, setSelectedTopic] = useState<string | null>(null)
  const [posts, setPosts] = useState<any[]>([])

  useEffect(() => {
    if (selectedTopic) {
      fetch(`http://localhost:8000/api/forums/topics/${selectedTopic}/posts`)
        .then(res => res.json())
        .then(data => setPosts(data))
        .catch(err => console.error('Failed to load posts:', err))
    }
  }, [selectedTopic])

  return (
    <main style={{ padding: '2rem', maxWidth: '1000px', margin: '0 auto' }}>
      <h1>Community Forums</h1>
      <p>Anonymous discussions about AI tools, capabilities, and job search</p>

      <div style={{ marginTop: '2rem' }}>
        <h2>Forum Topics</h2>
        <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
          {topics.map(topic => (
            <button
              key={topic}
              onClick={() => setSelectedTopic(topic)}
              style={{
                padding: '0.75rem 1.5rem',
                border: selectedTopic === topic ? '2px solid blue' : '1px solid #ccc'
              }}
            >
              {topic}
            </button>
          ))}
        </div>
      </div>

      {selectedTopic && (
        <div style={{ marginTop: '2rem' }}>
          <h2>Posts in {selectedTopic}</h2>
          {posts.length === 0 ? (
            <p>No posts yet. Be the first to post!</p>
          ) : (
            posts.map(post => (
              <div key={post.id} style={{ marginTop: '1rem', padding: '1rem', border: '1px solid #ccc' }}>
                <h3>{post.title}</h3>
                <p>{post.content}</p>
                <small>Posted: {new Date(post.created_at).toLocaleDateString()}</small>
              </div>
            ))
          )}
        </div>
      )}
    </main>
  )
}


