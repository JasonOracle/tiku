<!--
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Gemini 系列
 * 修改内容：[优化试卷列表上架状态交互：将静态胶囊全面升级为直观可点击的 el-switch 状态开关组件，内置 inline-prompt（已上架/待上架）显式标识，下架操作接入异步二次确认拦截(before-change)，彻底消除用户认知盲区]
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Gemini 系列
 * 修改内容：[增强 AI 创建试卷弹窗交互防护：在整个表单内容区域包裹 v-loading="aiExamLoading" 半透明遮罩与微提示，生成期间彻底冻结输入框与下拉选择，防止用户误触修改]
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Gemini 系列
 * 修改内容：[优化试卷列表操作列交互逻辑：仅在存在待人工批阅答卷且数量大于0 (row.pending_count > 0) 时才显示高亮批阅按钮，无待批阅时保持轻量整洁]
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Gemini 底层
 * 修改内容：[1. 彻底修复 AI 智能组卷审阅弹窗试题卡片样式错乱、选项缺失与答案不显示问题; 2. 补齐 .ai-review-list / .ai-review-card / .ai-review-head / .ai-review-title 完整现代卡片样式体系; 3. 增强试题审阅清单在弹窗内的独立滚动、选项高亮与解析呈现]
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Gemini 系列
 * 修改内容：[对齐参考图2核心视觉规范：1. 消除内部表格与大卡片的硬实线边框，替换为极其柔和的高级多层立体弥散阴影(Elevated Island Box-Shadow)；2. 表头首行独立着色：仅第1行表头配置清爽纯净的蓝灰背景色(#f1f5f9)与1px微底分割线，其余数据行全白无边框平铺，彻底告别沉重线条框感]
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Gemini 系列
 * 修改内容：[1. 强化列表清晰边框：page-card 边框加深为 #e2e8f0，表格外框增加 1px 优雅圆角实线边框；2. 表头立体区分：表头背景升级为深一档的淡冷灰蓝 #edf2f7，搭配底部分割实线 #cbd5e1，彻底与数据行拉开层次；3. 修复表头文字折行与字形变形Bug：ID、题目数、总分、随机排列等列宽全面拓宽至 80px~115px，并强制全局 white-space: nowrap 与 word-break: keep-all]
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Gemini 系列
 * 修改内容：[试卷列表全局样式按现代企业级SaaS标准重构：1. 搜索框与分类选择器大圆角化(10px)并内嵌精细阴影；2. 新建按钮与批阅按钮升级为实心高质感胶囊按键(Pill Button)，有待批阅时智能变色为亮橙渐变；3. 表格消除竖线与硬边框，行高扩充至62px，增加极简无边框分类胶囊、物理状态指示圆点(● 已上架/待上架)与弱化灰白布尔胶囊；4. 详情操作转为轻量无背景文字链接，底部分页栏圆润微卡片化]
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Gemini 系列
 * 修改内容：[1. 新建/编辑试卷弹窗高定重构：彻底消灭粗暴蓝色补丁框，重塑为高质感轻量卡片仪表盘(Settings Strip); 2. 规整开关项对齐与内联微提示，考试时间与及格线紧凑无缝排布; 3. 题目列表表格支持原地修改单题分值(数字微调器)，联动总分与及格线毫秒级计算; 4. 去除冗余分割线与双层卡片包裹，合并排序与删除至操作列，表格高度沉浸适配]
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Gemini 系列
 * 修改内容：[1. 完善考试数据业务闭环：当存在未批改简答题(verify_pending>0)时，顶部渲染高亮橙色 Alert 预警横幅与【前往核验】直达按钮; 2. KPI 卡片与明细表格增加待核验态：员工行判定结果显式展示橙色「待核验」，得分标记「初评」徽章，杜绝虚假全员不及格误判]
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Gemini 系列
 * 修改内容：[彻底去教育化：将试卷管理列表表头「创建老师」修正为标准企业级「创建人」，精准对接后端返回的 creator_name 字段]
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Gemini 系列
 * 修改内容：[1. 修复试卷详情弹窗题型判断Bug，兼容 single_choice/multiple_choice/judge/fill_in/short_answer 等后端枚举类型; 2. 增加 getNormalizedOptions 处理字符串与对象格式选项，修复选项内容空白及正确答案高亮失败Bug; 3. 升级考试数据 Tab 下方员工作答明细为高质感表格，配置深灰蓝立体表头(#f1f5f9)、外边框与成绩胶囊]
 * [变更日志]
 * 修改时间：2026-09-11
 * AI模型：Gemini 系列
 * 修改内容：[1. 彻底删除操作列中多余的「数据」按钮，全面合并入「查看详情」弹窗; 2. 试卷详情弹窗升级为双 Tab 结构(试卷数据 + 考试数据); 3. 试卷数据补全题目全景展示，选项高保真浅绿高亮正确答案，免折叠展开; 4. 考试数据对齐多租户员工模型，外显4大KPI指标卡、轻量成绩分布环形/条形图及员工作答明细; 5. 增加优雅空状态插画与提示，杜绝草稿或无作答时的图表白屏]
 * [变更日志]
 * 修改时间：2026-09-10
 * AI模型：OpenCode / Gemini 底层
 * 修改内容：[试卷管理筛选栏升级：全部任务分类改为试卷分类，增加试卷状态下拉(全部/已上架/未上架/已下架)，增加检索按钮并改为点击后触发请求，增加重置图标按钮]
 * [变更日志]
 * 修改时间：2026-09-10
 * AI模型：OpenCode / Gemini 底层
 * 修改内容：[1. 试卷管理表格列全面规范：任务名称->试卷名称、任务分类->试卷分类、任务时间窗->考试时间(长期开放->不限时)、条目数->题目数; 2. 列表操作列新增「人工批阅 (x份)」高亮橙色按钮，有人答卷且待批时展示并直达批阅抽屉]
 * [变更日志]
 * 修改时间：2026-09-09
 * AI模型：Muse Spark
 * 修改内容：[彻底清洗：全量通用化词汇映射，旧教育词汇已删除]
  * [变更日志]
  * 修改时间：2026-09-09
  * AI模型：Gemini 系列
  * 修改内容：[模块名称统一对齐「任务管理」: 1. 弹窗标题更新为「编辑任务」/「新建任务」/「任务详情 (只读模式)」; 2. 移除旧称「任务与编排」]
  * 修改时间：2026-09-09
  * AI模型：Gemini 系列
  * 修改内容：[统一编排资料文案为「参考私有文库」: 明确说明与编排需求不相关时系统将自动脱钩以通识出卷，避免张冠李戴]
  * 修改时间：2026-09-09
  * AI模型：Gemini 系列
  * 修改内容：[AI智能一键编排弹窗新增私有教材/资料(RAG)选填多选下拉框: 1. 仅当存在已向量化解析成功的文档时展示(v-if="ragDocs.length"); 2. 编排时优先检索命中切片并作为事实依据赋给大模型; 3. 新生成的条目自动携带切片溯源]
  * 修改时间：2026-09-09
  * AI模型：Gemini 系列
  * 修改内容：[优化任务下架与删除闭环: 1. 任务操作列对已归档/下架状态(archived)开放删除按钮与重新编辑上架能力; 2. 优化下架确认提示文案，说明零作答任务下架后依然支持物理删除或重新上架]
  * 修改时间：2026-09-08
  * AI模型：Gemini 系列
  * 修改内容：[✨AI智能一键编排优化: 1. 首屏两项核心输入改为「编排需求」+「任务分类」(分类必填且默认选中第一项); 2. 任务时间移至高级选项，未填写时系统自动默认当前时间起 7 天任务区间]
  * 修改时间：2026-09-07 00:05:00
  * AI模型：Gemini 系列
  * 修改内容：[1. AI 智能一键编排弹窗 UI 对齐普通新建任务: 增加条目难度单选框(默认简单)、限时作答开关+输入框、及格比例 Slider 滑块；2. 说明 AI 编排及格线在条目生成后进入查看与确认页动态向上取整计算]
  * 修改时间：2026-09-07
  * AI模型：Muse Spark
  * 修改内容：[v1.2 Step3: 任务标题列行内待办橙色微章 + VerifyDrawer 行内核验抽屉 (替代跳核验大厅)]
  * 修改时间：2026-09-07
  * AI模型：Muse Spark
  * 修改内容：[v1.2 Step4: 已选条目透亮选项与正确答案高亮(ResourcePreview) + grading_mode 三态单选(仅简答题展开)]
-->
<template>
  <div class="page-card">
    <div class="filter-bar">
      <div class="filters">
        <el-input
          v-model="filters.keyword"
          placeholder="请输入试卷名称、关键字..."
          clearable
          class="custom-search-input"
          style="width: 260px"
          @change="loadExams"
        >
          <template #prefix>
            <el-icon class="search-prefix-icon"><Search /></el-icon>
          </template>
        </el-input>
        <el-select
          v-model="filters.category_id"
          placeholder="请选择试卷分类"
          clearable
          class="custom-filter-select"
          style="width: 180px"
          @change="loadExams"
        >
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
      </div>

      <div class="actions">
        <el-button type="warning" plain class="ai-btn" @click="aiExamVisible = true">
          ✨ AI 智能一键编排
        </el-button>
        <el-button type="primary" class="primary-create-btn" @click="openCreateDialog">
          <el-icon><Plus /></el-icon> 新建试卷
        </el-button>
      </div>
    </div>

    <!-- 任务列表表格 (参考图1:1极简无界悬浮高定设计) -->
    <el-table
      :data="exams"
      v-loading="loading"
      class="saas-modern-table"
      style="width: 100%"
      :header-cell-style="{
        backgroundColor: '#f1f5f9',
        color: '#475569',
        fontWeight: '700',
        fontSize: '13px',
        padding: '14px 16px',
        borderBottom: '1px solid #e2e8f0',
        whiteSpace: 'nowrap'
      }"
      :cell-style="{
        padding: '18px 16px',
        borderBottom: '1px solid #f1f5f9'
      }"
    >
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column prop="id" label="ID" width="80" align="center">
        <template #default="{ row }">
          <span class="col-id-text">{{ row.id }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="试卷名称" min-width="320">
        <template #default="{ row }">
          <div class="exam-title-cell">
            <span class="exam-main-title">{{ row.title }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="category_id" label="试卷分类" width="140" align="center">
        <template #default="{ row }">
          <span class="category-pill">
            {{ row.category_name || getCategoryName(row.category_id) || '未分类' }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="上架状态" width="150" align="center">
        <template #default="{ row }">
          <div class="status-switch-cell">
            <el-switch
              :model-value="row.status === 'published'"
              :loading="row._statusLoading"
              inline-prompt
              active-text="已上架"
              inactive-text="待上架"
              class="exam-status-switch"
              :before-change="() => handleSwitchBeforeChange(row)"
            />
          </div>
        </template>
      </el-table-column>
      <el-table-column label="考试时间" width="120" align="center">
        <template #default="{ row }">
          <span v-if="row.is_timed && row.time_limit" class="timed-text">{{ row.time_limit }} 分钟</span>
          <span v-else class="muted-gray-text">不限时</span>
        </template>
      </el-table-column>
      <el-table-column prop="creator_name" label="创建人" width="115" align="center">
        <template #default="{ row }">
          <span class="muted-gray-text">{{ row.creator_name || '—' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="question_count" label="题目数" width="100" align="center">
        <template #default="{ row }">
          <span class="count-highlight">{{ row.question_count || 0 }} 题</span>
        </template>
      </el-table-column>
      <el-table-column prop="total_score" label="总分" width="95" align="center">
        <template #default="{ row }">
          <span class="score-text">{{ row.total_score || 0 }} 分</span>
        </template>
      </el-table-column>
      <el-table-column prop="is_random" label="随机排列" width="110" align="center">
        <template #default="{ row }">
          <span class="boolean-pill" :class="{ 'is-true': row.is_random }">
            {{ row.is_random ? '是' : '否' }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" align="center" fixed="right">
        <template #default="{ row }">
          <div class="action-btn-group">
            <button
              v-if="row.pending_count > 0"
              class="action-pill-btn pill-urgent"
              @click="handleOpenGrading(row)"
            >
              <el-icon class="pill-icon"><EditPen /></el-icon>
              <span>人工批阅 ({{ row.pending_count }}份)</span>
            </button>
            <el-button type="primary" link class="action-link-btn" @click="openViewDialog(row)">
              <el-icon><View /></el-icon> 详情
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-bar">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        layout="total, prev, pager, next, jumper"
        @current-change="loadExams"
      />
    </div>

    <!-- 试卷综合详情（双 Tab：试卷数据 + 考试数据） Dialog -->
    <el-dialog
      v-model="viewDialogVisible"
      title="试卷详情"
      width="920px"
      top="35px"
      destroy-on-close
      class="exam-detail-dialog"
    >
      <el-tabs v-model="viewActiveTab" class="detail-nav-tabs">
        <el-tab-pane label="试卷数据" name="exam">
          <div class="tab-pane-container" v-loading="viewDetailLoading">
            <!-- 1. 基础信息卡片 -->
            <div class="detail-section-card">
              <div class="section-title-bar">
                <el-icon class="section-icon"><Document /></el-icon>
                <span>基础信息</span>
              </div>
              <div class="info-grid">
                <div class="info-cell">
                  <span class="info-label">试卷标题：</span>
                  <span class="info-val strong">{{ viewData?.title || '—' }}</span>
                </div>
                <div class="info-cell">
                  <span class="info-label">试卷分类：</span>
                  <el-tag size="small" type="info">{{ getCategoryName(viewData?.category_id) }}</el-tag>
                </div>
                <div class="info-cell">
                  <span class="info-label">考试时长：</span>
                  <span class="info-val">{{ viewData?.is_timed ? `${viewData?.time_limit} 分钟` : '不限时长' }}</span>
                </div>
                <div class="info-cell">
                  <span class="info-label">得分线：</span>
                  <span class="info-val">总分 <strong style="color:#0284c7">{{ computedViewTotalScore }}</strong> 分 / 及格线 <strong style="color:#16a34a">{{ computedViewPassScore }}</strong> 分 ({{ viewData?.pass_percent || 60 }}%)</span>
                </div>
                <div class="info-cell">
                  <span class="info-label">阅卷模式：</span>
                  <el-tag :type="viewData?.verification_mode === 'ai_auto' ? 'success' : 'warning'" size="small">
                    {{ viewData?.verification_mode === 'ai_auto' ? 'AI 全自动审批' : '管理员人工终审' }}
                  </el-tag>
                </div>
                <div class="info-cell">
                  <span class="info-label">出题排列：</span>
                  <span class="info-val">{{ viewData?.is_random ? '随机条目顺序' : '固定题目顺序' }}</span>
                </div>
                <div class="info-cell">
                  <span class="info-label">创 建 人：</span>
                  <span class="info-val" style="color: #475569; font-weight: 600">{{ viewData?.creator_name || '系统内置' }}</span>
                </div>
              </div>
            </div>

            <!-- 2. 题目构成配比胶囊 -->
            <div class="detail-section-card" style="margin-top: 14px">
              <div class="section-title-bar">
                <el-icon class="section-icon"><PieChart /></el-icon>
                <span>题目分析</span>
              </div>
              <div class="q-type-capsules">
                <div class="q-capsule single" v-if="viewQuestionCounts.single > 0">
                  <div class="capsule-icon-wrap single">
                    <el-icon><Aim /></el-icon>
                  </div>
                  <div class="capsule-meta">
                    <span class="capsule-label">单选题</span>
                    <span class="capsule-count">{{ viewQuestionCounts.single }} <small>道</small></span>
                  </div>
                </div>
                <div class="q-capsule multiple" v-if="viewQuestionCounts.multiple > 0">
                  <div class="capsule-icon-wrap multiple">
                    <el-icon><Files /></el-icon>
                  </div>
                  <div class="capsule-meta">
                    <span class="capsule-label">多选题</span>
                    <span class="capsule-count">{{ viewQuestionCounts.multiple }} <small>道</small></span>
                  </div>
                </div>
                <div class="q-capsule judge" v-if="viewQuestionCounts.judge > 0">
                  <div class="capsule-icon-wrap judge">
                    <el-icon><CircleCheck /></el-icon>
                  </div>
                  <div class="capsule-meta">
                    <span class="capsule-label">判断题</span>
                    <span class="capsule-count">{{ viewQuestionCounts.judge }} <small>道</small></span>
                  </div>
                </div>
                <div class="q-capsule fill" v-if="viewQuestionCounts.fill > 0">
                  <div class="capsule-icon-wrap fill">
                    <el-icon><EditPen /></el-icon>
                  </div>
                  <div class="capsule-meta">
                    <span class="capsule-label">填空题</span>
                    <span class="capsule-count">{{ viewQuestionCounts.fill }} <small>道</small></span>
                  </div>
                </div>
                <div class="q-capsule short" v-if="viewQuestionCounts.short > 0">
                  <div class="capsule-icon-wrap short">
                    <el-icon><Notebook /></el-icon>
                  </div>
                  <div class="capsule-meta">
                    <span class="capsule-label">简答题</span>
                    <span class="capsule-count">{{ viewQuestionCounts.short }} <small>道</small></span>
                  </div>
                </div>
                <div class="q-capsule total">
                  <div class="capsule-icon-wrap total">
                    <el-icon><CollectionTag /></el-icon>
                  </div>
                  <div class="capsule-meta">
                    <span class="capsule-label">题目总计</span>
                    <span class="capsule-count">{{ viewQuestions.length }} <small>道</small></span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 3. 完整试题全景列表（免繁琐折叠） -->
            <div class="detail-section-card" style="margin-top: 14px">
              <div class="section-title-bar" style="margin-bottom: 12px">
                <el-icon class="section-icon"><Reading /></el-icon>
                <span>题目与答案详情 (共 {{ viewQuestions.length }} 题)</span>
              </div>

              <div class="questions-stream" v-if="viewQuestions.length">
                <div
                  v-for="(q, qIdx) in viewQuestions"
                  :key="q.id || qIdx"
                  class="question-full-card"
                >
                  <div class="q-head">
                    <span class="q-seq">#{{ qIdx + 1 }}</span>
                    <el-tag :type="getTypeTag(q.type)" size="small" effect="plain" class="q-type-tag">
                      {{ getTypeLabel(q.type) }}
                    </el-tag>
                    <span class="q-score">{{ q.eq_score || q.score || 10 }} 分</span>
                  </div>

                  <!-- 题干 -->
                  <div class="q-content">{{ q.content || q.title }}</div>

                  <!-- 选项列表 (单选/多选/判断) -->
                  <div class="q-options-grid" v-if="getNormalizedOptions(q).length">
                    <div
                      v-for="opt in getNormalizedOptions(q)"
                      :key="opt.key"
                      class="q-option-box"
                      :class="{ 'is-correct': isOptionCorrect(q, opt.key) }"
                    >
                      <span class="opt-prefix">{{ opt.key }}</span>
                      <span class="opt-text">{{ opt.text }}</span>
                      <el-icon v-if="isOptionCorrect(q, opt.key)" class="opt-check-icon"><Check /></el-icon>
                    </div>
                  </div>

                  <!-- 填空题/简答题参考答案 -->
                  <div class="q-answer-box" v-if="!getNormalizedOptions(q).length">
                    <span class="ans-label">正确答案：</span>
                    <span class="ans-text">
                      {{ formatAnswer(q.correct_answer || q.answer) }}
                    </span>
                  </div>
                </div>
              </div>

              <el-empty v-else description="本试卷尚未编排题目" :image-size="70" />
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="考试数据" name="stats">
          <div class="tab-pane-container" v-loading="statsLoading">
            <!-- 判断是否有作答数据 -->
            <template v-if="statsData && statsData.total_participants > 0">
              <!-- 待核验全局警示横幅 (Alert Banner) -->
              <div v-if="statsData.verify_pending > 0" class="pending-verify-alert">
                <div class="alert-content">
                  <span class="alert-badge">待批改</span>
                  <span class="alert-text">
                    检测到本试卷尚有 <strong>{{ statsData.verify_pending }}</strong> 份主观题正在等待人工核验打分。当前得分及格线为 <strong>{{ Math.ceil(statsData.pass_score || computedViewPassScore) }}</strong> 分，待核验试卷暂按客观题初评分呈现。
                  </span>
                </div>
                <el-button
                  type="warning"
                  size="small"
                  class="alert-action-btn"
                  @click="openGradingFromDetail"
                >
                  立即批阅 ({{ statsData.verify_pending }}份)
                </el-button>
              </div>

              <!-- 1. 4大核心 KPI 指标卡 -->
              <div class="stats-kpi-grid">
                <div class="kpi-card users">
                  <div class="kpi-icon-box users">
                    <el-icon><UserFilled /></el-icon>
                  </div>
                  <div class="kpi-info">
                    <span class="kpi-label">参考人员</span>
                    <div class="kpi-val">{{ statsData.total_participants }} <small>人</small></div>
                  </div>
                </div>

                <div class="kpi-card avg">
                  <div class="kpi-icon-box avg">
                    <el-icon><TrendCharts /></el-icon>
                  </div>
                  <div class="kpi-info">
                    <span class="kpi-label">全员平均分</span>
                    <div class="kpi-val">
                      {{ statsData.avg_score }} <small>分</small>
                    </div>
                  </div>
                </div>

                <div class="kpi-card max">
                  <div class="kpi-icon-box max">
                    <el-icon><Trophy /></el-icon>
                  </div>
                  <div class="kpi-info">
                    <span class="kpi-label">最高得分</span>
                    <div class="kpi-val">{{ computedStatsMaxScore }} <small>分</small></div>
                  </div>
                </div>

                <div class="kpi-card rate">
                  <div class="kpi-icon-box rate">
                    <el-icon><Finished /></el-icon>
                  </div>
                  <div class="kpi-info">
                    <span class="kpi-label">考核及格率</span>
                    <div class="kpi-val">{{ statsData.pass_rate }} <small>%</small></div>
                  </div>
                </div>
              </div>

              <!-- 2. 成绩区间分布与态势分析 -->
              <div class="detail-section-card" style="margin-top: 14px">
                <div class="section-title-bar" style="margin-bottom: 12px">
                  <el-icon class="section-icon"><DataLine /></el-icon>
                  <span>成绩分数段分布</span>
                  <span v-if="statsData.verify_pending > 0" class="section-title-tip">
                    * 包含 {{ statsData.verify_pending }} 位待核验成员初评成绩
                  </span>
                </div>
                <div class="score-dist-wrap">
                  <div class="dist-bar-item" v-for="tier in computedScoreDistribution" :key="tier.label">
                    <div class="dist-meta">
                      <span class="tier-label">{{ tier.label }}</span>
                      <span class="tier-count">{{ tier.count }} 人 ({{ tier.percent }}%)</span>
                    </div>
                    <div class="dist-progress-track">
                      <div
                        class="dist-progress-bar"
                        :style="{ width: `${tier.percent}%`, backgroundColor: tier.color }"
                      ></div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 3. 员工实测考核成绩明细 -->
              <div class="detail-section-card" style="margin-top: 14px">
                <div class="section-title-bar" style="margin-bottom: 12px">
                  <el-icon class="section-icon"><List /></el-icon>
                  <span>员工考核作答明细 ({{ statsData.user_records.length }} 条记录)</span>
                </div>

                <el-table
                  :data="statsData.user_records || []"
                  size="small"
                  stripe
                  border
                  class="exam-stats-table"
                  :header-cell-style="{
                    background: '#f1f5f9',
                    color: '#1e293b',
                    fontWeight: '700',
                    fontSize: '13px',
                    borderBottom: '1px solid #cbd5e1'
                  }"
                  style="width: 100%"
                  max-height="320"
                >
                  <el-table-column type="index" label="序号" width="60" align="center" />
                  <el-table-column label="考核成员" min-width="150">
                    <template #default="{ row }">
                      <div class="member-name-cell">
                        <span class="member-real-name">{{ row.nickname || row.username }}</span>
                        <span v-if="row.nickname" class="member-sub-info">({{ row.username }})</span>
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column prop="score" label="考核得分" width="125" align="center">
                    <template #default="{ row }">
                      <div style="display: flex; align-items: center; justify-content: center; gap: 4px">
                        <span
                          class="record-score-tag"
                          :class="row.status === 'pending_verification' ? 'score-pending' : (row.is_passed ? 'score-passed' : 'score-failed')"
                        >
                          {{ row.score }} 分
                        </span>
                        <el-tag v-if="row.status === 'pending_verification'" size="small" type="warning" effect="plain" style="padding: 0 4px; height: 20px; font-size: 11px">初评</el-tag>
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column prop="is_passed" label="判定结果" width="115" align="center">
                    <template #default="{ row }">
                      <el-tag v-if="row.status === 'pending_verification'" type="warning" size="small" effect="dark">
                        待人工核验
                      </el-tag>
                      <el-tag v-else :type="row.is_passed ? 'success' : 'danger'" size="small" effect="light">
                        {{ row.is_passed ? '及格通过' : '未及格' }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="time_spent" label="作答用时" width="115" align="center">
                    <template #default="{ row }">
                      <span style="color: #475569; font-weight: 500">
                        {{ Math.floor(row.time_spent / 60) }}分{{ row.time_spent % 60 }}秒
                      </span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="submit_time" label="交卷时间" min-width="160" />
                </el-table>
              </div>
            </template>

            <!-- 优雅 Empty State 插画 -->
            <div v-else class="exam-empty-box">
              <svg class="empty-svg-art" viewBox="0 0 200 160" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="100" cy="80" r="70" fill="#f1f5f9" />
                <rect x="65" y="45" width="70" height="90" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="2" />
                <line x1="77" y1="65" x2="123" y2="65" stroke="#94a3b8" stroke-width="3" stroke-linecap="round" />
                <line x1="77" y1="80" x2="115" y2="80" stroke="#cbd5e1" stroke-width="3" stroke-linecap="round" />
                <line x1="77" y1="95" x2="105" y2="95" stroke="#cbd5e1" stroke-width="3" stroke-linecap="round" />
                <circle cx="125" cy="120" r="22" fill="#3b82f6" fill-opacity="0.1" stroke="#3b82f6" stroke-width="2" stroke-dasharray="3 3" />
                <path d="M120 120L124 124L131 116" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
              <h4 class="empty-title">暂无考生作答记录</h4>
              <p class="empty-desc">试卷发布上架后，企业员工的真实作答成绩与分析数据将在此实时生成。</p>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <el-button type="primary" @click="viewDialogVisible = false">确认关闭</el-button>
      </template>
    </el-dialog>

    <!-- 新建/编辑 任务 Dialog -->
    <!-- 新建/编辑 试卷 Dialog（工业级精简卡片布局） -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="900px"
      top="25px"
      destroy-on-close
      class="exam-edit-dialog"
    >
      <el-form :model="form" label-position="top" class="edit-exam-form">
        <!-- 1. 基础标题与分类行 -->
        <div class="exam-form-header-grid">
          <div class="header-field title-field">
            <label class="field-label required">试卷名称</label>
            <el-input v-model="form.title" placeholder="请输入试卷标题（如：2026 Q3 企业网络安全合规测评）" clearable />
          </div>
          <div class="header-field cat-field">
            <label class="field-label required">所属分类</label>
            <el-select v-model="form.category_id" placeholder="选择分类" style="width: 100%">
              <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
          </div>
          <div class="header-field status-field">
            <label class="field-label">发布状态</label>
            <el-select v-model="form.status" style="width: 100%">
              <el-option label="暂存草稿 (待上架)" value="draft" />
              <el-option label="直接上线 (立即开放)" value="published" />
            </el-select>
          </div>
        </div>

        <!-- 2. 核心考试规则仪表盘面板 (Settings Strip，告别刺眼蓝框) -->
        <div class="settings-strip-card">
          <!-- 规则网格 -->
          <div class="strip-controls-grid">
            <!-- 限时作答 -->
            <div class="strip-item">
              <div class="strip-item-meta">
                <span class="strip-item-title">限时作答</span>
                <span class="strip-item-desc">开启后交卷计时</span>
              </div>
              <div class="strip-item-ctrl">
                <el-switch v-model="form.is_timed" size="small" />
                <div v-if="form.is_timed" class="time-limit-box">
                  <el-input-number
                    v-model="form.time_limit"
                    :min="1"
                    :max="600"
                    size="small"
                    controls-position="right"
                    style="width: 78px"
                  />
                  <span class="unit">分钟</span>
                </div>
              </div>
            </div>

            <!-- 随机排列 -->
            <div class="strip-item">
              <div class="strip-item-meta">
                <span class="strip-item-title">随机排列</span>
                <span class="strip-item-desc">打乱考卷题目顺序</span>
              </div>
              <el-switch v-model="form.is_random" size="small" />
            </div>

            <!-- 首页推荐 -->
            <div class="strip-item">
              <div class="strip-item-meta">
                <span class="strip-item-title">首页推荐</span>
                <span class="strip-item-desc">置顶展示于推荐位</span>
              </div>
              <el-switch v-model="form.is_recommended" size="small" />
            </div>

            <!-- 简答题阅卷模式 -->
            <div class="strip-item" v-if="hasShortQuestion">
              <div class="strip-item-meta">
                <span class="strip-item-title">AI 核验模式</span>
                <span class="strip-item-desc">主观题阅卷流程</span>
              </div>
              <el-select v-model="form.grading_mode" size="small" style="width: 120px">
                <el-option label="人工终审" value="manual" />
                <el-option label="AI辅助预审" value="ai_pre" />
                <el-option label="AI自动托管" value="ai_auto" />
              </el-select>
            </div>
          </div>

          <!-- 时间与得分综合栏 -->
          <div class="strip-bottom-bar">
            <!-- 开放区间 -->
            <div class="strip-date-cell">
              <span class="bar-label">考试时间：</span>
              <div class="date-pickers-wrap">
                <el-date-picker
                  v-model="form.start_time"
                  type="datetime"
                  placeholder="开始时间(可选)"
                  format="YYYY-MM-DD HH:mm"
                  value-format="YYYY-MM-DDTHH:mm:ss"
                  size="small"
                  style="width: 170px"
                />
                <span class="date-sep">至</span>
                <el-date-picker
                  v-model="form.end_time"
                  type="datetime"
                  placeholder="结束时间(可选)"
                  format="YYYY-MM-DD HH:mm"
                  value-format="YYYY-MM-DDTHH:mm:ss"
                  size="small"
                  style="width: 170px"
                />
              </div>
              <span v-if="timeWindowError" class="window-warn">⚠ {{ timeWindowError }}</span>
              <span v-else class="bar-sub-tip">未设置则长期开放</span>
            </div>

            <!-- 及格门槛与即时计算 -->
            <div class="strip-pass-cell">
              <span class="bar-label">及格比例：</span>
              <div style="width: 110px; margin: 0 10px">
                <el-slider v-model="form.pass_percent" :min="10" :max="100" :step="5" size="small" :show-tooltip="false" />
              </div>
              <span class="pass-val-pill">{{ form.pass_percent }}%</span>
              <span class="pass-calc-tag">
                总分 <strong>{{ computedTotalScore }}</strong> 分 ➔ 
                <strong style="color: #16a34a">{{ computedPassScore }}</strong> 分及格
              </span>
            </div>
          </div>
        </div>

        <!-- 3. 试卷题目编排（直接承接无冗余嵌套） -->
        <div class="exam-questions-section">
          <div class="questions-section-header">
            <div class="header-left">
              <span class="section-title">已选题目</span>
              <span class="section-badge">共 {{ selectedQuestions.length }} 题 · 合计 {{ computedTotalScore }} 分</span>
              <span class="section-tip">可原地修改每题分值与排列顺序</span>
            </div>
            <div class="header-actions">
              <el-button
                v-if="batchRemoveSelectedIds.length > 0"
                type="danger"
                plain
                size="small"
                @click="batchRemoveSelectedQuestions"
              >
                批量删除 ({{ batchRemoveSelectedIds.length }})
              </el-button>
              <el-button type="primary" size="small" class="primary-btn" @click="openPoolModal">
                <el-icon><Plus /></el-icon> 导入 / 添加题目
              </el-button>
            </div>
          </div>

          <el-table
            :data="selectedQuestions"
            size="small"
            border
            stripe
            class="selected-table"
            max-height="340"
            @selection-change="handleSelectedSelectionChange"
          >
            <el-table-column type="selection" width="40" align="center" />
            <el-table-column label="#" width="45" align="center">
              <template #default="{ $index }">
                <span style="font-weight: 700; color: #94a3b8">{{ $index + 1 }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="type" label="题型" width="85" align="center">
              <template #default="{ row }">
                <el-tag size="small" :type="getTypeTag(row.type)" effect="plain">
                  {{ getTypeLabel(row.type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="title" label="题干描述与选项预览" min-width="320">
              <template #default="{ row }">
                <div class="table-q-title">{{ row.title }}</div>
                <ResourcePreview :resource="row" />
              </template>
            </el-table-column>
            <el-table-column label="分值设置" width="115" align="center">
              <template #default="{ row }">
                <el-input-number
                  v-model="row.score"
                  :min="1"
                  :max="100"
                  size="small"
                  controls-position="right"
                  style="width: 82px"
                />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="110" align="center">
              <template #default="{ $index }">
                <div class="row-actions">
                  <el-button :disabled="$index === 0" text circle size="small" title="上移" @click="moveQuestion($index, -1)">▲</el-button>
                  <el-button :disabled="$index === selectedQuestions.length - 1" text circle size="small" title="下移" @click="moveQuestion($index, 1)">▼</el-button>
                  <el-button type="danger" text circle size="small" title="移除" @click="removeSelectedQuestion($index)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-form>

      <template #footer>
        <div class="dialog-footer-wrap">
          <div class="footer-summary">
            已加入 <strong style="color: #0284c7">{{ selectedQuestions.length }}</strong> 道题目，
            试卷总分 <strong style="color: #0284c7">{{ computedTotalScore }}</strong> 分，
            及格分数线 <strong style="color: #16a34a">{{ computedPassScore }}</strong> 分
          </div>
          <div class="footer-btns">
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" class="primary-btn" :loading="saving" @click="saveExam">
              {{ editingId ? '保存修改' : '确认创建试卷' }}
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>

    <!-- 资源库备选选择区 独立弹窗 Dialog -->
    <el-dialog v-model="poolModalVisible" title="选择备选资源库加入当前任务" width="800px" destroy-on-close>
      <div class="pool-modal-content">
        <div class="pool-filter-bar">
          <el-radio-group v-model="poolFilter.type" size="small" @change="handlePoolFilterChange">
            <el-radio-button label="">全部题型</el-radio-button>
            <el-radio-button label="single">单选</el-radio-button>
            <el-radio-button label="multiple">多选</el-radio-button>
            <el-radio-button label="judge">判断</el-radio-button>
            <el-radio-button label="fill">填空</el-radio-button>
            <el-radio-button label="short">简答</el-radio-button>
          </el-radio-group>
          <el-input v-model="poolFilter.keyword" placeholder="搜索题干关键词..." size="small" clearable style="width: 200px" @change="handlePoolFilterChange" />
        </div>

        <el-table
          :data="questionPool"
          size="small"
          v-loading="poolLoading"
          stripe
          style="width: 100%; margin-top: 12px"
          max-height="360"
          @selection-change="handlePoolSelectionChange"
        >
          <el-table-column type="selection" width="45" align="center" :selectable="selectablePoolRow" />
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="type" label="题型" width="85">
            <template #default="{ row }">
              <el-tag size="small" :type="getTypeTag(row.type)">{{ getTypeLabel(row.type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="title" label="题干描述" show-overflow-tooltip />
          <el-table-column prop="score" label="分值" width="75">
            <template #default="{ row }">
              <span>{{ row.score || 10 }}分</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="90" align="center">
            <template #default="{ row }">
              <el-tag v-if="isQuestionSelected(row.id)" type="info" size="small">已在任务中</el-tag>
              <el-tag v-else type="success" size="small">可选加入</el-tag>
            </template>
          </el-table-column>
        </el-table>

        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px">
          <span style="font-size: 13px; color: #64748b">勾选可多选添加，已勾选 {{ pendingPoolSelection.length }} 项</span>
          <el-pagination
            size="small"
            v-model:current-page="poolFilter.page"
            :page-size="poolFilter.size"
            :total="poolFilter.total"
            layout="total, prev, pager, next"
            @current-change="handlePoolPageChange"
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="poolModalVisible = false">完成选择</el-button>
        <el-button type="primary" :disabled="pendingPoolSelection.length === 0" @click="confirmAddBatchFromPool">
          确认加入已选 ({{ pendingPoolSelection.length }})
        </el-button>
      </template>
    </el-dialog>
    <!-- ✨ AI 智能一键编排 Dialog (v1.2 Step4: 极简两项必填 + 生成后原地审阅) -->
    <el-dialog v-model="aiExamVisible" :title="aiReviewVisible ? '✨ AI 试卷审阅' : '✨ AI 创建试卷'" width="700px" destroy-on-close @open="handleOpenAiExam">
      <div
        v-loading="aiExamLoading"
        element-loading-text="AI 智能组卷编排中，正在调优题干与选项，请稍候..."
        element-loading-background="rgba(255, 255, 255, 0.9)"
        class="ai-exam-dialog-body"
      >
        <!-- 默认行为提示 -->
        <el-alert type="info" :closable="false" show-icon style="margin-bottom: 12px"
                  title="默认题目数量 10 题 · 默认考试时间为 7 天 · 题型不写默认随机" />
        <!-- 生成后所见即所得审阅清单 -->
        <div v-if="aiReviewVisible">
          <el-alert type="success" :closable="false" show-icon style="margin-bottom: 14px"
                    :title="aiExamResult || 'AI 编排完成，请核对条目后确认保存'" />
          <div class="ai-review-list">
            <div v-for="(q, idx) in aiReviewQuestions" :key="q.id || idx" class="ai-review-card">
              <div class="ai-review-head">
                <span class="ai-review-index">第 {{ idx + 1 }} 题</span>
                <el-tag size="small" :type="getTypeTag(q.type)">{{ getTypeLabel(q.type) }}</el-tag>
                <span class="ai-review-score">{{ q.score || 10 }} 分</span>
              </div>
              <div class="ai-review-title">{{ q.title }}</div>
              <ResourcePreview :resource="q" />
            </div>
          </div>
        </div>

        <!-- 创建表单：核心两项（试卷需求 + 试卷分类）必填，其余按需折叠 -->
        <el-form v-else label-width="100px">
          <el-form-item label="试卷需求" required>
            <el-input v-model="aiExamForm.description" type="textarea" :rows="3"
                      placeholder="例如：帮我组一份消防安全测试卷，包含3道单选、2道判断、1道简答，难度中等" />
          </el-form-item>
          <el-form-item label="试卷分类" required>
            <el-select v-model="aiExamForm.category_id" placeholder="请选择任务分类" style="width: 100%">
              <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
            <div class="score-calc-tip" style="margin-top: 4px; color: #64748b; font-size: 12px">
              必填：明确任务归属分类，方便在任务列表与成员端按资源库维度归类展示
            </div>
          </el-form-item>

          <el-collapse>
            <el-collapse-item title="高级选项（考试时间 / 试卷标题 / 题目数量 / 难度 / 限时 / 及格线，已设最优默认）" name="advanced">
              <el-form-item v-if="ragDocs.length" label="参考私有文库">
                <el-select v-model="aiExamForm.doc_ids" multiple collapse-tags collapse-tags-tooltip clearable
                           placeholder="选填可多选：勾选后优先依据所选私有文库编排，条目将自动附带切片溯源" style="width: 100%">
                  <el-option v-for="d in ragDocs" :key="d.id" :label="`${d.filename}（${d.total_chunks}块切片）`" :value="d.id" />
                </el-select>
                <div class="score-calc-tip" style="margin-top: 4px; color: #64748b; font-size: 12px">
                  已检测到您的私有文库资料；若所选文档与编排需求不相关，系统将自动脱钩并以通识出卷，避免张冠李戴
                </div>
              </el-form-item>
              <el-form-item label="考试时间">
                <div style="display: flex; align-items: center; gap: 10px; width: 100%">
                  <el-date-picker v-model="aiExamForm.start_time" type="datetime" placeholder="默认当前时间" format="YYYY-MM-DD HH:mm"
                                  value-format="YYYY-MM-DDTHH:mm:ss" :disabled-date="disablePastDate" style="flex: 1" />
                  <span style="color: #94a3b8">至</span>
                  <el-date-picker v-model="aiExamForm.end_time" type="datetime" placeholder="默认 7 天后" format="YYYY-MM-DD HH:mm"
                                  value-format="YYYY-MM-DDTHH:mm:ss" :disabled-date="disableBeforeStart" style="flex: 1" />
                </div>
                <div class="score-calc-tip" style="margin-top: 4px; color: #64748b; font-size: 12px">
                  选填：不填写时系统将自动默认设置为当前时间起 7 天开放区间（如需指定任务开放窗口可在此设置）
                </div>
              </el-form-item>
              <el-form-item label="试卷标题">
                <el-input v-model="aiExamForm.title" placeholder="留空则由 AI 命名" />
              </el-form-item>
              <el-form-item label="题目数量">
                <el-input-number v-model="aiExamForm.count" :min="1" :max="20" style="width: 200px" />
                <div class="score-calc-tip" style="margin-top: 4px; color: #64748b; font-size: 12px">
                  默认 10 题；需求里写了题型/数量则以需求为准，否则按此数量随机题型
                </div>
              </el-form-item>
              <el-form-item label="条目难度">
                <el-radio-group v-model="aiExamForm.difficulty">
                  <el-radio label="easy">简单</el-radio>
                  <el-radio label="medium">中等</el-radio>
                  <el-radio label="hard">困难</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item label="限时作答">
                <div style="display: flex; align-items: center; gap: 12px">
                  <el-switch v-model="aiExamForm.is_timed" />
                  <div v-if="aiExamForm.is_timed" style="display: flex; align-items: center; gap: 6px">
                    <el-input-number v-model="aiExamForm.time_limit" :min="5" :max="300" size="default" style="width: 130px" />
                    <span style="font-size: 13px; color: #64748b">分钟</span>
                  </div>
                  <span v-else style="font-size: 13px; color: #94a3b8">不限时长</span>
                </div>
              </el-form-item>
              <el-form-item label="及格比例">
                <div style="display: flex; align-items: center; width: 100%; gap: 16px">
                  <el-slider v-model="aiExamForm.pass_percent" :min="10" :max="100" :step="5" style="flex: 1" />
                  <span style="font-weight: 700; width: 50px; color: #0284c7">{{ aiExamForm.pass_percent }}%</span>
                </div>
                <div class="score-calc-tip" style="margin-top: 4px; color: #64748b; font-size: 12px">
                  💡 及格分数将在 AI 生成条目并进入修改界面选定最终试题及分值后自动向上取整计算
                </div>
              </el-form-item>
            </el-collapse-item>
          </el-collapse>
        </el-form>
      </div>
      <template #footer>
        <template v-if="aiReviewVisible">
          <el-button @click="aiReviewVisible = false">返回修改</el-button>
          <el-button type="primary" @click="confirmAiExam">确认保存试卷</el-button>
        </template>
        <template v-else>
          <el-button @click="aiExamVisible = false">关闭</el-button>
          <el-button type="warning" :loading="aiExamLoading" @click="generateAiExam">
            {{ aiExamLoading ? 'AI 创建中...' : '开始 AI 创建' }}
          </el-button>
        </template>
      </template>
    </el-dialog>

    <!-- v1.2 Step3: 主观题核验抽屉 (行内待办原地核验) -->
    <VerifyDrawer
      :visible="gradingVisible"
      :task-id="gradingExam?.id ?? null"
      :task-title="gradingExam?.title ?? ''"
      @update:visible="gradingVisible = $event"
      @graded="handleGraded"
    />

    <!-- 行级核验大厅全屏弹窗 -->
    <TaskVerifyDialog
      :visible="gradingHallVisible"
      :task-id="gradingHallExam?.id ?? null"
      :task-title="gradingHallExam?.title ?? ''"
      @update:visible="gradingHallVisible = $event"
      @graded="handleGraded"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  Plus, Delete, View, Search, RefreshRight, Document, PieChart, Reading,
  Aim, Files, CircleCheck, EditPen, Notebook, CollectionTag, Check,
  UserFilled, TrendCharts, Trophy, Finished, DataLine, List
} from '@element-plus/icons-vue';
import request from '../../utils/request';
import VerifyDrawer from './components/VerifyDrawer.vue';
import TaskVerifyDialog from './components/TaskVerifyDialog.vue';
import ResourcePreview from './components/ResourcePreview.vue';

const loading = ref(false);

const exams = ref<any[]>([]);
const categories = ref<any[]>([]);
const filters = reactive({ keyword: '', category_id: null as number | null, status: '' });

const handleSearch = () => {
  pagination.page = 1;
  loadExams();
};

const handleReset = () => {
  filters.keyword = '';
  filters.category_id = null;
  filters.status = '';
  pagination.page = 1;
  loadExams();
};
const pagination = reactive({ page: 1, size: 10, total: 0 });

const dialogVisible = ref(false);
const editingId = ref<number | null>(null);
const dialogTitle = computed(() => (editingId.value ? '编辑试卷' : '新建试卷'));
const saving = ref(false);

// 试卷综合详情（双 Tab）状态
const viewDialogVisible = ref(false);
const viewActiveTab = ref('exam');
const viewData = ref<any>(null);
const viewQuestions = ref<any[]>([]);
const viewDetailLoading = ref(false);
const statsLoading = ref(false);
const statsData = ref<any>(null);

// 统计各题型数量
const viewQuestionCounts = computed(() => {
  const counts = { single: 0, multiple: 0, judge: 0, fill: 0, short: 0 };
  for (const q of viewQuestions.value) {
    const t = q.type || 'single';
    if (t === 'single' || t === 'single_choice') counts.single++;
    else if (t === 'multiple' || t === 'multiple_choice') counts.multiple++;
    else if (t === 'judge') counts.judge++;
    else if (t === 'fill' || t === 'fill_in') counts.fill++;
    else if (t === 'short' || t === 'short_answer') counts.short++;
    else counts.single++;
  }
  return counts;
});

// 计算试卷题目总分与及格分
const computedViewTotalScore = computed(() => {
  if (!viewQuestions.value.length) return viewData.value?.total_score || 0;
  return viewQuestions.value.reduce((sum, q) => sum + (q.eq_score || q.score || 10), 0);
});

const computedViewPassScore = computed(() => {
  const total = computedViewTotalScore.value;
  const pct = viewData.value?.pass_percent || 60;
  return Math.ceil((total * pct) / 100);
});

// 计算作答最高分
const computedStatsMaxScore = computed(() => {
  if (!statsData.value?.user_records?.length) return 0;
  const scores = statsData.value.user_records.map((r: any) => r.score || 0);
  return Math.max(...scores);
});

// 计算成绩分数段分布
const computedScoreDistribution = computed(() => {
  const records = statsData.value?.user_records || [];
  const total = records.length;
  if (!total) return [];

  let tier90 = 0; // 90~100
  let tier80 = 0; // 80~89
  let tier60 = 0; // 60~79
  let tierFail = 0; // <60

  for (const r of records) {
    const s = r.score || 0;
    if (s >= 90) tier90++;
    else if (s >= 80) tier80++;
    else if (s >= 60) tier60++;
    else tierFail++;
  }

  return [
    { label: '90 - 100分 (优秀)', count: tier90, percent: Math.round((tier90 / total) * 100), color: '#3b82f6' },
    { label: '80 - 89分 (良好)', count: tier80, percent: Math.round((tier80 / total) * 100), color: '#10b981' },
    { label: '60 - 79分 (及格)', count: tier60, percent: Math.round((tier60 / total) * 100), color: '#f59e0b' },
    { label: '< 60分 (不及格)', count: tierFail, percent: Math.round((tierFail / total) * 100), color: '#ef4444' }
  ];
});

// 规范化题目选项：兼容对象列表 [{key, text}]、字符串列表 ['A. 3-5分钟'] 以及 JSON 字符串
const getNormalizedOptions = (q: any): Array<{ key: string; text: string }> => {
  if (!q) return [];
  let raw = q.options;
  if (!raw) return [];

  // 若为序列化字符串则尝试解析
  if (typeof raw === 'string') {
    try {
      raw = JSON.parse(raw);
    } catch {
      return [];
    }
  }

  if (!Array.isArray(raw)) return [];

  const keys = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
  return raw.map((item: any, idx: number) => {
    if (typeof item === 'object' && item !== null) {
      const k = String(item.key || item.label || item.value || keys[idx] || '').trim().toUpperCase();
      const t = String(item.text ?? item.content ?? item.title ?? '').trim();
      return { key: k, text: t };
    }
    // 字符串格式，形如 "A. 3-5分钟" 或 "A、xxx" 或纯文本 "3-5分钟"
    const str = String(item).trim();
    const match = str.match(/^([A-Za-z])[\.\s\-:]+\s*(.*)$/);
    if (match) {
      return {
        key: match[1].toUpperCase(),
        text: match[2].trim()
      };
    }
    return {
      key: keys[idx] || `Opt${idx + 1}`,
      text: str
    };
  });
};

// 辅助函数：判断某个选项是否为正确答案
const isOptionCorrect = (q: any, optKey: string) => {
  const ans = q.correct_answer || q.answer;
  if (!ans) return false;
  const target = String(optKey).trim().toUpperCase();
  if (Array.isArray(ans)) {
    return ans.map((a) => String(a).trim().toUpperCase()).includes(target);
  }
  return String(ans).trim().toUpperCase() === target;
};

// 格式化展示填空或简答题答案
const formatAnswer = (ans: any) => {
  if (!ans) return '未设置参考答案';
  if (Array.isArray(ans)) {
    return ans.join('、');
  }
  return String(ans);
};

// 表单对象
const form = reactive({
  title: '',
  category_id: null as number | null,
  is_timed: true,
  time_limit: 30,
  start_time: null as string | null,
  end_time: null as string | null,
  pass_percent: 60,
  status: 'draft',
  is_recommended: false,
  is_random: false,
  is_ai_auto_grade: false,
  grading_mode: 'ai_pre' as string
});

// ---- v1.2 时间锁与 AI 全托管 ----
const windowMinutes = computed(() => {
  if (!form.start_time || !form.end_time) return 0;
  return Math.floor((new Date(form.end_time).getTime() - new Date(form.start_time).getTime()) / 60000);
});

const timeWindowError = computed(() => {
  if (!form.start_time || !form.end_time) return '';
  if (windowMinutes.value <= 0) return '结束时间必须晚于开始时间';
  if (form.is_timed && form.time_limit > windowMinutes.value) {
    return `任务限时不能大于开放区间 ${windowMinutes.value} 分钟`;
  }
  return '';
});

const hasShortQuestion = computed(() =>
  selectedQuestions.value.some((q) => q.type === 'short')
);

const selectedQuestions = ref<any[]>([]);
const batchRemoveSelectedIds = ref<number[]>([]);

// 资源库选择 Dialog 独立弹窗
const poolModalVisible = ref(false);
const questionPool = ref<any[]>([]);
const poolLoading = ref(false);
const poolFilter = reactive({ type: '', keyword: '', page: 1, size: 10, total: 0 });
const pendingPoolSelection = ref<any[]>([]);

const computedTotalScore = computed(() => {
  return selectedQuestions.value.reduce((sum, item) => sum + (item.score || 10), 0);
});

const computedPassScore = computed(() => {
  const total = computedTotalScore.value;
  const pct = form.pass_percent || 60;
  return Math.ceil((total * pct) / 100);
});

const loadCategories = async () => {
  try {
    const res: any = await request.get('/api/v1/admin/categories', {
      params: { target_type: 'task' }
    });
    categories.value = res.items || [];
  } catch (e) {
    categories.value = [];
  }
};

const getCategoryName = (catId: number | null) => {
  if (!catId) return '未分类';
  const c = categories.value.find((item) => item.id === catId);
  return c ? c.name : `任务分类#${catId}`;
};

const loadExams = async () => {
  loading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/tasks', {
      params: { ...filters, page: pagination.page, size: pagination.size }
    });
    exams.value = res.items || [];
    pagination.total = res.total || 0;
  } finally {
    loading.value = false;
  }
};

const handleSwitchBeforeChange = (row: any): Promise<boolean> => {
  const willPublish = row.status !== 'published';
  const newStatus = willPublish ? 'published' : 'archived';

  if (!willPublish) {
    // 下架需确认提醒
    return new Promise((resolve) => {
      ElMessageBox.confirm(
        '下架后任务将停止对成员开放（无成员作答时可重新编辑、上架或彻底删除；已有作答成绩则保留归档）。确定要下架吗？',
        '下架确认',
        {
          type: 'warning',
          confirmButtonText: '确认下架',
          cancelButtonText: '取消'
        }
      ).then(async () => {
        row._statusLoading = true;
        try {
          await request.put(`/api/v1/admin/tasks/${row.id}/status?status=${newStatus}`);
          row.status = newStatus;
          ElMessage.success('试卷已成功下架');
          resolve(true);
        } catch {
          resolve(false);
        } finally {
          row._statusLoading = false;
        }
      }).catch(() => {
        resolve(false);
      });
    });
  } else {
    // 上架直接发布
    return new Promise(async (resolve) => {
      row._statusLoading = true;
      try {
        await request.put(`/api/v1/admin/tasks/${row.id}/status?status=${newStatus}`);
        row.status = newStatus;
        ElMessage.success('试卷已成功发布上线');
        resolve(true);
      } catch {
        resolve(false);
      } finally {
        row._statusLoading = false;
      }
    });
  }
};

const loadTaskStats = async (taskId: number) => {
  statsLoading.value = true;
  try {
    const stats: any = await request.get(`/api/v1/admin/tasks/${taskId}/stats`);
    statsData.value = stats;
  } catch {
    statsData.value = null;
  } finally {
    statsLoading.value = false;
  }
};

const openViewDialog = async (row: any) => {
  viewData.value = row;
  viewActiveTab.value = 'exam';
  viewDialogVisible.value = true;
  viewDetailLoading.value = true;
  viewQuestions.value = [];
  statsData.value = null;

  // 并行请求试卷题目详情与考试作答统计数据
  const fetchDetail = request.get(`/api/v1/admin/tasks/${row.id}`)
    .then((detail: any) => {
      viewQuestions.value = detail?.questions || [];
    })
    .catch(() => {
      viewQuestions.value = [];
    })
    .finally(() => {
      viewDetailLoading.value = false;
    });

  const fetchStats = loadTaskStats(row.id);
  await Promise.allSettled([fetchDetail, fetchStats]);
};

const openPoolModal = () => {
  poolModalVisible.value = true;
  pendingPoolSelection.value = [];
  loadQuestionPool();
};

const loadQuestionPool = async () => {
  poolLoading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/resources', {
      params: { 
        type: poolFilter.type, 
        keyword: poolFilter.keyword, 
        page: poolFilter.page, 
        size: poolFilter.size 
      }
    });
    questionPool.value = res.items || [];
    poolFilter.total = res.total || 0;
  } finally {
    poolLoading.value = false;
  }
};

const handlePoolPageChange = (page: number) => {
  poolFilter.page = page;
  loadQuestionPool();
};

const handlePoolFilterChange = () => {
  poolFilter.page = 1;
  loadQuestionPool();
};

const isQuestionSelected = (qId: number) => {
  return selectedQuestions.value.some((q) => q.id === qId);
};

const selectablePoolRow = (row: any) => {
  return !isQuestionSelected(row.id);
};

const handlePoolSelectionChange = (val: any[]) => {
  pendingPoolSelection.value = val;
};

const confirmAddBatchFromPool = () => {
  let count = 0;
  for (const q of pendingPoolSelection.value) {
    if (!isQuestionSelected(q.id)) {
      selectedQuestions.value.push(q);
      count++;
    }
  }
  ElMessage.success(`成功加入 ${count} 道条目`);
  poolModalVisible.value = false;
};

const handleSelectedSelectionChange = (val: any[]) => {
  batchRemoveSelectedIds.value = val.map((q) => q.id);
};

const batchRemoveSelectedQuestions = () => {
  if (batchRemoveSelectedIds.value.length === 0) return;
  selectedQuestions.value = selectedQuestions.value.filter((q) => !batchRemoveSelectedIds.value.includes(q.id));
  batchRemoveSelectedIds.value = [];
  ElMessage.success('已从当前编排中移除选中条目');
};

const removeSelectedQuestion = (idx: number) => {
  selectedQuestions.value.splice(idx, 1);
};

const moveQuestion = (index: number, direction: number) => {
  const targetIndex = index + direction;
  if (targetIndex < 0 || targetIndex >= selectedQuestions.value.length) return;
  const temp = selectedQuestions.value[index];
  selectedQuestions.value[index] = selectedQuestions.value[targetIndex];
  selectedQuestions.value[targetIndex] = temp;
};

const getTypeTag = (type: string) => {
  if (type === 'single' || type === 'single_choice') return 'primary';
  if (type === 'multiple' || type === 'multiple_choice') return 'warning';
  if (type === 'judge') return 'info';
  if (type === 'fill' || type === 'fill_in') return 'success';
  if (type === 'short' || type === 'short_answer') return 'danger';
  return 'info';
};

const getTypeLabel = (type: string) => {
  if (type === 'single' || type === 'single_choice') return '单选题';
  if (type === 'multiple' || type === 'multiple_choice') return '多选题';
  if (type === 'judge') return '判断题';
  if (type === 'fill' || type === 'fill_in') return '填空题';
  if (type === 'short' || type === 'short_answer') return '简答题';
  return '选择题';
};

const openCreateDialog = () => {
  editingId.value = null;
  form.title = '';
  form.category_id = categories.value.length > 0 ? categories.value[0].id : null;
  form.is_timed = true;
  form.time_limit = 30;
  form.start_time = null;
  form.end_time = null;
  form.pass_percent = 60;
  form.status = 'draft';
  form.is_recommended = false;
  form.is_random = false;
  form.is_ai_auto_grade = false;
  form.grading_mode = 'ai_pre';
  selectedQuestions.value = [];
  batchRemoveSelectedIds.value = [];
  poolFilter.type = '';
  poolFilter.keyword = '';
  dialogVisible.value = true;
};

const openEditDialog = async (row: any) => {
  if (row.status === 'published') {
    ElMessage.warning('已上架任务已锁定编排编辑，请先下架后再进行修改');
    return;
  }
  if (row.status === 'archived') {
    ElMessage.warning('该任务已归档冻结，不可编辑');
    return;
  }
  editingId.value = row.id;
  form.title = row.title;
  form.category_id = categories.value.some((c) => c.id === row.category_id) ? row.category_id : null;
  form.is_timed = row.is_timed;
  form.time_limit = row.time_limit;
  form.start_time = row.start_time || null;
  form.end_time = row.end_time || null;
  form.pass_percent = row.pass_percent || 60;
  form.status = row.status || 'draft';
  form.is_recommended = row.is_recommended;
  form.is_random = row.is_random || false;
  form.is_ai_auto_grade = row.is_ai_auto_grade || false;
  form.grading_mode = row.grading_mode || (row.is_ai_auto_grade ? 'ai_auto' : 'ai_pre');
  selectedQuestions.value = [];
  batchRemoveSelectedIds.value = [];
  poolFilter.type = '';
  poolFilter.keyword = '';
  dialogVisible.value = true;

  try {
    const detail: any = await request.get(`/api/v1/admin/tasks/${row.id}`);
    selectedQuestions.value = detail.questions || [];
  } catch (e) {
    selectedQuestions.value = [];
  }
};

const saveExam = async () => {
  if (!form.title) {
    ElMessage.error('试卷名称不能为空');
    return;
  }
  if (!form.category_id) {
    ElMessage.error('请选择试卷分类');
    return;
  }
  if (selectedQuestions.value.length === 0) {
    ElMessage.error('试卷至少需要加入 1 道题目');
    return;
  }
  if (timeWindowError.value) {
    ElMessage.error(timeWindowError.value);
    return;
  }

  saving.value = true;
  // v1.2 Step4: 简答题智能展开 grading_mode；全客观题固定 manual（纯代码秒出分，用量计入看板统计）
  const resolvedMode = hasShortQuestion.value ? form.grading_mode : 'manual';
  const payload = {
    title: form.title,
    category_id: form.category_id,
    is_timed: form.is_timed,
    time_limit: form.time_limit,
    start_time: form.start_time || null,
    end_time: form.end_time || null,
    pass_percent: form.pass_percent,
    status: form.status,
    is_recommended: form.is_recommended,
    is_random: form.is_random,
    is_ai_auto_grade: resolvedMode === 'ai_auto',
    grading_mode: resolvedMode,
    question_ids: selectedQuestions.value.map((q) => q.id),
    questions: selectedQuestions.value.map((q) => ({ id: q.id, score: Number(q.score) || 10 }))
  };

  try {
    if (editingId.value) {
      await request.put(`/api/v1/admin/tasks/${editingId.value}`, payload);
      ElMessage.success('试卷及题目已成功修改');
    } else {
      await request.post('/api/v1/admin/tasks', payload);
      ElMessage.success('试卷及题目已成功创建');
    }
    dialogVisible.value = false;
    loadExams();
  } finally {
    saving.value = false;
  }
};

const handleDelete = (id: number) => {
  ElMessageBox.confirm('确定要删除该试卷吗？未上架或已下架且无成员作答的试卷可彻底删除，删除后不可恢复。', '提示', { type: 'warning' }).then(async () => {
    await request.delete(`/api/v1/admin/tasks/${id}`);
    ElMessage.success('试卷删除成功');
    loadExams();
  });
};

// ---- v1.2 Step3: 行内待办 → 核验抽屉 ----
const gradingVisible = ref(false);
const gradingExam = ref<any>(null);

const handleOpenGrading = (row: any) => {
  gradingExam.value = row;
  gradingVisible.value = true;
};

// 从试卷综合详情弹窗内一键直达核验抽屉
const openGradingFromDetail = () => {
  if (!viewData.value) return;
  handleOpenGrading(viewData.value);
};

const handleGraded = () => {
  loadExams();
  // 若当前正打开着试卷详情弹窗，实时重新拉取最新批改统计数据
  if (viewDialogVisible.value && viewData.value?.id) {
    loadTaskStats(viewData.value.id);
  }
};

// ---- 行级核验大厅全屏弹窗 ----
const gradingHallVisible = ref(false);
const gradingHallExam = ref<any>(null);

const openGradingHall = (row: any) => {
  gradingHallExam.value = row;
  gradingHallVisible.value = true;
};

// ---- v1.2 Step4: ✨ AI 智能一键编排 (极简两项 + 审阅确认) ----
const aiExamVisible = ref(false);
const aiExamLoading = ref(false);
const aiExamResult = ref('');
const aiReviewVisible = ref(false);
const aiReviewQuestions = ref<any[]>([]);
const ragDocs = ref<any[]>([]);

const loadRagDocs = async () => {
  try {
    const res: any = await request.get('/api/v1/admin/kb/documents');
    ragDocs.value = (res.items || []).map((d: any) => ({ ...d, filename: d.file_name, status: 'done' }));
  } catch (e) {
    ragDocs.value = [];
  }
};

const aiExamForm = reactive({
  description: '',
  title: '',
  category_id: null as number | null,
  doc_ids: [] as number[],
  difficulty: 'medium',
  count: 10,
  is_timed: true,
  time_limit: 30,
  start_time: null as string | null,
  end_time: null as string | null,
  pass_percent: 60
});
let aiExamId: number | null = null;

const aiWindowMinutes = computed(() => {
  if (!aiExamForm.start_time || !aiExamForm.end_time) return 0;
  return Math.floor((new Date(aiExamForm.end_time).getTime() - new Date(aiExamForm.start_time).getTime()) / 60000);
});

// 开始时间不得早于现在（精确到天禁用过去日期，提交时精确到分钟复核）
const disablePastDate = (date: Date): boolean => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return date.getTime() < today.getTime();
};

// 结束时间须晚于开始时间（未选开始则不早于今天）
const disableBeforeStart = (date: Date): boolean => {
  if (aiExamForm.start_time) {
    return date.getTime() < new Date(aiExamForm.start_time).getTime();
  }
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return date.getTime() < today.getTime();
};

// 打开 AI 创建弹窗时自动回显默认分类（若未选择）并拉取私有文库可用文档
const handleOpenAiExam = () => {
  aiReviewVisible.value = false;
  aiReviewQuestions.value = [];
  aiExamResult.value = '';
  aiExamForm.doc_ids = [];
  aiExamForm.count = 10;
  loadRagDocs();
  if (!aiExamForm.category_id && categories.value.length > 0) {
    aiExamForm.category_id = categories.value[0].id;
  }
};

const generateAiExam = async () => {
  if (!aiExamForm.description.trim()) {
    ElMessage.error('请描述试卷需求');
    return;
  }
  if (!aiExamForm.category_id) {
    ElMessage.error('请选择试卷分类');
    return;
  }

  // 考试时间选填校验
  if (aiExamForm.start_time && new Date(aiExamForm.start_time).getTime() < Date.now() - 60000) {
    ElMessage.error('开始时间不能早于现在');
    return;
  }
  if (aiExamForm.start_time && aiExamForm.end_time) {
    if (aiWindowMinutes.value <= 0) {
      ElMessage.error('考试结束时间必须晚于开始时间');
      return;
    }
    if (aiExamForm.is_timed && aiExamForm.time_limit > aiWindowMinutes.value) {
      ElMessage.error(`任务限时不能大于开放区间 ${aiWindowMinutes.value} 分钟`);
      return;
    }
  }

  // 题型数量确定：需求里写明则解析，否则按高级选项数量随机题型
  const specs = hasExplicitSpec(aiExamForm.description)
    ? parseSpecs(aiExamForm.description)
    : randomSpecs(aiExamForm.count || 10);

  aiExamLoading.value = true;
  aiReviewVisible.value = false;
  aiReviewQuestions.value = [];
  try {
    const res: any = await request.post('/api/v1/admin/ai/exams/generate', {
      title: aiExamForm.title || undefined,
      description: aiExamForm.description,
      specs,
      difficulty: aiExamForm.difficulty,
      category_id: aiExamForm.category_id,
      doc_ids: aiExamForm.doc_ids.length ? aiExamForm.doc_ids : undefined,
      is_timed: aiExamForm.is_timed,
      time_limit: aiExamForm.is_timed ? aiExamForm.time_limit : 0,
      start_time: aiExamForm.start_time || undefined,
      end_time: aiExamForm.end_time || undefined,
      pass_percent: aiExamForm.pass_percent
    }, { timeout: 180000 }); // 真实大模型编排较慢, 覆盖全局 10s 超时
    aiExamId = res.exam_id;
    aiExamResult.value = res.message || `已生成草稿，共 ${res.question_count} 题（AI 新生成 ${res.new_questions} 题）`;
    // 大模型实时全量原创生成条目，弹窗原地切换为审阅卡片（选项与正确答案绿色高亮）
    aiReviewQuestions.value = res.questions || [];
    aiReviewVisible.value = true;
    loadExams();
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    aiExamLoading.value = false;
  }
};

// 审阅无误后手动确认落库（后端已存为草稿，此处确认并刷新列表）
const confirmAiExam = () => {
  ElMessage.success('任务已保存为草稿，请检查无误后手动上架');
  aiExamVisible.value = false;
  aiReviewVisible.value = false;
  aiExamResult.value = '';
  aiExamId = null;
  loadExams();
};

// 需求里是否写明了题型/数量（写明则解析，否则随机题型）
const hasExplicitSpec = (text: string) => {
  return /(\d+)\s*道?(单选|多选|判断|填空|简答)/.test(text) ||
    /(\d+)\s*(?:道|个|条)?(?:题|条目|试题)/.test(text);
};

// 题型不写默认随机：把总数随机分配到各题型，保证总数精确且至少两种题型
const randomSpecs = (total: number) => {
  const types = ['single', 'multiple', 'judge', 'fill', 'short'];
  const n = Math.max(1, Math.min(20, total || 10));
  const picked = [...types].sort(() => Math.random() - 0.5).slice(0, Math.min(types.length, Math.max(2, Math.ceil(n / 3))));
  const counts = picked.map(() => 1);
  let rest = n - counts.length;
  let i = 0;
  while (rest > 0) {
    counts[i % counts.length]++;
    rest--;
    i++;
  }
  return picked.map((q_type, idx) => ({ q_type, count: counts[idx] }));
};

// 从自然语言需求中粗提取题型构成 ("3道单选、2道判断、1道简答" 或 "生成6道条目")
const parseSpecs = (text: string) => {
  const specs: Array<{ q_type: string; count: number }> = [];
  const patterns: Array<[RegExp, string]> = [
    [/(\d+)\s*道?单选/, 'single'],
    [/(\d+)\s*道?多选/, 'multiple'],
    [/(\d+)\s*道?判断/, 'judge'],
    [/(\d+)\s*道?填空/, 'fill'],
    [/(\d+)\s*道?简答/, 'short']
  ];
  for (const [re, t] of patterns) {
    const m = text.match(re);
    if (m) specs.push({ q_type: t, count: parseInt(m[1]) });
  }
  if (specs.length === 0) {
    // 匹配如 "6道条目", "生成6题", "共6道" 等泛指数量
    const totalMatch = text.match(/(\d+)\s*(?:道|个|条)?(?:题|条目|试题)/);
    const count = totalMatch ? parseInt(totalMatch[1]) : 5;
    specs.push({ q_type: 'single', count: count });
  }
  return specs;
};

onMounted(() => {
  loadCategories();
  loadExams();
});
</script>

<style scoped>
.page-card {
  background: #ffffff;
  border-radius: 18px;
  padding: 24px 28px;
  box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.05), 0 20px 25px -5px rgba(0, 0, 0, 0.02), 0 1px 3px rgba(0, 0, 0, 0.03);
  border: none;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.filters {
  display: flex;
  gap: 14px;
  align-items: center;
}

/* 高定圆角输入框与选择器 */
.custom-search-input :deep(.el-input__wrapper),
.custom-filter-select :deep(.el-select__wrapper) {
  border-radius: 10px !important;
  background-color: #ffffff !important;
  box-shadow: 0 0 0 1px #e2e8f0 inset !important;
  transition: all 0.2s ease !important;
  padding: 5px 14px !important;
}

.custom-search-input :deep(.el-input__wrapper.is-focus),
.custom-filter-select :deep(.el-select__wrapper.is-focused) {
  box-shadow: 0 0 0 2px #1d4ed8 inset !important;
}

.search-prefix-icon {
  color: #94a3b8;
  font-size: 15px;
}

/* 顶部深蓝主创建按钮 */
.primary-create-btn {
  background: #1d4ed8 !important;
  border-color: #1d4ed8 !important;
  color: #ffffff !important;
  font-weight: 700 !important;
  border-radius: 10px !important;
  padding: 10px 20px !important;
  box-shadow: 0 2px 8px rgba(29, 78, 216, 0.25) !important;
  transition: all 0.2s ease !important;
}

.primary-create-btn:hover {
  background: #1e40af !important;
  border-color: #1e40af !important;
  transform: translateY(-1px);
}

.ai-btn {
  border-radius: 10px !important;
}

/* ─────────── 现代高质感 SaaS 列表样式体系 (无硬边框，仅首行背景与微划线) ─────────── */
.saas-modern-table {
  border: none !important;
}

/* 仅第一行表头赋予浅蓝灰底色与细分隔线 */
.saas-modern-table :deep(.el-table__header-wrapper th) {
  background-color: #f1f5f9 !important;
  color: #475569 !important;
  font-weight: 700 !important;
  font-size: 13px !important;
  border-bottom: 1px solid #e2e8f0 !important;
  border-right: none !important;
  border-top: none !important;
  border-left: none !important;
  white-space: nowrap !important;
  letter-spacing: 0.3px;
}

.saas-modern-table :deep(.el-table__header-wrapper th .cell) {
  white-space: nowrap !important;
  word-break: keep-all !important;
}

.saas-modern-table :deep(.el-table__inner-wrapper::before) {
  display: none;
}

.saas-modern-table :deep(.el-table__border-left-patch) {
  display: none;
}

.saas-modern-table :deep(.el-table__row td) {
  border-right: none !important;
  border-left: none !important;
  border-bottom: 1px solid #f1f5f9 !important;
}

.saas-modern-table :deep(.el-table__row:hover td) {
  background-color: #f8fafc !important;
}

/* 复选框圆润化 */
.saas-modern-table :deep(.el-checkbox__inner) {
  border-radius: 4px !important;
  border-color: #cbd5e1 !important;
}

.col-id-text {
  font-size: 13px;
  color: #64748b;
  font-weight: 700;
  white-space: nowrap;
}

.exam-title-cell {
  display: flex;
  align-items: center;
}

.exam-main-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.5;
}

/* 极简无边框分类胶囊 */
.category-pill {
  display: inline-block;
  padding: 3px 12px;
  background: #f1f5f9;
  color: #475569;
  font-size: 12px;
  font-weight: 600;
  border-radius: 14px;
  white-space: nowrap;
}

/* 状态指示圆点胶囊 */
.status-dot-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  user-select: none;
  transition: all 0.15s ease;
}

.status-dot-pill.published {
  background: #eff6ff;
  color: #1d4ed8;
}

.status-dot-pill.published .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #2563eb;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
}

.status-dot-pill.draft {
  background: #f8fafc;
  color: #94a3b8;
}

.status-dot-pill.draft .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #cbd5e1;
}

.status-dot-pill:hover {
  filter: brightness(0.96);
  transform: scale(1.02);
}

/* 现代开关单元格 */
.status-switch-cell {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.exam-status-switch :deep(.el-switch__core) {
  border-radius: 20px !important;
  min-width: 68px !important;
  height: 26px !important;
  border: 1px solid #e2e8f0 !important;
}

.exam-status-switch.is-checked :deep(.el-switch__core) {
  background-color: #2563eb !important;
  border-color: #2563eb !important;
}

.exam-status-switch :deep(.el-switch__inner) {
  font-size: 12px !important;
  font-weight: 700 !important;
  padding: 0 8px !important;
}

/* 弱化文本与强调文本 */
.muted-gray-text {
  font-size: 13px;
  color: #64748b;
}

.timed-text {
  font-size: 13px;
  color: #1e293b;
  font-weight: 500;
}

.count-highlight {
  font-size: 13px;
  font-weight: 700;
  color: #0284c7;
}

.score-text {
  font-size: 13px;
  font-weight: 700;
  color: #1e293b;
}

/* 否/是 弱化灰白胶囊 */
.boolean-pill {
  display: inline-block;
  padding: 2px 10px;
  background: #f8fafc;
  color: #94a3b8;
  font-size: 12px;
  font-weight: 600;
  border-radius: 10px;
}

.boolean-pill.is-true {
  background: #fef3c7;
  color: #d97706;
}

/* 实体胶囊操作按钮与次级图标按钮 */
.action-btn-group {
  display: inline-flex;
  align-items: center;
  gap: 12px;
}

.action-pill-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.action-pill-btn.pill-primary {
  background: #2563eb;
  color: #ffffff;
  box-shadow: 0 2px 6px rgba(37, 99, 235, 0.2);
}

.action-pill-btn.pill-primary:hover {
  background: #1d4ed8;
  transform: translateY(-1px);
}

.action-pill-btn.pill-urgent {
  background: linear-gradient(135deg, #f97316, #ea580c);
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(249, 115, 22, 0.35);
}

.action-pill-btn.pill-urgent:hover {
  filter: brightness(1.06);
  transform: translateY(-1px);
}

.pill-icon {
  font-size: 13px;
}

.action-link-btn {
  color: #2563eb !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 4px !important;
  padding: 4px 6px !important;
}

.action-link-btn:hover {
  color: #1d4ed8 !important;
  background: #eff6ff !important;
  border-radius: 6px !important;
}

/* 极简精致底部分页栏 */
.pagination-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 12px;
}

.pagination-bar :deep(.el-pagination.is-background .el-pager li.is-active) {
  background-color: #1d4ed8 !important;
  color: #ffffff !important;
  border-radius: 6px !important;
  font-weight: 700 !important;
}

.pagination-bar :deep(.el-pagination.is-background .el-pager li) {
  border-radius: 6px !important;
  font-weight: 600 !important;
}

.pagination-bar :deep(.el-pagination .el-select .el-select__wrapper) {
  border-radius: 6px !important;
}

.score-calc-tip {
  margin-top: 6px;
  background: #f0f9ff;
  padding: 8px 14px;
  border-radius: 8px;
  border: 1px solid #bae6fd;
  color: #0369a1;
  font-size: 13px;
}

/* ─────────── 新建/编辑 试卷高定卡片仪表盘样式 (Settings Strip) ─────────── */
.exam-edit-dialog :deep(.el-dialog__body) {
  padding: 14px 22px 18px;
}

.edit-exam-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* 1. 顶部基础信息栅格 */
.exam-form-header-grid {
  display: grid;
  grid-template-columns: 1fr 220px 180px;
  gap: 14px;
  align-items: flex-start;
}

.header-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 12px;
  font-weight: 700;
  color: #475569;
}

.field-label.required::after {
  content: ' *';
  color: #ef4444;
}

/* 2. 考试核心规则卡片仪表盘 */
.settings-strip-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.strip-controls-grid {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.strip-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.strip-item-meta {
  display: flex;
  flex-direction: column;
}

.strip-item-title {
  font-size: 13px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.2;
}

.strip-item-desc {
  font-size: 11px;
  color: #94a3b8;
  line-height: 1.2;
}

.strip-item-ctrl {
  display: flex;
  align-items: center;
  gap: 8px;
}

.time-limit-box {
  display: flex;
  align-items: center;
  gap: 4px;
}

.time-limit-box .unit {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
}

/* 下层综合条（开放时间与及格联动） */
.strip-bottom-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 10px;
  border-top: 1px solid #e2e8f0;
  gap: 16px;
}

.strip-date-cell,
.strip-pass-cell {
  display: flex;
  align-items: center;
}

.bar-label {
  font-size: 12px;
  font-weight: 700;
  color: #475569;
  flex-shrink: 0;
}

.date-pickers-wrap {
  display: flex;
  align-items: center;
  gap: 6px;
}

.date-sep {
  font-size: 12px;
  color: #94a3b8;
}

.bar-sub-tip {
  font-size: 11px;
  color: #94a3b8;
  margin-left: 8px;
}

.window-warn {
  font-size: 11px;
  color: #ef4444;
  margin-left: 8px;
  font-weight: 600;
}

.pass-val-pill {
  font-size: 12px;
  font-weight: 800;
  color: #0284c7;
  background: #e0f2fe;
  padding: 2px 8px;
  border-radius: 12px;
  margin-right: 12px;
}

.pass-calc-tag {
  font-size: 12px;
  color: #475569;
  background: #ffffff;
  padding: 4px 10px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  white-space: nowrap;
}

.pass-calc-tag strong {
  font-weight: 800;
}

/* 3. 题目编排区 */
.exam-questions-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.questions-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
}

.section-badge {
  font-size: 11px;
  font-weight: 700;
  color: #0284c7;
  background: #e0f2fe;
  padding: 2px 8px;
  border-radius: 12px;
}

.section-tip {
  font-size: 12px;
  color: #94a3b8;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.selected-table {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.selected-table :deep(.el-table__header-wrapper th) {
  background-color: #f8fafc !important;
  color: #334155 !important;
  font-weight: 700 !important;
  font-size: 12px;
}

.table-q-title {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.5;
  margin-bottom: 4px;
}

.row-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
}

/* 4. 底部栏对齐 */
.dialog-footer-wrap {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.footer-summary {
  font-size: 13px;
  color: #475569;
}

.footer-summary strong {
  font-weight: 800;
}

.footer-btns {
  display: flex;
  gap: 10px;
}

/* 备选题库弹窗 */
.pool-modal-content {
  display: flex;
  flex-direction: column;
}

.pool-filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.stats-overview {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  flex: 1;
  background: #f8fafc;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  text-align: center;
}

.stat-num {
  display: block;
  font-size: 24px;
  font-weight: 800;
  color: #0f172a;
}

.stat-label {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

.q-detail-expand {
  padding: 12px 16px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.expand-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 13px;
}

.expand-label {
  font-weight: 700;
  color: #475569;
  width: 75px;
  flex-shrink: 0;
}

.opts-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.opt-chip {
  background: white;
  padding: 4px 10px;
  border-radius: 6px;
  border: 1px solid #cbd5e1;
  color: #334155;
}

.exp-content {
  color: #64748b;
  line-height: 1.5;
}
.manual-grade-btn {
  background: #f97316 !important;
  border-color: #f97316 !important;
  color: #ffffff !important;
  font-weight: 600 !important;
}
.manual-grade-btn:hover {
  background: #ea580c !important;
  border-color: #ea580c !important;
}

/* ─────────── 试卷综合详情（双 Tab）弹窗现代化样式 ─────────── */
.exam-detail-dialog :deep(.el-dialog__body) {
  padding: 12px 24px 24px;
}

.detail-nav-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background-color: #e2e8f0;
}

.detail-nav-tabs :deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 600;
  color: #64748b;
  padding: 0 20px;
}

.detail-nav-tabs :deep(.el-tabs__item.is-active) {
  color: #0284c7;
}

.tab-pane-container {
  min-height: 280px;
}

.detail-section-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px 18px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}

.section-title-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 14px;
}

