# /**
#  * [变更日志]
#  * 修改时间：2026-09-11
#  * AI模型：Gemini 3.6 Flash
#  * 修改内容：[1. 增加造数脚本，为星雅教育与皓石集团生成6份试卷及30条考试记录]
#  */
import json
import pymysql
from datetime import datetime, timedelta

def seed_data():
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='rootpassword',
        database='tiku_db',
        charset='utf8mb4',
        autocommit=False
    )
    cursor = conn.cursor()

    try:
        print("1. 清理现有旧的考核数据...")
        cursor.execute("DELETE FROM task_records;")
        cursor.execute("DELETE FROM task_resources;")
        cursor.execute("DELETE FROM tasks;")
        cursor.execute("DELETE FROM resources;")

        now = datetime.now()

        # 定义 6 份试卷及其 30 道题目结构
        # 每份试卷包含 5 道题（单选15分，多选20分，判断15分，填空20分，简答30分；如果不含简答，则单选20,多选25,判断15,填空20,单选20等凑满100分）
        
        exams_def = [
            # --- 租户 1: 星雅教育 (tenant_id=1, creator_id=2) ---
            {
                "tenant_id": 1,
                "creator_id": 2,
                "title": "星雅教育-2026教学质量与标准化考核（人工审核版）",
                "description": "旨在评估教师团队教学规范、课堂互动与家校沟通能力（含简答题，人工人工审核）。",
                "verification_mode": "manual",
                "questions": [
                    {
                        "type": "single_choice",
                        "content": "在星雅教育标准课堂中，首次课前互动引导时间建议控制在多少分钟内？",
                        "options": ["A. 3-5分钟", "B. 10-15分钟", "C. 20分钟", "D. 不需要引导"],
                        "correct_answer": "A",
                        "score": 15
                    },
                    {
                        "type": "multiple_choice",
                        "content": "星雅教育对课堂教学质量评估的核心维度包括哪些？（多选）",
                        "options": ["A. 教学目标明确性", "B. 学员互动参与度", "C. 课后作业讲评闭环", "D. 教师个人服装品牌"],
                        "correct_answer": ["A", "B", "C"],
                        "score": 20
                    },
                    {
                        "type": "judge",
                        "content": "教师在收到家长关于学习进度的咨询时，应当在24小时内给予明确回复与反馈。",
                        "options": ["A. 正确", "B. 错误"],
                        "correct_answer": "A",
                        "score": 15
                    },
                    {
                        "type": "fill_in",
                        "content": "星雅教育的服务宗旨是：以学员为中心，以______为导向。",
                        "options": None,
                        "correct_answer": "教学质量",
                        "score": 20
                    },
                    {
                        "type": "short_answer",
                        "content": "请简述当学员在课堂上出现注意力不集中或跟不上进度时，教师应采取的具体应对策略。",
                        "options": None,
                        "correct_answer": "1. 采用提问或互动游戏手段重新拉回注意力；2. 课中巡视给予个别点拨指导；3. 课后微课复习补差，并与家长沟通协同关注。",
                        "score": 30
                    }
                ]
            },
            {
                "tenant_id": 1,
                "creator_id": 2,
                "title": "星雅教育-AI辅助教学与智能工具应用考试（AI全自动审批）",
                "description": "测试教研人员对于智能备课、AI助教与学员作业自动批改工具的掌握程度（含简答题，AI全自动审批）。",
                "verification_mode": "ai_auto",
                "questions": [
                    {
                        "type": "single_choice",
                        "content": "在使用AI智能教案生成器时，提示词（Prompt）中最重要的要素是什么？",
                        "options": ["A. 明确的角色设置与目标上下文", "B. 复杂的英文语法", "C. 大量的修饰形容词", "D. 随意输入关键词"],
                        "correct_answer": "A",
                        "score": 15
                    },
                    {
                        "type": "multiple_choice",
                        "content": "AI助教系统可以为星雅教育的日常教学提供哪些支持？（多选）",
                        "options": ["A. 自动生成错题集与解析", "B. 个性化学习路径推荐", "C. 替代教师进行线下实操", "D. 学情数据可视化分析"],
                        "correct_answer": ["A", "B", "D"],
                        "score": 20
                    },
                    {
                        "type": "judge",
                        "content": "AI生成的教学素材和试题可以直接发布给学员使用，无需人工教研审核。",
                        "options": ["A. 正确", "B. 错误"],
                        "correct_answer": "B",
                        "score": 15
                    },
                    {
                        "type": "fill_in",
                        "content": "星雅AI助教系统中，用于检索本地知识库文档的核心技术机制简称为______。",
                        "options": None,
                        "correct_answer": "RAG",
                        "score": 20
                    },
                    {
                        "type": "short_answer",
                        "content": "阐述在数字化教学背景下，如何平衡AI技术赋能与人文关怀教学的关系？",
                        "options": None,
                        "correct_answer": "AI技术负责重复性的知识传递、作业批改与数据分析，释放教师精力；教师专注于情感沟通、价值观引导与个性化心理辅导，实现人机协同育人。",
                        "score": 30
                    }
                ]
            },
            {
                "tenant_id": 1,
                "creator_id": 2,
                "title": "星雅教育-教务合规与员工安全制度测试（全客观题）",
                "description": "星雅教育教务合规、消防安全与行政制度全员基础考试（全客观题）。",
                "verification_mode": "ai_auto",
                "questions": [
                    {
                        "type": "single_choice",
                        "content": "星雅教育校区消火栓及安全出口检查的常规频率是？",
                        "options": ["A. 每日检查", "B. 每月检查一次", "C. 每半年检查一次", "D. 每年检查一次"],
                        "correct_answer": "A",
                        "score": 20
                    },
                    {
                        "type": "multiple_choice",
                        "content": "关于学员隐私与数据安全保护，员工严禁实施的行为有？（多选）",
                        "options": ["A. 私自导出学员家长联系方式并外泄", "B. 将学员成绩发布在公开社交平台且未打码", "C. 在加密教学系统中查看学员作业", "D. 向第三方机构出售学员名单"],
                        "correct_answer": ["A", "B", "D"],
                        "score": 25
                    },
                    {
                        "type": "judge",
                        "content": "校区内发生突发紧急状况时，第一发现人应立即启动应急预案并向校区负责人汇报。",
                        "options": ["A. 正确", "B. 错误"],
                        "correct_answer": "A",
                        "score": 15
                    },
                    {
                        "type": "fill_in",
                        "content": "星雅教育员工考勤管理规定中，每月允许的紧急事假补办窗口期为______个工作日内。",
                        "options": None,
                        "correct_answer": "2",
                        "score": 20
                    },
                    {
                        "type": "single_choice",
                        "content": "校区内部文档与课程讲义的安全密级分类中，核心教研大纲属于？",
                        "options": ["A. 内部公开", "B. 商业机密/核心保密", "C. 外部完全公开", "D. 普通浏览"],
                        "correct_answer": "B",
                        "score": 20
                    }
                ]
            },

            # --- 租户 2: 皓石集团 (tenant_id=2, creator_id=3) ---
            {
                "tenant_id": 2,
                "creator_id": 3,
                "title": "皓石集团-企业战略与高绩效项目管理考试（人工审核版）",
                "description": "评估项目经理与业务骨干的OKRs执行、风险管控与团队协作能力（含简答题，人工审核）。",
                "verification_mode": "manual",
                "questions": [
                    {
                        "type": "single_choice",
                        "content": "皓石集团敏捷项目迭代管理中，Sprint敏捷冲刺的标准周期通常推荐为？",
                        "options": ["A. 2周", "B. 2个月", "C. 6个月", "D. 1天"],
                        "correct_answer": "A",
                        "score": 15
                    },
                    {
                        "type": "multiple_choice",
                        "content": "在皓石集团项目风险管理框架中，关键风险应对策略包括哪些？（多选）",
                        "options": ["A. 风险规避", "B. 风险转移", "C. 风险减轻", "D. 完全忽视风险"],
                        "correct_answer": ["A", "B", "C"],
                        "score": 20
                    },
                    {
                        "type": "judge",
                        "content": "项目变更控制委员会（CCB）对任何重大范围变更具有最终审批决策权。",
                        "options": ["A. 正确", "B. 错误"],
                        "correct_answer": "A",
                        "score": 15
                    },
                    {
                        "type": "fill_in",
                        "content": "皓石集团的核心价值观是：创新、担当、______、共赢。",
                        "options": None,
                        "correct_answer": "高效",
                        "score": 20
                    },
                    {
                        "type": "short_answer",
                        "content": "请简述当项目面临进度严重滞后且预算受限时，作为项目负责人你将采取哪些救火措施？",
                        "options": None,
                        "correct_answer": "1. 梳理关键路径，裁剪非核心MVP功能范围；2. 优化资源配置，攻坚核心瓶颈模块；3. 加强每日站会进度盘点，及时向利益相关方预警并争取支持。",
                        "score": 30
                    }
                ]
            },
            {
                "tenant_id": 2,
                "creator_id": 3,
                "title": "皓石集团-AI大模型赋能与商业数字化转型测试（AI全自动审批）",
                "description": "检验员工利用AI技术进行业务流程优化、数据分析与创新应用的能力（含简答题，AI全自动审批）。",
                "verification_mode": "ai_auto",
                "questions": [
                    {
                        "type": "single_choice",
                        "content": "在皓石集团AI数据分析平台中，为了保护商业敏感数据，提问时应当避免传入？",
                        "options": ["A. 未脱敏的真实客户身份与财务底表", "B. 行业公开趋势报告", "C. 通用业务逻辑伪代码", "D. 脱敏后的统计汇总指标"],
                        "correct_answer": "A",
                        "score": 15
                    },
                    {
                        "type": "multiple_choice",
                        "content": "生成式AI在皓石集团企业营销与客户服务中可以应用于哪些场景？（多选）",
                        "options": ["A. 智能客服7x24小时问答", "B. 营销文案与海报草案快速生成", "C. 客户意图识别与精准标签提取", "D. 代替客户签署法律合同"],
                        "correct_answer": ["A", "B", "C"],
                        "score": 20
                    },
                    {
                        "type": "judge",
                        "content": "AI模型输出的内容具有绝对准确性，可以直接作为财务核算和法律履约依据。",
                        "options": ["A. 正确", "B. 错误"],
                        "correct_answer": "B",
                        "score": 15
                    },
                    {
                        "type": "fill_in",
                        "content": "皓石集团私有化部署的大模型知识库采用的向量数据库技术缩写为______。",
                        "options": None,
                        "correct_answer": "Milvus",
                        "score": 20
                    },
                    {
                        "type": "short_answer",
                        "content": "结合你所在的岗位，举例说明如何利用大模型工具提升日常工作效率30%以上？",
                        "options": None,
                        "correct_answer": "利用AI辅助撰写报告大纲与会议纪要整理，自动提取待办事项；利用大模型编写数据处理脚本与代码重构，缩短研发与分析周期。",
                        "score": 30
                    }
                ]
            },
            {
                "tenant_id": 2,
                "creator_id": 3,
                "title": "皓石集团-信息安全与合规审计认证考试（全客观题）",
                "description": "皓石集团全员网络安全、商业保密与合规行为准则测试（全客观题）。",
                "verification_mode": "ai_auto",
                "questions": [
                    {
                        "type": "single_choice",
                        "content": "根据皓石集团密码安全规范，员工个人工作账号的复杂密码最长更换周期为？",
                        "options": ["A. 90天", "B. 3年", "C. 永不更换", "D. 1天"],
                        "correct_answer": "A",
                        "score": 20
                    },
                    {
                        "type": "multiple_choice",
                        "content": "防范钓鱼邮件和网络诈骗的正确做法包括哪些？（多选）",
                        "options": ["A. 仔细核对发件人邮箱后缀", "B. 绝不点击来历不明的附件或外链", "C. 收到要钱提醒时立即电话二次确认", "D. 顺手将工作密码填入任何弹框"],
                        "correct_answer": ["A", "B", "C"],
                        "score": 25
                    },
                    {
                        "type": "judge",
                        "content": "员工离职或岗位调换时，其原有的系统高权访问权限必须在生效当日完成关停或变更。",
                        "options": ["A. 正确", "B. 错误"],
                        "correct_answer": "A",
                        "score": 15
                    },
                    {
                        "type": "fill_in",
                        "content": "皓石集团ISO27001信息安全管理体系中，安全事件响应首要原则是：一发现、二隔离、三______。",
                        "options": None,
                        "correct_answer": "上报",
                        "score": 20
                    },
                    {
                        "type": "single_choice",
                        "content": "在公共场所（如咖啡厅）办公时，连接未加密公共Wi-Fi的安全隐患是？",
                        "options": ["A. 流量易被监听与中间人攻击", "B. 电脑电池消耗过快", "C. 屏幕亮度降低", "D. Wi-Fi速度太快导致数据丢失"],
                        "correct_answer": "A",
                        "score": 20
                    }
                ]
            }
        ]

        created_tasks = []

        print("2. 创建试卷与题目数据...")
        for exam in exams_def:
            # 插入 task
            cursor.execute("""
                INSERT INTO tasks (tenant_id, title, description, cover_image, category_id, status, is_timed, time_limit, start_time, deadline, verification_mode, creator_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (
                exam["tenant_id"],
                exam["title"],
                exam["description"],
                "",
                None,
                "published",
                1,
                45,
                now - timedelta(days=1),
                now + timedelta(days=30),
                exam["verification_mode"],
                exam["creator_id"],
                now
            ))
            task_id = cursor.lastrowid
            created_tasks.append({
                "id": task_id,
                "tenant_id": exam["tenant_id"],
                "verification_mode": exam["verification_mode"],
                "questions": []
            })

            # 插入 resources 与 task_resources
            for idx, q in enumerate(exam["questions"]):
                options_json = json.dumps(q["options"], ensure_ascii=False) if q["options"] else None
                correct_answer_json = json.dumps(q["correct_answer"], ensure_ascii=False)
                cursor.execute("""
                    INSERT INTO resources (tenant_id, category_id, type, content, options, correct_answer, score, creator_id, is_deleted, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, (
                    exam["tenant_id"],
                    None,
                    q["type"],
                    q["content"],
                    options_json,
                    correct_answer_json,
                    q["score"],
                    exam["creator_id"],
                    0,
                    now
                ))
                res_id = cursor.lastrowid
                created_tasks[-1]["questions"].append({
                    "id": res_id,
                    "type": q["type"],
                    "correct_answer": q["correct_answer"],
                    "score": q["score"]
                })

                cursor.execute("""
                    INSERT INTO task_resources (task_id, resource_id, score, sort_order)
                    VALUES (%s, %s, %s, %s);
                """, (task_id, res_id, q["score"], idx + 1))

        print(f"成功生成 {len(created_tasks)} 份试卷，30 道题目。")

        # 3. 组织员工考试作答矩阵
        # 星雅教育 members: 4 (赵艳), 6 (孙杰), 8 (刘艳), 10 (李艳), 13 (赵芳)
        # 皓石集团 members: 5 (陈伟), 7 (李敏), 9 (王磊), 11 (吴涛), 12 (周芳)
        
        # 分数矩阵配置:
        # 每家企业 5 个员工考 3 份试卷。
        # 约定作答模式：
        # - Pass 高分: 客观题全对，简答题满分或大部分得分 (85-95分)
        # - Pass 中等: 错1题客观题，简答题得部分分 (70-80分)
        # - Fail 不及格: 错多道客观题，简答题极少分或未作答 (30-50分)
        
        # 星雅 (tasks 0, 1, 2)
        # 赵艳 (4): [85, 90, 95] -> 全胜
        # 孙杰 (6): [45 (FAIL), 85, 80] -> 试卷1不及格
        # 刘艳 (8): [90, 50 (FAIL), 85] -> 试卷2不及格
        # 李艳 (10): [80, 85, 40 (FAIL)] -> 试卷3不及格
        # 赵芳 (13): [55 (FAIL), 45 (FAIL), 90] -> 试卷1、2不及格
        
        # 皓石 (tasks 3, 4, 5)
        # 陈伟 (5): [90, 85, 95] -> 全胜
        # 李敏 (7): [40 (FAIL), 90, 85] -> 试卷1不及格
        # 王磊 (9): [85, 45 (FAIL), 80] -> 试卷2不及格
        # 吴涛 (11): [80, 85, 50 (FAIL)] -> 试卷3不及格
        # 周芳 (12): [50 (FAIL), 85, 45 (FAIL)] -> 试卷1、3不及格

        user_exam_matrix = {
            # tenant 1
            4: [("pass_high", 90), ("pass_high", 90), ("pass_high", 100)],
            6: [("fail", 45), ("pass_mid", 85), ("pass_mid", 80)],
            8: [("pass_mid", 85), ("fail", 50), ("pass_mid", 85)],
            10: [("pass_mid", 80), ("pass_mid", 85), ("fail", 40)],
            13: [("fail", 50), ("fail", 45), ("pass_high", 90)],

            # tenant 2
            5: [("pass_high", 90), ("pass_high", 90), ("pass_high", 100)],
            7: [("fail", 40), ("pass_high", 90), ("pass_mid", 85)],
            9: [("pass_mid", 85), ("fail", 45), ("pass_mid", 80)],
            11: [("pass_mid", 80), ("pass_mid", 85), ("fail", 50)],
            12: [("fail", 50), ("pass_mid", 85), ("fail", 45)]
        }

        print("3. 生成 30 条考查作答记录 (task_records)...")
        record_count = 0

        for task_idx, task_info in enumerate(created_tasks):
            t_id = task_info["id"]
            t_tenant = task_info["tenant_id"]
            t_mode = task_info["verification_mode"]
            t_questions = task_info["questions"]
            relative_exam_idx = task_idx % 3  # 0, 1, 2

            # 找到所属租户的 user_ids
            members = [4, 6, 8, 10, 13] if t_tenant == 1 else [5, 7, 9, 11, 12]

            for u_id in members:
                mode_str, target_score = user_exam_matrix[u_id][relative_exam_idx]

                # 构建用户答案列表
                answers = []
                actual_score = 0

                for q in t_questions:
                    q_type = q["type"]
                    q_correct = q["correct_answer"]
                    q_score = q["score"]

                    if mode_str == "pass_high":
                        # 全对
                        user_ans = q_correct
                        actual_score += q_score
                    elif mode_str == "pass_mid":
                        # 错第一道单选题或部分分
                        if q_type == "single_choice" and len(answers) == 0:
                            user_ans = "B" if q_correct != "B" else "C" # 答错
                        elif q_type == "short_answer":
                            user_ans = "理解并遵守相关规范，按要求完成。" # 得部分分
                            actual_score += 15
                        else:
                            user_ans = q_correct
                            actual_score += q_score
                    else: # fail
                        # 大量答错
                        if q_type == "single_choice":
                            user_ans = "D" if q_correct != "D" else "C"
                        elif q_type == "multiple_choice":
                            user_ans = ["D"]
                        elif q_type == "judge":
                            user_ans = "B" if q_correct == "A" else "A"
                        elif q_type == "fill_in":
                            user_ans = "未知"
                        elif q_type == "short_answer":
                            user_ans = "不太清楚。"
                            actual_score += 5

                    answers.append({
                        "resource_id": q["id"],
                        "answer": user_ans
                    })

                # 修正精确总分以接近 target_score
                final_score = actual_score if mode_str != "pass_high" else sum(q["score"] for q in t_questions)
                if mode_str == "fail" and final_score >= 60:
                    final_score = 45

                # 状态判定
                # 人工审核试卷 (manual) -> 'submitted'
                # AI / 客观题试卷 (ai_auto) -> 'verified'
                rec_status = "submitted" if t_mode == "manual" else "verified"

                ai_result_json = None
                comments_str = None

                if rec_status == "verified":
                    ai_result_json = json.dumps({
                        "total_score": final_score,
                        "evaluation": "AI自动阅卷完成",
                        "details": "客观题与大模型辅助自动评分完毕"
                    }, ensure_ascii=False)
                    comments_str = "AI全自动批改完成"
                else:
                    comments_str = "等待管理员/主考官人工审核简答题"

                submit_dt = now - timedelta(hours=relative_exam_idx * 2 + (u_id % 3))

                cursor.execute("""
                    INSERT INTO task_records (tenant_id, task_id, user_id, status, score, time_spent, answers, ai_result, comments, created_at, submit_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, (
                    t_tenant,
                    t_id,
                    u_id,
                    rec_status,
                    final_score,
                    1200 + u_id * 30, # time_spent (秒)
                    json.dumps(answers, ensure_ascii=False),
                    ai_result_json,
                    comments_str,
                    submit_dt,
                    submit_dt
                ))
                record_count += 1

        conn.commit()
        print(f"成功插入 {record_count} 条考试记录！造数全部完成！")

    except Exception as e:
        conn.rollback()
        print(f"数据库操作失败，已回滚！错误详情: {e}")
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    seed_data()
