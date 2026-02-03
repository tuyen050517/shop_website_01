// ⚙️ product_detail.js
document.addEventListener("DOMContentLoaded", () => {
  const addBtn = document.getElementById("addToCartBtn");
  const alertMsg = document.getElementById("alertMessage");

  if (!addBtn) return;

  addBtn.addEventListener("click", async (e) => {
    e.preventDefault();
    const url = addBtn.getAttribute("href");

    try {
      const res = await fetch(url);
      const contentType = res.headers.get("content-type");

      // 🧭 Nếu chưa đăng nhập → server trả về HTML
      if (contentType && contentType.includes("text/html")) {
        const html = await res.text();
        document.open();
        document.write(html);
        document.close();
        return;
      }

      // ✅ Nếu server trả JSON → hiển thị thông báo
      const data = await res.json();
      showAlert(data.message || "✅ Đã thêm vào giỏ hàng!");
    } catch (err) {
      showAlert("⚠️ Lỗi khi thêm sản phẩm!");
    }
  });

  function showAlert(msg) {
    alertMsg.textContent = msg;
    alertMsg.style.display = "block";
    setTimeout(() => (alertMsg.style.display = "none"), 2000);
  }
});
