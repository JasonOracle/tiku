"""
[变更日志]
修改时间：2026-09-06 17:35:00
AI模型：Gemini 3.1 Pro
修改内容：[创建 AI 代理网关使用的工具注册表]
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.models.user import Admin
from app.models.question import Question
from app.models.exam import Exam

class AiToolDefinition(BaseModel):
    name: str
    description: str
    parameters: dict
    risk_level: str = "low"  # low, high
    allowed_roles: List[str] = ["super_admin", "admin", "teacher"]

def get_database_stats_handler(db: Session, admin: Admin, args: dict) -> dict:
    """获取全局题库和试卷大盘数据"""
    total_q = db.query(Question).count()
    total_e = db.query(Exam).count()
    draft_e = db.query(Exam).filter(Exam.status == "draft").count()
    published_e = db.query(Exam).filter(Exam.status == "published").count()
    return {
        "total_questions": total_q,
        "total_exams": total_e,
        "draft_exams": draft_e,
        "published_exams": published_e
    }

def get_user_stats_handler(db: Session, admin: Admin, args: dict) -> dict:
    """获取用户统计数据 (C端用户与管理员)"""
    from app.models.user import User
    from sqlalchemy import func
    
    # 统计C端用户
    total_users = db.query(User).count()
    
    # 统计B端人员角色
    counts = db.query(Admin.role, func.count(Admin.id)).group_by(Admin.role).all()
    stats = {row[0]: row[1] for row in counts}
    
    return {
        "super_admin": stats.get("super_admin", 0),
        "admin": stats.get("admin", 0),
        "teacher": stats.get("teacher", 0),
        "c_end_users": total_users,
        "role_distribution": stats
    }


def get_my_exams_handler(db: Session, admin: Admin, args: dict) -> dict:
    """获取我的试卷列表"""
    q = db.query(Exam).filter(Exam.creator_id == admin.id)
    limit = args.get("limit", 10)
    exams = q.order_by(Exam.id.desc()).limit(limit).all()
    return {
        "my_exams": [
            {
                "id": e.id,
                "title": e.title,
                "status": e.status,
                "pass_percent": e.pass_percent,
                "created_at": e.created_at.strftime("%Y-%m-%d %H:%M:%S")
            } for e in exams
        ]
    }

def soft_delete_question_handler(db: Session, admin: Admin, args: dict) -> dict:
    """软删除公共题库某道题"""
    q_id = args.get("question_id")
    q = db.query(Question).filter(Question.id == q_id).first()
    if not q:
        return {"error": f"题目 ID {q_id} 不存在"}
    
    # 真正的执行逻辑 (在网关二次确认后调用)
    q.is_deleted = True
    db.commit()
    return {"success": True, "message": f"题目 ID {q_id} 已成功软删除"}

def create_question_draft_handler(db: Session, admin: Admin, args: dict) -> dict:
    """创建题目草稿"""
    from app.models.category import ExamCategory
    from app.services.exam_service import first_category_id
    cat_id = first_category_id(db)
    
    q = Question(
        creator_id=admin.id,
        category_id=cat_id,
        type=args.get("type", "single"),
        title=args.get("title"),
        options=args.get("options", []),
        answer=args.get("answer", []),
        explanation=args.get("explanation", ""),
        difficulty=args.get("difficulty", "medium"),
        score=args.get("score", 10)
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return {"success": True, "message": f"题目草稿已创建，ID: {q.id}"}

# ================= 工具注册表 =================

REGISTRY: Dict[str, dict] = {
    "get_database_stats": {
        "definition": AiToolDefinition(
            name="get_database_stats",
            description="查询系统全局的题库数量、试卷数量及状态分布。当用户询问宏观统计数据时调用此工具。",
            parameters={
                "type": "object",
                "properties": {},
                "required": []
            },
            risk_level="low",
            allowed_roles=["super_admin", "admin"]
        ),
        "handler": get_database_stats_handler
    },
    "get_my_exams": {
        "definition": AiToolDefinition(
            name="get_my_exams",
            description="获取当前登录用户（我自己）创建的试卷列表。当用户询问自己创建了哪些试卷或其状态时调用。",
            parameters={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "需要返回的试卷数量上限，默认10"
                    }
                },
                "required": []
            },
            risk_level="low",
            allowed_roles=["super_admin", "admin", "teacher"]
        ),
        "handler": get_my_exams_handler
    },
    "soft_delete_question": {
        "definition": AiToolDefinition(
            name="soft_delete_question",
            description="软删除公共题库中的某道题目。当用户明确要求删除某个具体 ID 的题目时调用。",
            parameters={
                "type": "object",
                "properties": {
                    "question_id": {
                        "type": "integer",
                        "description": "要删除的题目 ID"
                    }
                },
                "required": ["question_id"]
            },
            risk_level="high",
            allowed_roles=["super_admin", "admin"]
        ),
        "handler": soft_delete_question_handler
    },
    "create_question_draft": {
        "definition": AiToolDefinition(
            name="create_question_draft",
            description="创建一道新的题目。当用户要求新增或创建特定题目时调用。",
            parameters={
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["single", "multiple", "judge", "fill", "short"]},
                    "title": {"type": "string", "description": "题干内容"},
                    "options": {"type": "array", "items": {"type": "object"}},
                    "answer": {"type": "array", "items": {"type": "string"}},
                    "explanation": {"type": "string"},
                    "difficulty": {"type": "string", "enum": ["easy", "medium", "hard"]},
                    "score": {"type": "integer"}
                },
                "required": ["type", "title", "answer"]
            },
            risk_level="high",
            allowed_roles=["super_admin", "admin", "teacher"]
        ),
        "handler": create_question_draft_handler
    },
    "get_user_stats": {
        "definition": AiToolDefinition(
            name="get_user_stats",
            description="查询系统用户大盘数据，包括C端用户、管理员、出题人的数量分布。当用户询问用户统计时调用。",
            parameters={
                "type": "object",
                "properties": {},
                "required": []
            },
            risk_level="low",
            allowed_roles=["super_admin"]
        ),
        "handler": get_user_stats_handler
    }
}

def get_allowed_tools(role: str) -> List[dict]:
    """根据角色获取其被允许使用的工具定义列表 (符合 OpenAI Tools Schema)"""
    tools = []
    for tool_name, tool_data in REGISTRY.items():
        definition: AiToolDefinition = tool_data["definition"]
        if role in definition.allowed_roles:
            tools.append({
                "type": "function",
                "function": {
                    "name": definition.name,
                    "description": definition.description,
                    "parameters": definition.parameters
                }
            })
    return tools
