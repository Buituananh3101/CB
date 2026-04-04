export default function QuizPanel({ isActive }: { isActive: boolean }) {
  return (
    <div className={`panel ${isActive ? 'active' : ''}`} style={{ overflow: 'hidden' }}>
      <div className="panel-inner" style={{ overflowY: 'auto' }}>
        <div className="quiz-setup">
          <h2>✅ Kiểm tra kiến thức</h2>
          <p>Tạo bộ câu hỏi trắc nghiệm theo chủ đề và trả lời từng câu ngay trên trang.</p>
          <div className="form-group">
            <label>Chủ đề</label>
            <input className="form-control" placeholder="Ví dụ: Phương trình bậc hai" />
          </div>
          <div style={{ display: 'flex', gap: '14px' }}>
            <div className="form-group" style={{ flex: 1 }}>
              <label>Số câu hỏi</label>
              <input className="form-control" type="number" defaultValue={5} min={1} max={10} />
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label>Độ khó</label>
              <select className="form-control" defaultValue="medium">
                <option value="easy">🟢 Dễ</option>
                <option value="medium">🟡 Trung bình</option>
                <option value="hard">🔴 Khó</option>
              </select>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
            <button className="btn btn-primary">✅ Bắt đầu Quiz</button>
            <button className="btn-ghost" style={{ padding: '10px 18px' }}>📋 Lịch sử làm bài</button>
          </div>
        </div>
      </div>
    </div>
  );
}
