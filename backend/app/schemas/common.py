from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List, Optional, Any

T = TypeVar("T")

class ResponseModel(BaseModel, Generic[T]):
    """统一 API 基础响应封装"""
    code: int = Field(200, description="状态码 200 为成功")
    message: str = Field("success", description="提示文本说明")
    data: Optional[T] = Field(None, description="业务载荷数据")

class PageResponse(BaseModel, Generic[T]):
    """标准分页响应数据载荷"""
    total: int = Field(..., description="总记录条数")
    page: int = Field(..., description="当前页码 (从1开始)")
    size: int = Field(..., description="每页限制大小")
    total_pages: int = Field(..., description="总页数")
    has_next: bool = Field(..., description="是否存在下一页")
    items: List[T] = Field(..., description="列表数据项")
