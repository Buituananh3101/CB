import { useState, useRef, useEffect } from 'react';
import { api } from '../services/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function ChatPanel({ isActive }: { isActive: boolean }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputVal, setInputVal] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = async () => {
    if (!inputVal.trim()) return;
    const userMsg = inputVal.trim();
    setInputVal('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setIsTyping(true);

    try {
      const res = await api.post('/chat', { message: userMsg, conversation_id: null });
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.response }]);
    } catch (e) {
      console.error(e);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Lỗi: Không thể kết nối tới server!' }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className={`panel ${isActive ? 'active' : ''}`}>
      <div className="messages-wrap">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="big-icon">🧮</div>
            <h2>Xin chào! Tôi là MathBot</h2>
            <p>Hỏi tôi bất kỳ điều gì về toán học cấp 3 — giải thích, bài tập, hay khái niệm.</p>
            <div className="suggestions">
              <div className="suggestion-chip" onClick={() => setInputVal('Định lý Pythagoras')}>Định lý Pythagoras</div>
              <div className="suggestion-chip" onClick={() => setInputVal('Phương trình bậc 2')}>Phương trình bậc 2</div>
              <div className="suggestion-chip" onClick={() => setInputVal('Đạo hàm')}>Đạo hàm</div>
              <div className="suggestion-chip" onClick={() => setInputVal('Tích phân')}>Tích phân</div>
            </div>
          </div>
        ) : (
          messages.map((m, idx) => (
            <div key={idx} className={`bubble ${m.role === 'user' ? 'user' : 'ai'}`}>
              <div className={`avatar ${m.role === 'user' ? 'user-av' : 'ai'}`}>
                {m.role === 'user' ? '👤' : '🧮'}
              </div>
              <div className="bubble-content">{m.content}</div>
            </div>
          ))
        )}
        
        {isTyping && (
          <div className="bubble ai">
             <div className="avatar ai">🧮</div>
             <div className="typing-indicator">
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
             </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="chat-input-area">
        <div className="input-row">
          <textarea
            className="chat-textarea"
            placeholder="Hỏi về toán học..."
            rows={1}
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
          ></textarea>
          <button className="send-btn" onClick={handleSend} disabled={isTyping || !inputVal.trim()}>➤</button>
        </div>
      </div>
    </div>
  );
}
