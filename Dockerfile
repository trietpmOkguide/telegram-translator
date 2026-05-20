# Sử dụng Python image bản nhẹ (slim)
FROM python:3.13-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Copy file requirements trước để tối ưu cache của Docker
COPY requirements.txt .

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào container (sẽ bỏ qua các file trong .dockerignore)
COPY . .

# Lệnh khởi chạy bot
CMD ["python", "bot.py"]
