# Demo 截图目录

将以下截图放入此目录，README 会自动展示：

1. **swagger-demo.png** — Swagger 中成功执行 `POST /api/v1/query` 的界面（含 Request + 200 Response）
2. **steps-trace.png** — 响应中 `steps` 字段展开，展示 ReAct 工具调用过程

截图步骤：
1. 启动服务：`py -m uvicorn app.main:app --reload --port 8000`
2. 打开 http://localhost:8000/docs
3. 执行问题：`销量最高的3个产品是什么？`
4. Win + Shift + S 截图，保存到此目录
