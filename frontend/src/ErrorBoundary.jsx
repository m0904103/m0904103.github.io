import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', background: '#ffcccc', color: '#990000', fontFamily: 'sans-serif' }}>
          <h2>🚨 系統發生崩潰 (System Crash)</h2>
          <p>很抱歉，量化終端遇到了致命錯誤。請將以下錯誤訊息回報給志剛：</p>
          <pre style={{ background: '#fff', padding: '10px', overflow: 'auto' }}>
            {this.state.error && this.state.error.toString()}
          </pre>
          <button onClick={() => window.location.reload()} style={{ padding: '10px 20px', cursor: 'pointer' }}>
            重新整理 (Reload)
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
