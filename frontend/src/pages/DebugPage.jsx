import { useEffect, useState } from 'react';
import { getHealth } from '../services/api';

function DebugPage() {
  const [backendStatus, setBackendStatus] = useState('checking');

  useEffect(() => {
    getHealth()
      .then(() => setBackendStatus('connected'))
      .catch(() => setBackendStatus('unreachable'));
  }, []);

  return (
    <main>
      <h1>FixTrace-RAG</h1>
      <p>Backend status: {backendStatus}</p>
      <p>
        The debug form, diagnosis panel, evidence panel, and claim verification
        table land here once the AI service's <code>/debug</code> pipeline exists.
      </p>
    </main>
  );
}

export default DebugPage;
