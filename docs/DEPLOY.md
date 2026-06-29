# **SAEP v1.0 部署文档**

## 环境要求

- Python 3.12+
- Node.js 20+
- MySQL 8.0+

## 环境变量

生产环境建议通过环境变量配置，而非硬编码到 settings.py：

```bash
export DB_NAME=saep
export DB_USER=root
export DB_PASSWORD=******
export DB_HOST=127.0.0.1
export DB_PORT=3306
export DJANGO_SECRET_KEY=******
export DJANGO_DEBUG=False
export DJANGO_ALLOWED_HOSTS=your-domain.com,localhost
export FILE_UPLOAD_MAX_SIZE=10485760  # 10MB
```

## 后端部署

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements/dev.txt

# 初始化数据库
mysql -u root -p -e "CREATE DATABASE saep CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
python manage.py migrate
python manage.py init_roles
python manage.py createsuperuser

# 收集静态文件
python manage.py collectstatic --noinput

# MEDIA_ROOT 配置
# settings.py 中已配置:
#   MEDIA_ROOT = BASE_DIR / "media"
#   MEDIA_URL = "/media/"
# 确保 media/ 目录可写，Nginx 需配置 /media/ 代理

# 启动
gunicorn config.wsgi -b 0.0.0.0:8000
```

开发环境：
```bash
python manage.py runserver
```

## 前端部署

```bash
cd frontend
npm install
npm run build    # 产出 dist/
```

Nginx 完整配置（/api + /media 反向代理到后端 8000）：
```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/frontend/dist;

    # API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 媒体文件
    location /media/ {
        proxy_pass http://127.0.0.1:8000;
    }

    # 静态文件 (collectstatic 产出)
    location /static/ {
        proxy_pass http://127.0.0.1:8000;
    }

    # SPA fallback
    location / {
        try_files $uri /index.html;
    }
}
```

开发环境：
```bash
npm run dev    # 自带代理到 8000
```

## 默认账号

| 角色 | 用户名 | 密码 |
|------|------|------|
| 管理员 | admin | admin123 |
| 学生 | 20250001 | 250001 |
| 测评小组 | eval01 | eval123456 |
| 辅导员 | counselor01 | counselor123456 |

## 管理命令

```bash
python manage.py init_roles            # 初始化角色
python manage.py summarize_scores --batch=3 --class=3  # 成绩汇总
python manage.py rank_scores --batch=3 --class=3       # 排名计算
```
