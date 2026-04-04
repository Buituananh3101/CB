import { useState } from 'react';

interface SidebarProps {
  isOpen: boolean;
  closeSidebar: () => void;
}

export default function Sidebar({ isOpen, closeSidebar }: SidebarProps) {
  const [activeTab, setActiveTab] = useState<'history' | 'docs'>('history');

  return (
    <aside className={`sidebar ${isOpen ? 'open' : ''}`} id="sidebar">
      <div className="sidebar-header">
        <div className="logo">🧮 Math<span>Bot</span></div>
        <button className="new-chat-btn">
          ✏️ Chat mới
        </button>
      </div>

      <div className="sidebar-tabs">
        <button 
          className={`sidebar-tab ${activeTab === 'history' ? 'active' : ''}`} 
          onClick={() => setActiveTab('history')}
        >
          Lịch sử
        </button>
        <button 
          className={`sidebar-tab ${activeTab === 'docs' ? 'active' : ''}`} 
          onClick={() => setActiveTab('docs')}
        >
          Tài liệu
        </button>
      </div>

      <div className="history-list">
        <div style={{ color: 'var(--text-muted)', fontSize: '13px', padding: '16px 6px', textAlign: 'center' }}>
          Đang tải...
        </div>
      </div>
    </aside>
  );
}
