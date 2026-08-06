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
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  handleHardReload = () => {
    try {
      if ('caches' in window) {
        caches.keys().then(names => names.forEach(name => caches.delete(name)));
      }
      localStorage.clear();
      sessionStorage.clear();
    } catch (e) {}
    window.location.href =
      window.location.origin +
      window.location.pathname +
      '?bust=' +
      Date.now();
  };

  render() {
    if (this.state.hasError) {
      const errMsg = this.state.error ? this.state.error.toString() : '未知錯誤';
      return (
        <div style={{
          padding: '30px',
          background: '#111827',
          color: '#f87171',
          fontFamily: 'sans-serif',
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <div style={{
            maxWidth: '600px',
            width: '100%',
            background: '#1f2937',
            padding: '30px',
            borderRadius: '16px',
            border: '1px solid #374151',
            boxShadow: '0 20px 25px -5px rgba(0,0,0,0.5)'
          }}>
            <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#f87171', marginBottom: '10px' }}>
              🚨 偵測到舊版快取殘留 — 正在嘗試自動修復
            </div>
            <div style={{ fontSize: '14px', color: '#9ca3af', marginBottom: '15px' }}>
              瀏覽器快取了舊版 JS 檔案，導致程式出錯。請點擊下方按鈕一鍵清除快取並重新載入最新版本。
            </div>
            <pre style={{
              background: '#111827',
              padding: '12px',
              borderRadius: '8px',
              color: '#fca5a5',
              fontSize: '12px',
              overflow: 'auto',
              marginBottom: '20px',
              whiteSpace: 'pre-wrap'
            }}>
              {errMsg}
            </pre>
            <button
              onClick={this.handleHardReload}
              style={{
                width: '100%',
                padding: '14px',
                background: '#3b82f6',
                color: '#ffffff',
                fontWeight: 'bold',
                border: 'none',
                borderRadius: '10px',
                cursor: 'pointer',
                fontSize: '15px'
              }}
            >
              🔄 一鍵清除舊快取並載入最新版本
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
