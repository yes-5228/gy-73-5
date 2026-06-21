import { Star, History, AlertCircle } from "lucide-react";
import { useState } from "react";

export default function ReviewPanel({ orders, onReview }) {
  const reviewableOrders = orders.filter((order) => order.can_review);
  const [orderId, setOrderId] = useState("");
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [showHistory, setShowHistory] = useState(false);
  const [reviewHistory, setReviewHistory] = useState([]);

  const selectedOrder = reviewableOrders.find((o) => o.id === Number(orderId)) || null;

  async function submit(event) {
    event.preventDefault();
    if (!orderId || !selectedOrder?.can_review) return;
    const result = await onReview(Number(orderId), { rating: Number(rating), comment });
    if (result && result.history) {
      setReviewHistory(result.history);
      setShowHistory(true);
    }
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
      const order = reviewableOrders.find((o) => o.id === Number(id));
      if (order && order.review) {
        setRating(order.review.rating);
        setComment(order.review.comment || "");
      } else {
        setRating(5);
        setComment("");
      }
    } else {
      setRating(5);
      setComment("");
    }
  }

  function renderStars(count, size = 14) {
    return (
      <span className="inline-stars">
        {[...Array(5)].map((_, i) => (
          <Star
            key={i}
            size={size}
            fill={i < count ? "#fbbf24" : "none"}
            color={i < count ? "#fbbf24" : "#d1d5db"}
          />
        ))}
      </span>
    );
  }

  return (
    <div className="panel">
      <div className="panel-title">
        <Star size={20} />
        <h3>完成评价</h3>
      </div>
      <form className="review-form" onSubmit={submit}>
        <div className="form-field">
          <label>选择订单</label>
          <select value={orderId} onChange={handleOrderChange}>
            <option value="">请选择可评价订单</option>
            {reviewableOrders.map((order) => (
              <option value={order.id} key={order.id}>
                {order.customer_name} · {order.destination}
                {order.review ? ` [${order.review.rating}星 已评价，可更新]` : ""}
              </option>
            ))}
          </select>
        </div>

        {selectedOrder && (
          <div className="order-review-status">
            {selectedOrder.review ? (
              <div className="status-info reviewed">
                <Star size={16} fill="#fbbf24" color="#fbbf24" />
                <span>已评价 {selectedOrder.review.rating} 星，可更新</span>
              </div>
            ) : (
              <div className="status-info can-review">
                <Star size={16} />
                <span>可评价</span>
              </div>
            )}
          </div>
        )}

        {selectedOrder && selectedOrder.exception_status !== "none" && (
          <div className={`status-tag ${selectedOrder.exception_status}`}>
            异常状态: {selectedOrder.exception_status_label}
          </div>
        )}

        {selectedOrder && (
          <div className={`status-tag ${selectedOrder.settlement_status}`}>
            结算状态: {selectedOrder.settlement_status_label}
          </div>
        )}

        {selectedOrder && (
          <div className="rating-input">
            <label>评分</label>
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
        )}

        {selectedOrder && (
          <div className="form-field">
            <label>评价内容</label>
            <textarea
              rows="3"
              placeholder="请输入评价内容..."
              value={comment}
              onChange={(e) => setComment(e.target.value)}
            />
          </div>
        )}

        {selectedOrder && (
          <div className="button-row">
            <button
              className="primary-button"
              type="submit"
            >
              {selectedOrder.review ? "更新评价" : "提交评价"}
            </button>
            {selectedOrder.review && (
              <button
                type="button"
                className="secondary-button"
                onClick={() => fetchHistory(Number(orderId))}
              >
                <History size={16} /> 查看历史
              </button>
            )}
          </div>
        )}

        {!selectedOrder && orderId === "" && (
          <p className="muted">
            {reviewableOrders.length > 0
              ? "请从上方选择一个可评价的订单"
              : "暂无可评价的订单"}
          </p>
        )}
      </form>

      {showHistory && reviewHistory.length > 0 && (
        <div className="review-history">
          <h4>评价历史记录</h4>
          {reviewHistory.map((review) => (
            <div key={review.id} className={`history-item ${review.is_current ? "current" : ""}`}>
              <div className="history-header">
                <span className="version-badge">版本 {review.version}</span>
                {review.is_current && <span className="current-badge">当前生效</span>}
                <span className="rating-display">
                  {renderStars(review.rating, 14)}
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
