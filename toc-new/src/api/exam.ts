/**
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Gemini 系列
 * 修改内容：[新增 fetchMemberBanners 接口与 BannerItem 类型，支持首页轮播展示]
 */
import { request } from "@/utils/request";

export type BannerItem = {
  id: number;
  title: string;
  image_url: string;
  link_url?: string;
};

export type BannerListResult = {
  items: BannerItem[];
  interval_seconds: number;
};

export function fetchMemberBanners(): Promise<BannerListResult> {
  return request<BannerListResult>({
    url: "/api/v1/member/banners",
    method: "GET"
  });
}

/**
 * 路径说明（重要）：
 * C 端全部接口挂在 /api/v1/member 前缀下，由 backend/app/main.py 注册，
 * 不存在 /api/v1/saas 前缀（saas 只是后端 Python 模块目录名）。
 */

/** 选项双形态：存量数据为字符串数组（如 "A. 莫奈"），新录入数据为对象数组；渲染前需归一化 */
export type QuestionOption = string | { key: string; text: string };

/** 单题作答：单选 / 判断 / 简答提交 string，多选 / 多空填空提交 string[] */
export type UserAnswerItem = {
  resource_id: number;
  answer: string | string[];
};

/** 可考测评列表项：GET /api/v1/member/member-tasks */
export type MemberTaskItem = {
  task_id: number;
  /** 本人该卷记录 ID，未开考为 null；有值时可直接跳成绩详情 */
  record_id: number | null;
  title: string;
  /** pending 未开考 / submitted 已定稿 / pending_verification 核验中 / verified 已核验 */
  status: string;
  category_id: number | null;
  category_name: string;
  question_count: number;
  total_score: number;
  pass_score: number;
  is_timed: boolean;
  /** 单位分钟，不限时为 0 */
  time_limit: number;
  start_time: string | null;
  deadline: string | null;
  score: number | null;
  submit_time: string | null;
  /** 后端权威判定是否可「继续测试」，前端只做渲染 */
  can_continue: boolean;
  /** manual 人工审核 / ai_auto AI 核验 */
  verification_mode: string;
};

export type MemberTaskListResult = {
  items: MemberTaskItem[];
};

/** 作答视角题目：服务端已剥离正确答案与解析，防泄题 */
export type ExamQuestion = {
  id: number;
  /** single_choice / multiple_choice / judge / fill / short 等 */
  type: string;
  title: string;
  content: string;
  options: QuestionOption[];
  score: number;
  category_id: number | null;
};

/** 入考取题结果：GET /api/v1/member/tasks/{task_id}/entry */
export type ExamEntryResult = {
  task_id: number;
  exam_title: string;
  title: string;
  is_timed: boolean;
  time_limit: number;
  end_time: string | null;
  deadline: string | null;
  /** 服务端权威时间，前端倒计时必须以它为基准，禁止使用本地时间 */
  server_now: string;
  /** 服务端锁定的开考时刻 */
  started_at: string;
  my_status: string;
  my_record_id: number | null;
  /** 续答回填数据：仅「继续测试」退回 pending 后非空 */
  my_answers: UserAnswerItem[];
  questions: ExamQuestion[];
};

/** 交卷入参：POST /api/v1/member/task-records/submit */
export type ExamSubmitPayload = {
  task_id: number;
  /** 服务端会忽略客户端上报值并按自身开考时刻结算，此处仅保持契约完整 */
  time_spent: number;
  answers: UserAnswerItem[];
};

export type ExamSubmitResult = {
  record_id: number;
  status: string;
  score: number;
  time_spent: number;
  server_now: string;
};

/** 成绩单单题明细 */
export type ExamRecordItem = {
  resource_id: number | null;
  content: string;
  type: string | null;
  options: QuestionOption[];
  user_answer: string | string[] | null;
  /**
   * 标准答案。实库中 multiple_choice 为数组 ["A","B","D"]，
   * 而 fill_in / short_answer 为字符串（如 "2"），因此必须保留联合类型。
   * 该字段在「核验中」的试卷上由后端照常返回，防泄题必须由前端不渲染来兜底。
   */
  correct_answer: string | string[] | null;
  explanation: string;
  /** 后端预留字段，当前固定为 null */
  gained: null;
  /** 该题实际分值（取自试卷内个性化配分） */
  eq_score: number;
};

