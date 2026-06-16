import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/api";

export default function Chat() {
  const navigate = useNavigate();

  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);

  const exampleQuestions = [
    "Can I take Tylenol on an empty stomach?",
    "Can I take ibuprofen with cold medicine?",
    "What should I be careful about when taking antibiotics?",
  ];

  const labelMap = {
    FEMALE: "여성",
    MALE: "남성",
    OTHER: "기타",
    UNKNOWN: "미입력",
    NONE: "해당 없음",
    PREGNANT: "임신 중",
    BREASTFEEDING: "수유 중",
  };

  const label = (value) => labelMap[value] || value;

  const fetchProfile = async () => {
    try {
      const response = await api.get("/api/profile/");
      setProfile(response.data);
    } catch {
      setProfile(null);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();

    if (!question.trim()) {
      alert("질문을 입력해주세요.");
      return;
    }

    const userQuestion = question;
    setQuestion("");
    setLoading(true);

    try {
      const response = await api.post("/api/chat/", {
        question: userQuestion,
      });

      setMessages((prev) => [
        ...prev,
        {
          question: response.data.question,
          answer: response.data.answer,
        },
      ]);
    } catch (error) {
      alert("채팅 요청 실패");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = (text) => {
    setQuestion(text);
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  return (
    <div className="page">
      <div className="chat-card">
        <div className="section-header">
          <span className="badge">Step 3</span>
          <h1>AI 의약품 상담</h1>
          <p>
            저장된 건강정보는 답변 생성에 참고되며, 답변에는 필요한 주의사항만
            반영됩니다.
          </p>
        </div>

        {profile ? (
          <div className="profile-summary-card">
            <div className="summary-top">
              <div>
                <p className="summary-label">내 건강정보 요약</p>
                <h3>
                  {profile.age}세 · {label(profile.gender)} · {profile.weight}kg
                </h3>
              </div>
              <button
                type="button"
                className="small-secondary-btn"
                onClick={() => navigate("/profile")}
              >
                건강정보 수정
              </button>
            </div>

            <div className="summary-card-grid">
              <div className="summary-item">
                <span>혈액형</span>
                <strong>{label(profile.blood_type)}</strong>
              </div>
              <div className="summary-item">
                <span>임신/수유</span>
                <strong>{label(profile.pregnancy_status)}</strong>
              </div>
              <div className="summary-item danger">
                <span>알레르기</span>
                <strong>{profile.allergies}</strong>
              </div>
              <div className="summary-item warning">
                <span>기저질환</span>
                <strong>{profile.diseases}</strong>
              </div>
              <div className="summary-item info">
                <span>복용약</span>
                <strong>{profile.current_medications}</strong>
              </div>
            </div>
          </div>
        ) : (
          <div className="profile-summary warning">
            건강정보가 등록되어 있지 않습니다.
            <button
              type="button"
              className="small-secondary-btn"
              onClick={() => navigate("/profile")}
            >
              건강정보 등록하기
            </button>
          </div>
        )}

        <div className="example-list pretty">
          {exampleQuestions.map((item) => (
            <button
              key={item}
              type="button"
              className="example-chip"
              onClick={() => handleExampleClick(item)}
            >
              {item}
            </button>
          ))}
        </div>

        <form onSubmit={handleSend} className="chat-form">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="예: Can I take Tylenol on an empty stomach?"
          />
          <button type="submit" disabled={loading}>
            {loading ? "생성 중..." : "질문하기"}
          </button>
        </form>

        {loading && (
          <div className="loading-box">
            건강정보를 참고해 답변을 생성하고 있습니다...
          </div>
        )}

        <div className="message-list">
          {messages.map((msg, index) => (
            <div key={index} className="message-box">
              <div className="question">Q. {msg.question}</div>
              <div className="answer">A. {msg.answer}</div>
            </div>
          ))}
        </div>

        {messages.length > 0 && (
          <div className="action-row">
            <button type="button" onClick={() => navigate("/history")}>
              상담 이력 보기
            </button>
            <button
              type="button"
              className="secondary-btn"
              onClick={() => navigate("/profile")}
            >
              건강정보 수정하기
            </button>
          </div>
        )}
      </div>
    </div>
  );
}