export default function MindmapPanel({ isActive }: { isActive: boolean }) {
  return (
    <div className={`panel ${isActive ? 'active' : ''}`}>
      <div className="panel-inner">
        <h2>🧠 Tạo Mind Map</h2>
        <div className="form-group">
          <label>Chủ đề</label>
          <input className="form-control" placeholder="Ví dụ: Hàm số bậc hai" />
        </div>
        <div className="form-group">
          <label>Độ sâu (1–5)</label>
          <input className="form-control" type="number" defaultValue={3} min={1} max={5} />
        </div>
        <button className="btn btn-primary">🧠 Tạo Mind Map</button>
      </div>
    </div>
  );
}
