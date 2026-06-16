import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/api";

export default function History() {
  const navigate = useNavigate();
  const [histories, setHistories] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchHistories = async () => {
    setLoading(true);

    try {
      const response = await api.get("/api/chat/history/");
      setHistories(response.data);
    } catch (error) {
      alert("상담 이력 조회 실패");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistories();
  }, []);

  return (
    <div className="page">
      <div className="chat-card">
        <div className="section-header">
          <span className="badge">History</span>
          <h1>상담 이력</h1>
          <p>이전에 질문한 내용과 답변을 다시 확인할 수 있습니다.</p>
        </div>

        {loading && <div className="loading-box">상담 이력을 불러오는 중...</div>}

        {!loading && histories.length === 0 && (
          <div className="empty-box">
            아직 상담 이력이 없습니다.
            <button onClick={() => navigate("/chat")}>상담하러 가기</button>
          </div>
        )}

        {histories.map((item) => (
          <div key={item.id} className="message-box">
            <p className="date">{item.created_at}</p>
            <div className="question">Q. {item.question}</div>
            <div className="answer">A. {item.answer}</div>
          </div>
        ))}

        {histories.length > 0 && (
          <div className="action-row">
            <button onClick={() => navigate("/chat")}>새 질문하기</button>
            <button className="secondary-btn" onClick={() => navigate("/profile")}>
              건강정보 수정하기
            </button>
          </div>
        )}
      </div>
    </div>
  );
}