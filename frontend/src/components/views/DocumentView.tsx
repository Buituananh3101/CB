export default function UploadPanel({ isActive }: { isActive: boolean }) {
  return (
    <div className={`panel ${isActive ? 'active' : ''}`}>
      <div className="panel-inner">
        <h2>📄 Tài liệu học tập</h2>
        <div className="upload-zone">
            <div className="upload-icon">📁</div>
            <p>Click hoặc kéo thả file vào đây</p>
            <small>Hỗ trợ: PDF, DOCX, TXT, JPG, PNG — tối đa 10MB</small>
        </div>
        <h3 style={{marginTop: '24px', fontSize: '15px', color: 'var(--text-muted)'}}>Đã tải lên</h3>
        <div className="doc-grid">
            <p style={{color: 'var(--text-muted)', fontSize: '13px', marginTop: '10px'}}>Chưa có tài liệu nào.</p>
        </div>
      </div>
    </div>
  );
}
