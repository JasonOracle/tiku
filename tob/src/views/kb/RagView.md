# RagView RAG 私有文档库页

## 设计初衷

v1.3 任务 3：上传 PDF / Word / 文本资料，滑窗切片 + 本地向量化（大文档后台进行，
2 秒轮询进度条）；检索验证框可直观检验召回效果；AI 出题弹窗勾选已完成文档后，
生成题目自动携带 `source_ref`，在题海列表以`引用溯源`抽屉高亮出处。

## 接口

- `POST /api/v1/admin/rag/documents`（multipart，10MB 上限）
- `GET /api/v1/admin/rag/documents`（超管全览，他人仅自传）
- `GET /api/v1/admin/rag/documents/{id}`（进度）
- `DELETE /api/v1/admin/rag/documents/{id}`
- `POST /api/v1/admin/rag/search`（检索验证）
