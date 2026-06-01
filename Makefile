.PHONY: help up down logs build seed backend frontend test compose-config

help:
	@echo "可用命令:"
	@echo "  make up            - 启动全部容器 (docker compose up -d)"
	@echo "  make down          - 停止并移除容器"
	@echo "  make logs          - 查看容器日志"
	@echo "  make build         - 构建镜像"
	@echo "  make compose-config- 校验 docker-compose 配置"
	@echo "  make seed          - 在后端容器中初始化并填充种子数据"
	@echo "  make backend       - 本地运行后端 (uvicorn)"
	@echo "  make frontend      - 本地运行前端 (vite dev)"
	@echo "  make test          - 运行后端测试"

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

build:
	docker compose build

compose-config:
	docker compose config

seed:
	docker compose exec backend python -m app.db.init_db

backend:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

test:
	cd backend && python -m pytest -q
