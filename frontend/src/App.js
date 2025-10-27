import React, { useState, useEffect, useCallback } from 'react';
import './App.css';

function App() {
  const [name, setName] = useState('');
  const [message, setMessage] = useState('');
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);

  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Memoize fetchUsers to avoid dependency issues
  const fetchUsers = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/users`);
      const data = await response.json();
      setUsers(data.users || []);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  }, [API_BASE]);

  // Fetch all users on component mount
  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) return;

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/hello/${name}`);
      const data = await response.json();
      setMessage(data.message || data.error);
      
      // Refresh users list
      await fetchUsers();
    } catch (error) {
      setMessage('Error connecting to server');
    }
    setLoading(false);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>User Greeting App</h1>
        
        <form onSubmit={handleSubmit} className="name-form">
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter your name"
            className="name-input"
            disabled={loading}
          />
          <button type="submit" disabled={loading || !name.trim()}>
            {loading ? 'Submitting...' : 'Submit'}
          </button>
        </form>

        {message && (
          <div className="message">
            {message}
          </div>
        )}

        <div className="users-section">
          <h2>All Users ({users.length})</h2>
          {users.length > 0 ? (
            <table className="users-table">
              <thead>
                <tr>
                  <th>Username</th>
                  <th>Created At</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user, index) => (
                  <tr key={index}>
                    <td>{user.username}</td>
                    <td>{new Date(user.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>No users yet</p>
          )}
        </div>
      </header>
    </div>
  );
}

export default App;