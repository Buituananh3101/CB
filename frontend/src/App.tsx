import { useState } from 'react';
import Sidebar from './components/layout/Sidebar';
import ChatView from './components/views/ChatView';
import DocumentView from './components/views/DocumentView';
import MindmapView from './components/views/MindmapView';
import NotesView from './components/views/NotesView';
import QuizView from './components/views/QuizView';

export type PanelType = 'chat' | 'upload' | 'mindmap' | 'notes' | 'quiz';

function App() {
  const [activePanel, setActivePanel] = useState<PanelType>('chat');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [convTitle, setConvTitle] = useState('—');

  const closeSidebar = () => setIsSidebarOpen(false);
  const toggleSidebar = () => setIsSidebarOpen(prev => !prev);

  return (
    <>
      <div 
        className={`sidebar-overlay ${isSidebarOpen ? 'active' : ''}`} 
        onClick={closeSidebar}
      ></div>

      <Sidebar isOpen={isSidebarOpen} closeSidebar={closeSidebar} />

      <main className="main">
        <div className="topbar">
          <button className="hamburger-btn" onClick={toggleSidebar} title="Menu">☰</button>
          <div className="topbar-tabs">
            <button className={`tab-btn ${activePanel === 'chat' ? 'active' : ''}`} onClick={() => setActivePanel('chat')}>💬 Chat</button>
            <button className={`tab-btn ${activePanel === 'upload' ? 'active' : ''}`} onClick={() => setActivePanel('upload')}>📄 Tài liệu</button>
            <button className={`tab-btn ${activePanel === 'mindmap' ? 'active' : ''}`} onClick={() => setActivePanel('mindmap')}>🧠 Mind Map</button>
            <button className={`tab-btn ${activePanel === 'notes' ? 'active' : ''}`} onClick={() => setActivePanel('notes')}>📝 Ghi chú</button>
            <button className={`tab-btn ${activePanel === 'quiz' ? 'active' : ''}`} onClick={() => setActivePanel('quiz')}>✅ Quiz</button>
          </div>
          <div className="conv-title-display">{convTitle}</div>
        </div>

        <div className="panels">
          <ChatView isActive={activePanel === 'chat'} />
          <DocumentView isActive={activePanel === 'upload'} />
          <MindmapView isActive={activePanel === 'mindmap'} />
          <NotesView isActive={activePanel === 'notes'} />
          <QuizView isActive={activePanel === 'quiz'} />
        </div>
      </main>
    </>
  );
}

export default App;
