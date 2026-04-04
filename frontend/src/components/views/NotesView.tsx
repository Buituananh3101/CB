export default function NotesPanel({ isActive }: { isActive: boolean }) {
  return (
    <div className={`panel ${isActive ? 'active' : ''}`}>
      <div className="panel-inner">
        <h2>📝 Ghi chú thông minh</h2>
        <div className="form-group">
          <label>Tiêu đề</label>
          <input className="form-control" placeholder="Ví dụ: Tổng hợp kiến thức Đạo hàm" />
        </div>
        <div className="form-group">
          <label>Nội dung (để trống để AI tự tạo)</label>
          <textarea className="form-control" rows={4} placeholder="Nội dung tùy chọn..."></textarea>
        </div>
        <button className="btn btn-primary">📝 Tạo Ghi chú</button>
      </div>
    </div>
  );
}