/** 成绩与答题复盘：GET /api/v1/member/task-records/{record_id} */
export type ExamRecordDetail = {
  record_id: number;
  task_id: number;
  task_title: string;
  status: string;
  /** true 表示处于核验中，前端必须阻断标准答案渲染，规避泄题 */
  pending: boolean;
  score: number | null;
  passed: boolean;
  time_spent: number;
  /** 人工核验评语 */
  comments: string;
  /** AI 核验评语 */
  ai_comments: string;
  submit_time: string;
  items: ExamRecordItem[];
};

/** 获取可考测评列表（含本人作答状态） */
export function fetchMemberTasks(): Promise<MemberTaskListResult> {
  return request<MemberTaskListResult>({
    url: "/api/v1/member/member-tasks",
  });
}

/** 入考取题：服务端同时完成开考时刻锁定与防泄题脱敏 */
export function fetchExamEntry(taskId: number): Promise<ExamEntryResult> {
  return request<ExamEntryResult>({
    url: `/api/v1/member/tasks/${taskId}/entry`,
  });
}

/** 交卷：answers 必须为对象数组，禁止序列化为 {101: "A"} 字典 */
export function submitExam(payload: ExamSubmitPayload): Promise<ExamSubmitResult> {
  return request<ExamSubmitResult>({
    url: "/api/v1/member/task-records/submit",
    method: "POST",
    data: payload as unknown as Record<string, unknown>,
  });
}

/** 获取单次考试成绩与答题复盘 */
export function fetchExamRecord(recordId: number): Promise<ExamRecordDetail> {
  return request<ExamRecordDetail>({
    url: `/api/v1/member/task-records/${recordId}`,
  });
}

/** 单条历史作答记录：GET /api/v1/member/task-records */
export type MyRecordItem = {
  record_id: number;
  task_id: number;
  task_title: string;
  /** pending 进行中 / submitted 已定稿 / pending_verification 核验中 / verified 已核验 */
  status: string;
  /** 未出分时为 null */
  score: number | null;
  submit_time: string;
};

export type MyRecordListResult = {
  items: MyRecordItem[];
};

/** 个人中心统计：GET /api/v1/member/me/stats */
export type MyStatsResult = {
  total_exams_taken: number;
  history_count: number;
  passed_count: number;
  /** 综合通过率，后端已按百分比数值返回（如 91.7） */
  pass_rate: number;
  favorite_count: number;
};

/** 获取本人历史作答记录列表（按记录 ID 倒序，后端不分页） */
export function fetchMyRecords(): Promise<MyRecordListResult> {
  return request<MyRecordListResult>({
    url: "/api/v1/member/task-records",
  });
}

/** 获取个人中心统计数据 */
export function fetchMyStats(): Promise<MyStatsResult> {
  return request<MyStatsResult>({
    url: "/api/v1/member/me/stats",
  });
}

/** 收藏的题目条目：GET /api/v1/member/favorites */
export type FavoriteItem = {
  id: number;
  resource_id: number;
  /** 后端同时返回的题目 ID 别名，与 resource_id 取值相同 */
  question_id: number;
  content: string;
  title: string;
  type: string;
  options: QuestionOption[];
};

export type FavoriteListResult = {
  items: FavoriteItem[];
};

/** 获取本人重点题目收藏列表 */
export function fetchFavorites(): Promise<FavoriteListResult> {
  return request<FavoriteListResult>({
    url: "/api/v1/member/favorites",
  });
}

/**
 * 添加题目收藏。
 * 后端对已收藏的题目做幂等处理，重复调用不会产生重复数据；成功响应 code 为 201 且不含 data 字段。
 */
export function addFavorite(resourceId: number): Promise<void> {
  return request<void>({
    url: "/api/v1/member/favorites",
    method: "POST",
    data: { resource_id: resourceId },
  });
}

/** 取消题目收藏，成功响应 code 为 200 且不含 data 字段 */
export function removeFavorite(resourceId: number): Promise<void> {
  return request<void>({
    url: `/api/v1/member/favorites/${resourceId}`,
    method: "DELETE",
  });
}
