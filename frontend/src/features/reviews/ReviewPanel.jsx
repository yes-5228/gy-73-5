import { Star, History } from "lucide-react";
import { useState } from "react";

export default function ReviewPanel({ orders, onReview }) {
  const reviewableOrders = orders.filter((order) => order.can_review);
  const [orderId, setOrderId] = useState("");
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [showHistory, setShowHistory] = useState(false);
  const [reviewHistory, setReviewHistory] = useState([]);

  const selectedOrderData = orders.find((o) => o.id === Number(orderId));

  async function submit(event) {
    event.preventDefault();
    if (!orderId) return;
    const result = await onReview(Number(orderId), { rating: Number(rating), comment });
    if (result && result.history) {
      setReviewHistory(result.history);
      setShowHistory(true);
    }
    setComment("");
  }

  async function fetchHistory(orderId) {
    try {
      const response = await fetch(`/api/reviews/orders/${orderId}/history/`);
      const data = await response.json();
      setReviewHistory(data.history || []);
      setShowHistory(true);
    } catch (error) {
      console.error("获取评价历史失败:", error);
    }
  }

  function handleOrderChange(e) {
    const id = e.target.value;
    setOrderId(id);
    setShowHistory(false);
    setReviewHistory([]);
    if (id) {
      const order = orders.find((o) => o.id === Number(id));
      setSelectedOrder(order);
      if (order && order.review) {
        setRating(order.review.rating);
        setComment(order.review.comment || "");
      } else {
        setRating(5);
        setComment("");
      }
    } else {
      setSelectedOrder(null);
    }
  }

  return (
    <div className="panel">
      <div className="panel-title">
        <Star size={20} />
        <h3>完成评价</h3>
      </div>
      <form className="review-form" onSubmit={submit}>
        <select value={orderId} onChange={handleOrderChange}>
          <option value="">选择可评价订单</option>
          {reviewableOrders.map((order) => (
            <option value={order.id} key={order.id}>
              {order.customer_name} · {order.destination}
              {order.review ? " (已评价，可更新)" : ""}
            </option>
          ))}
        </select>

        {selectedOrderData && !selectedOrderData.can_review && (
          <div className="warning-message">
            ⚠️ {selectedOrderData.review_reason}
          </div>
        )}

        {selectedOrderData && selectedOrderData.exception_status !== "none" && (
          <div className={`status-tag ${selectedOrderData.exception_status}`}>
            异常状态: {selectedOrderData.exception_status_label}
          </div>
        )}

        {selectedOrderData && (
          <div className={`status-tag ${selectedOrderData.settlement_status}`}>
            结算状态: {selectedOrderData.settlement_status_label}
          </div>
        )}

        <div className="rating-input">
          <label>评分:</label>
          <div className="star-rating">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                type="button"
                key={star}
                className={`star-btn ${star <= rating ? "active" : ""}`}
                onClick={() => setRating(star)}
              >
                <Star size={24} fill={star <= rating ? "#fbbf24" : "none"} />
              </button>
            ))}
            <span className="rating-value">{rating} 星</span>
          </div>
        </div>

        <input
          type="number"
          min="1"
          max="5"
          value={rating}
          onChange={(e) => setRating(Number(e.target.value))}
          style={{ display: "none" }}
        />
        <textarea
          rows="3"
          placeholder="客户评价内容..."
          value={comment}
          onChange={(e) => setComment(e.target.value)}
        />

        <div className="button-row">
          <button
            className="primary-button"
            type="submit"
            disabled={!orderId || !selectedOrderData?.can_review}
          >
            {selectedOrderData?.review ? "更新评价" : "提交评价"}
          </button>
          {selectedOrderData?.review && (
            <button
              type="button"
              className="secondary-button"
              onClick={() => fetchHistory(Number(orderId))}
            >
              <History size={16} /> 查看历史
            </button>
          )}
        </div>
      </form>

      {showHistory && reviewHistory.length > 0 && (
        <div className="review-history">
          <h4>评价历史记录</h4>
          {reviewHistory.map((review, index) => (
            <div key={review.id} className={`history-item ${review.is_current ? "current" : ""}`}>
              <div className="history-header">
                <span className="version-badge">版本 {review.version}</span>
                {review.is_current && <span className="current-badge">当前生效</span>}
                <span className="rating-display">
                  {[...Array(review.rating)].map((_, i) => (
                    <Star key={i} size={14} fill="#fbbf24" color="#fbbf24" />
                  ))}
                </span>
              </div>
              <p className="history-comment">{review.comment || "(无评价内容)"}</p>
              <p className="history-date">{new Date(review.created_at).toLocaleString()}</p>
            </div>
          ))}
          <button className="close-btn" onClick={() => setShowHistory(false)}>关闭</button>
        </div>
      )}
    </div>
  );
}