.section-icon {
  font-size: 16px;
  color: #0284c7;
}

/* 基础信息网格 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  row-gap: 12px;
  column-gap: 20px;
}

.info-cell {
  display: flex;
  align-items: center;
  font-size: 13px;
}

.info-label {
  color: #64748b;
  flex-shrink: 0;
}

.info-val {
  color: #334155;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.info-val.strong {
  font-weight: 700;
  color: #0f172a;
}

/* 题目分析胶囊配比 */
.q-type-capsules {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 12px;
}

.q-capsule {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
}

.capsule-icon-wrap {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 17px;
  flex-shrink: 0;
}

.capsule-icon-wrap.single { background: #e0f2fe; color: #0284c7; }
.capsule-icon-wrap.multiple { background: #dcfce7; color: #16a34a; }
.capsule-icon-wrap.judge { background: #fef3c7; color: #d97706; }
.capsule-icon-wrap.fill { background: #ede9fe; color: #7c3aed; }
.capsule-icon-wrap.short { background: #fee2e2; color: #dc2626; }
.capsule-icon-wrap.total { background: #f1f5f9; color: #475569; }

.capsule-meta {
  display: flex;
  flex-direction: column;
}

.capsule-label {
  font-size: 11px;
  color: #64748b;
}

.capsule-count {
  font-size: 16px;
  font-weight: 800;
  color: #0f172a;
}

.capsule-count small {
  font-size: 11px;
  font-weight: normal;
  color: #94a3b8;
}

/* 题目全景流 */
.questions-stream {
  display: flex;
  flex-direction: column;
  gap: 14px;
  max-height: 480px;
  overflow-y: auto;
  padding-right: 4px;
}

.question-full-card {
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  border-radius: 10px;
  padding: 14px 16px;
  transition: all 0.2s ease;
}

.question-full-card:hover {
  border-color: #cbd5e1;
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.q-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.q-seq {
  font-size: 13px;
  font-weight: 800;
  color: #475569;
}

.q-type-tag {
  font-weight: 600;
}

.q-score {
  margin-left: auto;
  font-size: 13px;
  font-weight: 700;
  color: #0284c7;
}

.q-content {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
  line-height: 1.6;
  margin-bottom: 12px;
}

/* 选项网格与高保真高亮 */
.q-options-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 10px;
  margin-bottom: 8px;
}

.q-option-box {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 13px;
  color: #334155;
  transition: all 0.15s;
}

.opt-prefix {
  font-weight: 700;
  margin-right: 8px;
  color: #64748b;
}

.opt-text {
  flex: 1;
}

.q-option-box.is-correct {
  background: #f0fdf4;
  border-color: #86efac;
  color: #15803d;
  font-weight: 600;
}

.q-option-box.is-correct .opt-prefix {
  color: #16a34a;
}

.opt-check-icon {
  margin-left: 6px;
  color: #16a34a;
  font-size: 16px;
}

/* 填空/简答答案区 */
.q-answer-box {
  padding: 10px 12px;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  font-size: 13px;
  color: #166534;
}

.ans-label {
  font-weight: 700;
  margin-right: 6px;
}

/* ─────────── 考试数据：KPI 指标网格 ─────────── */
.stats-kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

.kpi-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
}

.kpi-icon-box {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}

.kpi-icon-box.users { background: #eff6ff; color: #2563eb; }
.kpi-icon-box.avg { background: #f0fdf4; color: #16a34a; }
.kpi-icon-box.max { background: #faf5ff; color: #9333ea; }
.kpi-icon-box.rate { background: #fffbeb; color: #d97706; }

.kpi-info {
  display: flex;
  flex-direction: column;
}

.kpi-label {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 2px;
}

.kpi-val {
  font-size: 22px;
  font-weight: 800;
  color: #0f172a;
}

.kpi-val small {
  font-size: 12px;
  font-weight: 600;
  color: #94a3b8;
}

/* 成绩分数段分布条 */
.score-dist-wrap {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.dist-bar-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dist-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #475569;
}

.tier-label {
  font-weight: 600;
}

.tier-count {
  color: #64748b;
}

.dist-progress-track {
  width: 100%;
  height: 8px;
  background: #f1f5f9;
  border-radius: 4px;
  overflow: hidden;
}

.dist-progress-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.4s ease;
}

/* 员工成绩明细表样式 */
.exam-stats-table {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.exam-stats-table :deep(.el-table__header-wrapper th) {
  background-color: #f1f5f9 !important;
  color: #1e293b !important;
  font-weight: 700 !important;
  font-size: 13px;
  border-bottom: 1px solid #cbd5e1 !important;
}

.member-name-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.member-real-name {
  font-weight: 700;
  color: #0f172a;
}

.member-sub-info {
  font-size: 12px;
  color: #94a3b8;
}

.record-score-tag {
  font-weight: 800;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 13px;
}

.record-score-tag.score-passed {
  color: #16a34a;
  background: #f0fdf4;
}

.record-score-tag.score-failed {
  color: #dc2626;
  background: #fef2f2;
}

.record-score-tag.score-pending {
  color: #d97706;
  background: #fffbeb;
  border: 1px solid #fde68a;
}

/* 待核验警示横幅 (Alert Banner) */
.pending-verify-alert {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fffbeb;
  border: 1px solid #fef08a;
  padding: 10px 14px;
  border-radius: 8px;
  margin-bottom: 14px;
  gap: 12px;
}

.alert-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.alert-badge {
  background: #f59e0b;
  color: white;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
}

.alert-text {
  font-size: 13px;
  color: #92400e;
  line-height: 1.4;
}

.alert-action-btn {
  font-weight: 600;
  flex-shrink: 0;
}

.section-title-tip {
  font-size: 12px;
  color: #f59e0b;
  font-weight: normal;
  margin-left: 8px;
}

/* 优雅空状态 */
.exam-empty-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 16px;
  text-align: center;
}

.empty-svg-art {
  width: 140px;
  height: 110px;
  margin-bottom: 14px;
}

.empty-title {
  margin: 0 0 6px;
  font-size: 16px;
  font-weight: 700;
  color: #334155;
}

.empty-desc {
  margin: 0;
  font-size: 13px;
  color: #94a3b8;
  max-width: 360px;
  line-height: 1.5;
}

/* ─────────── ✨ AI 智能组卷审阅清单现代精致卡片体系 ─────────── */
.ai-review-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 480px;
  overflow-y: auto;
  padding: 4px 6px 4px 2px;
}

.ai-review-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 14px 16px;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}

.ai-review-card:hover {
  border-color: #cbd5e1;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
}

.ai-review-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.ai-review-index {
  font-size: 13px;
  font-weight: 800;
  color: #0f172a;
}

.ai-review-score {
  font-size: 12px;
  font-weight: 700;
  color: #0284c7;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  padding: 1px 8px;
  border-radius: 10px;
  margin-left: auto;
}

.ai-review-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.6;
  margin-bottom: 8px;
}
</style>
