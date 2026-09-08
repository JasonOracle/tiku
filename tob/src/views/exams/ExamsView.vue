<!--
  * [变更日志]
  * 修改时间：2026-09-09
  * AI模型：Gemini 系列
  * 修改内容：[模块名称统一对齐「试卷管理」: 1. 弹窗标题更新为「编辑试卷」/「新建试卷」/「试卷详情 (只读模式)」; 2. 移除旧称「试卷与组卷」]
  * 修改时间：2026-09-09
  * AI模型：Gemini 系列
  * 修改内容：[统一组卷资料文案为「参考私有文库」: 明确说明与组卷需求不相关时系统将自动脱钩以通识出卷，避免张冠李戴]
  * 修改时间：2026-09-09
  * AI模型：Gemini 系列
  * 修改内容：[AI智能一键组卷弹窗新增私有教材/资料(RAG)选填多选下拉框: 1. 仅当存在已向量化解析成功的文档时展示(v-if="ragDocs.length"); 2. 组卷时优先检索命中切片并作为事实依据赋给大模型; 3. 新生成的题目自动携带切片溯源]
  * 修改时间：2026-09-09
  * AI模型：Gemini 系列
  * 修改内容：[优化试卷下架与删除闭环: 1. 试卷操作列对已归档/下架状态(archived)开放删除按钮与重新编辑上架能力; 2. 优化下架确认提示文案，说明零作答试卷下架后依然支持物理删除或重新上架]
  * 修改时间：2026-09-08
  * AI模型：Gemini 系列
  * 修改内容：[✨AI智能一键组卷优化: 1. 首屏两项核心输入改为「组卷需求」+「试卷分类」(分类必填且默认选中第一项); 2. 考试时间移至高级选项，未填写时系统自动默认当前时间起 7 天考试区间]
  * 修改时间：2026-09-07 00:05:00
  * AI模型：Gemini 系列
  * 修改内容：[1. AI 智能一键组卷弹窗 UI 对齐普通新建试卷: 增加题目难度单选框(默认简单)、限时作答开关+输入框、及格比例 Slider 滑块；2. 说明 AI 组卷及格线在题目生成后进入查看与确认页动态向上取整计算]
  * 修改时间：2026-09-07
  * AI模型：Muse Spark
  * 修改内容：[v1.2 Step3: 试卷标题列行内待办橙色微章 + GradingDrawer 行内批阅抽屉 (替代跳阅卷大厅)]
  * 修改时间：2026-09-07
  * AI模型：Muse Spark
  * 修改内容：[v1.2 Step4: 已选题目透亮选项与正确答案高亮(QuestionPreview) + grading_mode 三态单选(仅简答题展开)]
-->
<template>
  <div class="page-card">
    <div class="filter-bar">
      <div class="filters">
        <el-input v-model="filters.keyword" placeholder="搜索试卷名称..." clearable style="width: 220px" @change="loadExams" />
        <el-select v-model="filters.category_id" placeholder="全部试卷分类" clearable style="width: 160px" @change="loadExams">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
      </div>

      <div class="actions">
        <el-button type="warning" plain class="ai-btn" @click="aiExamVisible = true">
          ✨ AI 智能一键组卷
        </el-button>
        <el-button type="primary" class="primary-btn" @click="openCreateDialog">
          <el-icon><Plus /></el-icon> 新建试卷
        </el-button>
      </div>
    </div>

    <!-- 试卷列表表格 -->
    <el-table :data="exams" v-loading="loading" stripe style="width: 100%; margin-top: 16px">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="title" label="试卷名称" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          <div class="exam-title-cell">
            <span>{{ row.title }}</span>
            <el-tag
              v-if="row.pending_count > 0"
              type="warning"
              effect="dark"
              class="cursor-pointer pending-badge"
              @click="handleOpenGrading(row)"
            >
              {{ row.pending_count }} 份待批阅
            </el-tag>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="category_id" label="试卷分类" width="140">
        <template #default="{ row }">
          <el-tag type="info" effect="plain">{{ row.category_name || getCategoryName(row.category_id) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="上架状态" width="130">
        <template #default="{ row }">
          <el-switch
            :model-value="row.status === 'published'"
            active-text="已上架"
            :inactive-text="row.status === 'archived' ? '已下架' : '待上架'"
            inline-prompt
            @change="(val: boolean) => handleStatusChange(row, val)"
          />
        </template>
      </el-table-column>
      <el-table-column label="考试时间窗" width="110">
        <template #default="{ row }">
          <el-tag v-if="row.window_status === 'upcoming'" type="info" size="small">未开始</el-tag>
          <el-tag v-else-if="row.window_status === 'ongoing'" type="success" size="small">进行中</el-tag>
          <el-tag v-else-if="row.window_status === 'ended'" type="danger" size="small">已结束</el-tag>
          <el-tag v-else type="info" size="small" effect="plain">长期开放</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="creator_name" label="创建老师" width="110">
        <template #default="{ row }">
          <span style="font-size: 13px; color: #475569">{{ row.creator_name || '—' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="question_count" label="题目数" width="85">
        <template #default="{ row }">
          <span style="font-weight: 700; color: #0284c7">{{ row.question_count || 0 }} 题</span>
        </template>
      </el-table-column>
      <el-table-column prop="total_score" label="总分" width="80">
        <template #default="{ row }">
          <span style="font-weight: 700">{{ row.total_score || 0 }} 分</span>
        </template>
      </el-table-column>
      <el-table-column prop="is_random" label="随机排列" width="90">
        <template #default="{ row }">
          <el-tag :type="row.is_random ? 'warning' : 'info'" size="small">
            {{ row.is_random ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="300" fixed="right">
        <template #default="{ row }">
          <el-button v-if="row.pending_count > 0" type="warning" text size="small" @click="handleOpenGrading(row)">
            行内批阅
          </el-button>
          <el-button v-if="row.pending_count > 0" type="primary" text size="small" @click="openGradingHall(row)">
            阅卷大厅
          </el-button>
          <el-button v-if="row.status !== 'draft'" type="success" text size="small" @click="openStatsDialog(row)">
            <el-icon><DataAnalysis /></el-icon> 考情
          </el-button>
          <el-button v-if="row.status !== 'draft'" type="info" text size="small" @click="openViewDialog(row)">
            <el-icon><View /></el-icon> 查看详情
          </el-button>
          <el-button v-if="row.status === 'draft'" type="primary" text size="small" @click="openEditDialog(row)">编辑/组卷</el-button>
          <el-button v-if="row.status !== 'published'" type="danger" text size="small" @click="handleDelete(row.id)">删除</el-button>
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

    <!-- 考情看板 Dialog -->
    <el-dialog v-model="statsDialogVisible" title="已上架试卷考情分析数据" width="700px">
      <div v-loading="statsLoading">
        <div class="stats-overview" v-if="statsData">
          <div class="stat-card">
            <span class="stat-num">{{ statsData.total_participants }}</span>
            <span class="stat-label">累计参与作答人数</span>
          </div>
          <div class="stat-card">
            <span class="stat-num" style="color: #0284c7">{{ statsData.avg_score }}</span>
            <span class="stat-label">全站平均得分</span>
          </div>
          <div class="stat-card">
            <span class="stat-num" style="color: #16a34a">{{ statsData.pass_rate }}%</span>
            <span class="stat-label">综合及格通过率</span>
          </div>
        </div>

        <el-divider content-position="left"><strong>用户答卷历史明细</strong></el-divider>

        <el-table :data="statsData?.user_records || []" size="small" stripe style="width: 100%" max-height="300">
          <el-table-column label="作答用户" width="150">
            <template #default="{ row }">
              <span style="font-weight: 700">{{ row.nickname || row.username }}</span>
              <span v-if="row.nickname" style="font-size: 12px; color: #94a3b8"> ({{ row.username }})</span>
            </template>
          </el-table-column>
          <el-table-column prop="score" label="得 分" width="90">
            <template #default="{ row }">
              <span style="font-weight: 700">{{ row.score }} 分</span>
            </template>
          </el-table-column>
          <el-table-column prop="is_passed" label="判定" width="90">
            <template #default="{ row }">
              <el-tag :type="row.is_passed ? 'success' : 'danger'" size="small">
                {{ row.is_passed ? '及格' : '未及格' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="time_spent" label="耗时" width="90">
            <template #default="{ row }">
              {{ Math.floor(row.time_spent / 60) }}分{{ row.time_spent % 60 }}秒
            </template>
          </el-table-column>
          <el-table-column prop="submit_time" label="提交时间" min-width="160" />
        </el-table>
      </div>
    </el-dialog>

    <!-- 查看详情（只读模态框） Dialog -->
    <el-dialog v-model="viewDialogVisible" title="试卷详情 (只读模式)" width="850px" top="40px">
      <el-form :model="viewData" label-width="100px" disabled>
        <el-row :gutter="16">
          <el-col :span="14">
            <el-form-item label="试卷名称">
              <el-input :model-value="viewData?.title" />
            </el-form-item>
          </el-col>
          <el-col :span="10">
            <el-form-item label="试卷分类">
              <el-input :model-value="getCategoryName(viewData?.category_id)" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="限时作答">
              <el-tag :type="viewData?.is_timed ? 'success' : 'info'">
                {{ viewData?.is_timed ? `${viewData?.time_limit} 分钟` : '不限时' }}
              </el-tag>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="随机排列">
              <el-tag :type="viewData?.is_random ? 'warning' : 'info'">
                {{ viewData?.is_random ? '随机题目顺序' : '固定顺序' }}
              </el-tag>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="首页推荐">
              <el-tag :type="viewData?.is_recommended ? 'danger' : 'info'">
                {{ viewData?.is_recommended ? '已推荐' : '普通' }}
              </el-tag>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="试卷封面">
          <CoverArt :cover="viewData?.cover_url || 'preset:1'" width="140px" height="84px" />
        </el-form-item>
        <el-form-item label="试卷得分线">
          <div style="font-size: 14px; font-weight: 600; color: #0f172a">
            总分：{{ viewData?.total_score }} 分 | 及格分：{{ viewData?.pass_score }} 分 ({{ viewData?.pass_percent }}%)
          </div>
        </el-form-item>
        <el-divider content-position="left"><strong>包含了 {{ viewQuestions.length }} 道题目 (点击展开查看选项、答案与解析)</strong></el-divider>
        <el-table :data="viewQuestions" size="small" stripe style="width: 100%" max-height="380">
          <el-table-column type="expand">
            <template #default="{ row }">
              <div class="q-detail-expand">
                <div class="expand-item" v-if="row.options && row.options.length">
                  <span class="expand-label">选项配置：</span>
                  <div class="opts-list">
                    <span v-for="opt in row.options" :key="opt.key" class="opt-chip">
                      <strong>{{ opt.key }}.</strong> {{ opt.text }}
                    </span>
                  </div>
                </div>
                <div class="expand-item">
                  <span class="expand-label">正确答案：</span>
                  <el-tag type="success" size="small" effect="dark">
                    {{ Array.isArray(row.answer) ? row.answer.join(', ') : row.answer }}
                  </el-tag>
                </div>
                <div class="expand-item" v-if="row.explanation">
                  <span class="expand-label">题目解析：</span>
                  <span class="exp-content">{{ row.explanation }}</span>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column type="index" label="序号" width="60" align="center" />
          <el-table-column prop="type" label="题型" width="90">
            <template #default="{ row }">
              <el-tag size="small" :type="getTypeTag(row.type)">{{ getTypeLabel(row.type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="title" label="题干描述" show-overflow-tooltip />
          <el-table-column prop="score" label="分值" width="90">
            <template #default="{ row }">
              <span style="font-weight: 700; color: #0284c7">{{ row.score || 10 }} 分</span>
            </template>
          </el-table-column>
        </el-table>
      </el-form>
      <template #footer>
        <el-button type="primary" @click="viewDialogVisible = false">确认关闭</el-button>
      </template>
    </el-dialog>

    <!-- 新建/编辑 试卷 Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="880px" top="30px" destroy-on-close>
      <el-form :model="form" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="14">
            <el-form-item label="试卷名称" required>
              <el-input v-model="form.title" placeholder="请输入试卷名称" />
            </el-form-item>
          </el-col>
          <el-col :span="10">
            <el-form-item label="试卷分类" required>
              <el-select v-model="form.category_id" placeholder="选择试卷分类" style="width: 100%">
                <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="限时作答">
              <el-switch v-model="form.is_timed" />
              <el-input-number v-if="form.is_timed" v-model="form.time_limit" :min="1" :max="600" style="width: 100px; margin-left: 8px" />
              <span v-if="form.is_timed" style="margin-left: 4px; color: #64748b">分</span>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="随机排列">
              <el-switch v-model="form.is_random" active-text="C端答题随机打乱题序" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="首页推荐">
              <el-switch v-model="form.is_recommended" active-text="推荐至首页Hero" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="24">
            <el-form-item label="考试时间窗">
              <div style="display: flex; align-items: center; gap: 10px; width: 100%">
                <el-date-picker v-model="form.start_time" type="datetime" placeholder="开始时间(可选)" format="YYYY-MM-DD HH:mm"
                                value-format="YYYY-MM-DDTHH:mm:ss" style="flex: 1" />
                <span style="color: #94a3b8">至</span>
                <el-date-picker v-model="form.end_time" type="datetime" placeholder="结束时间(可选)" format="YYYY-MM-DD HH:mm"
                                value-format="YYYY-MM-DDTHH:mm:ss" style="flex: 1" />
              </div>
              <div class="score-calc-tip" style="margin-top: 6px">
                <template v-if="form.start_time && form.end_time">
                  开放区间 {{ windowMinutes }} 分钟
                  <template v-if="form.is_timed"> | 限时 {{ form.time_limit }} 分钟
                    <strong v-if="timeWindowError" style="color: #dc2626">⚠ {{ timeWindowError }}</strong>
                    <strong v-else style="color: #16a34a">✓ 校验通过</strong>
                  </template>
                  | 结束后系统强制收卷，解析在结束前锁定(防泄题)
                </template>
                <template v-else>不设置则长期开放（可选）；设置后 C 端按「未开始/进行中/已结束」流转</template>
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row v-if="hasShortQuestion" :gutter="16">
          <el-col :span="24">
            <el-form-item label="AI 阅卷模式">
              <el-radio-group v-model="form.grading_mode">
                <el-radio label="manual">人工全权批阅</el-radio>
                <el-radio label="ai_pre">AI 辅助预审</el-radio>
                <el-radio label="ai_auto">AI 自动托管</el-radio>
              </el-radio-group>
              <div class="score-calc-tip" style="margin-top: 6px">
                检测到<strong>简答题</strong>才显示此选项：人工全权不消耗 AI 额度，交卷后等待老师批改；
                AI 辅助预审由 AI 生成初评建议分，需老师确认发布；AI 自动托管批完直接发布成绩。
                全客观题试卷隐藏此选项（纯代码秒出分）。
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="24">
            <el-form-item label="试卷封面">
              <div class="cover-picker">
                <div
                  v-for="p in COVER_PRESETS"
                  :key="p"
                  class="cover-opt"
                  :class="{ selected: form.cover_url === p }"
                  @click="form.cover_url = p"
                >
                  <CoverArt :cover="p" width="120px" height="72px" />
                </div>
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="24">
            <el-form-item label="及格比例">
              <div style="display: flex; align-items: center; width: 100%; gap: 16px">
                <el-slider v-model="form.pass_percent" :min="10" :max="100" :step="5" style="flex: 1" />
                <span style="font-weight: 700; width: 50px; color: #0284c7">{{ form.pass_percent }}%</span>
              </div>
              <div class="score-calc-tip">
                动态计算试卷总分：<strong style="color: #0284c7; font-size: 15px">{{ computedTotalScore }}</strong> 分 ➔ 
                及格线：<strong style="color: #16a34a; font-size: 15px">{{ computedPassScore }}</strong> 分 
                <span style="color: #94a3b8; font-size: 12px">({{ computedTotalScore }}分 × {{ form.pass_percent }}%，向上取整)</span>
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left"><strong>试卷已加入题目（支持拖拽上下排序与多选批量删除）</strong></el-divider>

        <div class="selected-box">
          <div class="box-header">
            <span>已加入题目 (共 <strong style="color: #0284c7">{{ selectedQuestions.length }}</strong> 题)</span>
            <div style="display: flex; gap: 10px; align-items: center">
              <el-button
                v-if="batchRemoveSelectedIds.length > 0"
                type="danger"
                plain
                size="small"
                @click="batchRemoveSelectedQuestions"
              >
                批量移除所选 ({{ batchRemoveSelectedIds.length }})
              </el-button>
              <el-button type="primary" size="small" @click="openPoolModal">
                <el-icon><Plus /></el-icon> 导入 / 添加题目
              </el-button>
            </div>
          </div>

          <el-table
            :data="selectedQuestions"
            size="small"
            border
            style="width: 100%; margin-top: 8px"
            max-height="300"
            @selection-change="handleSelectedSelectionChange"
          >
            <el-table-column type="selection" width="45" align="center" />
            <el-table-column label="排序" width="85" align="center">
              <template #default="{ $index }">
                <div class="sort-actions">
                  <el-button :disabled="$index === 0" text circle size="small" @click="moveQuestion($index, -1)">▲</el-button>
                  <el-button :disabled="$index === selectedQuestions.length - 1" text circle size="small" @click="moveQuestion($index, 1)">▼</el-button>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="type" label="题型" width="80">
              <template #default="{ row }">
                <el-tag size="small" :type="getTypeTag(row.type)">{{ getTypeLabel(row.type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="title" label="题干描述" min-width="260">
              <template #default="{ row }">
                <div class="selected-title">{{ row.title }}</div>
                <QuestionPreview :question="row" />
              </template>
            </el-table-column>
            <el-table-column prop="score" label="分值" width="80">
              <template #default="{ row }">
                <span style="font-weight: 700; color: #0284c7">{{ row.score || 10 }} 分</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="70" align="center">
              <template #default="{ $index }">
                <el-button type="danger" text circle size="small" @click="removeSelectedQuestion($index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveExam">保存试卷</el-button>
      </template>
    </el-dialog>

    <!-- 题库备选选择区 独立弹窗 Dialog -->
    <el-dialog v-model="poolModalVisible" title="选择备选题库加入当前试卷" width="800px" destroy-on-close>
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
              <el-tag v-if="isQuestionSelected(row.id)" type="info" size="small">已在试卷中</el-tag>
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
    <!-- ✨ AI 智能一键组卷 Dialog (v1.2 Step4: 极简两项必填 + 生成后原地审阅) -->
    <el-dialog v-model="aiExamVisible" :title="aiReviewVisible ? '✨ AI 组卷结果审阅' : '✨ AI 智能一键组卷'" width="700px" destroy-on-close @open="handleOpenAiExam">
      <!-- 生成后所见即所得审阅清单 -->
      <div v-if="aiReviewVisible">
        <el-alert type="success" :closable="false" show-icon style="margin-bottom: 14px"
                  :title="aiExamResult || 'AI 组卷完成，请核对题目后确认保存'" />
        <div class="ai-review-list">
          <div v-for="(q, idx) in aiReviewQuestions" :key="q.id || idx" class="ai-review-card">
            <div class="ai-review-head">
              <span class="ai-review-index">第 {{ idx + 1 }} 题</span>
              <el-tag size="small" :type="getTypeTag(q.type)">{{ getTypeLabel(q.type) }}</el-tag>
              <span class="ai-review-score">{{ q.score || 10 }} 分</span>
            </div>
            <div class="ai-review-title">{{ q.title }}</div>
            <QuestionPreview :question="q" />
          </div>
        </div>
      </div>

      <!-- 组卷表单：核心两项（组卷需求 + 试卷分类）必填，其余按需折叠 -->
      <el-form v-else label-width="100px">
        <el-form-item label="组卷需求" required>
          <el-input v-model="aiExamForm.description" type="textarea" :rows="3"
                    placeholder="例如：帮我组一份消防安全测试卷，包含3道单选、2道判断、1道简答，难度中等" />
        </el-form-item>
        <el-form-item label="试卷分类" required>
          <el-select v-model="aiExamForm.category_id" placeholder="请选择试卷分类" style="width: 100%">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
          <div class="score-calc-tip" style="margin-top: 4px; color: #64748b; font-size: 12px">
            必填：明确试卷归属分类，方便在试卷列表与学员端按题库维度归类展示
          </div>
        </el-form-item>

        <!-- 私有文库（RAG，选填多选）：仅当存在已解析完成的文档时呈现 -->
        <el-form-item v-if="ragDocs.length" label="参考私有文库">
          <el-select v-model="aiExamForm.doc_ids" multiple collapse-tags collapse-tags-tooltip clearable
                     placeholder="选填可多选：勾选后优先依据所选私有文库组卷，题目将自动附带切片溯源" style="width: 100%">
            <el-option v-for="d in ragDocs" :key="d.id" :label="`${d.filename}（${d.total_chunks}块切片）`" :value="d.id" />
          </el-select>
          <div class="score-calc-tip" style="margin-top: 4px; color: #64748b; font-size: 12px">
            已检测到您的私有文库资料；若所选文档与组卷需求不相关，系统将自动脱钩并以通识出卷，避免张冠李戴
          </div>
        </el-form-item>

        <el-collapse>
          <el-collapse-item title="高级选项（考试时间 / 试卷标题 / 难度 / 限时 / 及格线，已设最优默认）" name="advanced">
            <el-form-item label="考试时间">
              <div style="display: flex; align-items: center; gap: 10px; width: 100%">
                <el-date-picker v-model="aiExamForm.start_time" type="datetime" placeholder="默认当前时间" format="YYYY-MM-DD HH:mm"
                                value-format="YYYY-MM-DDTHH:mm:ss" :disabled-date="disablePastDate" style="flex: 1" />
                <span style="color: #94a3b8">至</span>
                <el-date-picker v-model="aiExamForm.end_time" type="datetime" placeholder="默认 7 天后" format="YYYY-MM-DD HH:mm"
                                value-format="YYYY-MM-DDTHH:mm:ss" :disabled-date="disableBeforeStart" style="flex: 1" />
              </div>
              <div class="score-calc-tip" style="margin-top: 4px; color: #64748b; font-size: 12px">
                选填：不填写时系统将自动默认设置为当前时间起 7 天开放区间（如需指定考试开放窗口可在此设置）
              </div>
            </el-form-item>
            <el-form-item label="试卷标题">
              <el-input v-model="aiExamForm.title" placeholder="留空则由 AI 命名" />
            </el-form-item>
            <el-form-item label="题目难度">
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
                💡 及格分数将在 AI 生成题目并进入修改界面选定最终试题及分值后自动向上取整计算
              </div>
            </el-form-item>
          </el-collapse-item>
        </el-collapse>
      </el-form>
      <template #footer>
        <template v-if="aiReviewVisible">
          <el-button @click="aiReviewVisible = false">返回修改</el-button>
          <el-button type="primary" @click="confirmAiExam">确认保存试卷</el-button>
        </template>
        <template v-else>
          <el-button @click="aiExamVisible = false">关闭</el-button>
          <el-button type="warning" :loading="aiExamLoading" @click="generateAiExam">
            {{ aiExamLoading ? 'AI 组卷中...' : '开始 AI 组卷' }}
          </el-button>
        </template>
      </template>
    </el-dialog>

    <!-- v1.2 Step3: 主观题批阅抽屉 (行内待办原地批阅) -->
    <GradingDrawer
      :visible="gradingVisible"
      :exam-id="gradingExam?.id ?? null"
      :exam-title="gradingExam?.title ?? ''"
      @update:visible="gradingVisible = $event"
      @graded="handleGraded"
    />

    <!-- v1.7: 行级阅卷大厅全屏弹窗 -->
    <ExamGradingDialog
      :visible="gradingHallVisible"
      :exam-id="gradingHallExam?.id ?? null"
      :exam-title="gradingHallExam?.title ?? ''"
      @update:visible="gradingHallVisible = $event"
      @graded="handleGraded"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Delete, DataAnalysis, View } from '@element-plus/icons-vue';
import request from '../../utils/request';
import CoverArt from '../../components/CoverArt.vue';
import GradingDrawer from './components/GradingDrawer.vue';
import ExamGradingDialog from './components/ExamGradingDialog.vue';
import QuestionPreview from './components/QuestionPreview.vue';
import { COVER_PRESETS } from '../../assets/covers/index';

const loading = ref(false);

const exams = ref<any[]>([]);
const categories = ref<any[]>([]);
const filters = reactive({ keyword: '', category_id: null });
const pagination = reactive({ page: 1, size: 10, total: 0 });

const dialogVisible = ref(false);
const editingId = ref<number | null>(null);
const dialogTitle = computed(() => (editingId.value ? '编辑试卷' : '新建试卷'));
const saving = ref(false);

const statsDialogVisible = ref(false);
const statsLoading = ref(false);
const statsData = ref<any>(null);

// 只读弹窗
const viewDialogVisible = ref(false);
const viewData = ref<any>(null);
const viewQuestions = ref<any[]>([]);

// 表单对象
const form = reactive({
  title: '',
  category_id: null as number | null,
  cover_url: 'preset:1',
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
    return `考试限时不能大于开放区间 ${windowMinutes.value} 分钟`;
  }
  return '';
});

const hasShortQuestion = computed(() =>
  selectedQuestions.value.some((q) => q.type === 'short')
);

const selectedQuestions = ref<any[]>([]);
const batchRemoveSelectedIds = ref<number[]>([]);

// 题库选择 Dialog 独立弹窗
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
      params: { target_type: 'exam' }
    });
    categories.value = res || [];
  } catch (e) {
    categories.value = [];
  }
};

const getCategoryName = (catId: number | null) => {
  if (!catId) return '未分类';
  const c = categories.value.find((item) => item.id === catId);
  return c ? c.name : `试卷分类#${catId}`;
};

const loadExams = async () => {
  loading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/exams', {
      params: { ...filters, page: pagination.page, size: pagination.size }
    });
    exams.value = res.items || [];
    pagination.total = res.total || 0;
  } finally {
    loading.value = false;
  }
};

const handleStatusChange = (row: any, val: boolean) => {
  const newStatus = val ? 'published' : 'archived';
  if (!val) {
    ElMessageBox.confirm('下架后试卷将停止对学员开放（无学员作答时可重新编辑、上架或彻底删除；已有作答成绩则保留归档）。确定要下架吗？', '下架确认', {
      type: 'warning',
      confirmButtonText: '确认下架',
      cancelButtonText: '取消'
    }).then(async () => {
      await request.put(`/api/v1/admin/exams/${row.id}/status?status=${newStatus}`);
      ElMessage.success('试卷已成功下架');
      loadExams();
    });
  } else {
    request.put(`/api/v1/admin/exams/${row.id}/status?status=${newStatus}`).then(() => {
      ElMessage.success('试卷已成功上线发布');
      loadExams();
    });
  }
};

const openStatsDialog = async (row: any) => {
  statsDialogVisible.value = true;
  statsLoading.value = true;
  try {
    const res: any = await request.get(`/api/v1/admin/exams/${row.id}/stats`);
    statsData.value = res;
  } finally {
    statsLoading.value = false;
  }
};

const openViewDialog = async (row: any) => {
  viewData.value = row;
  viewDialogVisible.value = true;
  try {
    const detail: any = await request.get(`/api/v1/admin/exams/${row.id}`);
    viewQuestions.value = detail.questions || [];
  } catch (e) {
    viewQuestions.value = [];
  }
};

const openPoolModal = () => {
  poolModalVisible.value = true;
  pendingPoolSelection.value = [];
  loadQuestionPool();
};

const loadQuestionPool = async () => {
  poolLoading.value = true;
  try {
    const res: any = await request.get('/api/v1/admin/questions', {
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
  ElMessage.success(`成功加入 ${count} 道题目`);
  poolModalVisible.value = false;
};

const handleSelectedSelectionChange = (val: any[]) => {
  batchRemoveSelectedIds.value = val.map((q) => q.id);
};

const batchRemoveSelectedQuestions = () => {
  if (batchRemoveSelectedIds.value.length === 0) return;
  selectedQuestions.value = selectedQuestions.value.filter((q) => !batchRemoveSelectedIds.value.includes(q.id));
  batchRemoveSelectedIds.value = [];
  ElMessage.success('已从当前组卷中移除选中题目');
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
  if (type === 'single') return 'primary';
  if (type === 'multiple') return 'warning';
  if (type === 'fill') return 'success';
  if (type === 'short') return 'danger';
  return 'info';
};

const getTypeLabel = (type: string) => {
  if (type === 'single') return '单选题';
  if (type === 'multiple') return '多选题';
  if (type === 'fill') return '填空题';
  if (type === 'short') return '简答题';
  return '判断题';
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
  form.cover_url = 'preset:1';
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
    ElMessage.warning('已上架试卷已锁定组卷编辑，请先下架后再进行修改');
    return;
  }
  if (row.status === 'archived') {
    ElMessage.warning('该试卷已归档冻结，不可编辑');
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
  form.cover_url = row.cover_url || 'preset:1';
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
    const detail: any = await request.get(`/api/v1/admin/exams/${row.id}`);
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
  // v1.2 Step4: 简答题智能展开 grading_mode；全客观题固定 manual（纯代码秒出分，不耗 AI 额度）
  const resolvedMode = hasShortQuestion.value ? form.grading_mode : 'manual';
  const payload = {
    title: form.title,
    category_id: form.category_id,
    cover_url: form.cover_url,
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
    question_ids: selectedQuestions.value.map((q) => q.id)
  };

  try {
    if (editingId.value) {
      await request.put(`/api/v1/admin/exams/${editingId.value}`, payload);
      ElMessage.success('试卷及组卷已成功修改');
    } else {
      await request.post('/api/v1/admin/exams', payload);
      ElMessage.success('试卷及组卷已成功创建');
    }
    dialogVisible.value = false;
    loadExams();
  } finally {
    saving.value = false;
  }
};

const handleDelete = (id: number) => {
  ElMessageBox.confirm('确定要删除该试卷吗？未上架或已下架且无学员作答的试卷可彻底删除，删除后不可恢复。', '提示', { type: 'warning' }).then(async () => {
    await request.delete(`/api/v1/admin/exams/${id}`);
    ElMessage.success('试卷删除成功');
    loadExams();
  });
};

// ---- v1.2 Step3: 行内待办 → 批阅抽屉 ----
const gradingVisible = ref(false);
const gradingExam = ref<any>(null);

const handleOpenGrading = (row: any) => {
  gradingExam.value = row;
  gradingVisible.value = true;
};

const handleGraded = () => {
  loadExams();
};

// ---- v1.7: 行级阅卷大厅全屏弹窗 ----
const gradingHallVisible = ref(false);
const gradingHallExam = ref<any>(null);

const openGradingHall = (row: any) => {
  gradingHallExam.value = row;
  gradingHallVisible.value = true;
};

// ---- v1.2 Step4: ✨ AI 智能一键组卷 (极简两项 + 审阅确认) ----
const aiExamVisible = ref(false);
const aiExamLoading = ref(false);
const aiExamResult = ref('');
const aiReviewVisible = ref(false);
const aiReviewQuestions = ref<any[]>([]);
const ragDocs = ref<any[]>([]);

const loadRagDocs = async () => {
  try {
    const res: any = await request.get('/api/v1/admin/rag/documents');
    ragDocs.value = (res.items || []).filter((d: any) => d.status === 'done');
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

// 打开 AI 组卷弹窗时自动回显默认分类（若未选择）并拉取私有文库可用文档
const handleOpenAiExam = () => {
  aiReviewVisible.value = false;
  aiReviewQuestions.value = [];
  aiExamResult.value = '';
  aiExamForm.doc_ids = [];
  loadRagDocs();
  if (!aiExamForm.category_id && categories.value.length > 0) {
    aiExamForm.category_id = categories.value[0].id;
  }
};

const generateAiExam = async () => {
  if (!aiExamForm.description.trim()) {
    ElMessage.error('请描述组卷需求');
    return;
  }
  if (!aiExamForm.category_id) {
    ElMessage.error('请选择试卷分类');
    return;
  }

  // 考试时间选填校验：若填写了开始时间或结束时间，则校验时间先后顺序与区间合法性
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
      ElMessage.error(`考试限时不能大于开放区间 ${aiWindowMinutes.value} 分钟`);
      return;
    }
  }

  aiExamLoading.value = true;
  aiReviewVisible.value = false;
  aiReviewQuestions.value = [];
  try {
    const res: any = await request.post('/api/v1/admin/ai/exams/generate', {
      title: aiExamForm.title || undefined,
      description: aiExamForm.description,
      specs: parseSpecs(aiExamForm.description),
      difficulty: aiExamForm.difficulty,
      category_id: aiExamForm.category_id,
      doc_ids: aiExamForm.doc_ids.length ? aiExamForm.doc_ids : undefined,
      is_timed: aiExamForm.is_timed,
      time_limit: aiExamForm.is_timed ? aiExamForm.time_limit : 0,
      start_time: aiExamForm.start_time || undefined,
      end_time: aiExamForm.end_time || undefined,
      pass_percent: aiExamForm.pass_percent
    }, { timeout: 180000 }); // 真实大模型组卷较慢, 覆盖全局 10s 超时
    aiExamId = res.exam_id;
    aiExamResult.value = res.message || `已生成草稿，共 ${res.question_count} 题（AI 新生成 ${res.new_questions} 题）`;
    // 大模型实时全量原创生成题目，弹窗原地切换为审阅卡片（选项与正确答案绿色高亮）
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
  ElMessage.success('试卷已保存为草稿，请检查无误后手动上架');
  aiExamVisible.value = false;
  aiReviewVisible.value = false;
  aiExamResult.value = '';
  aiExamId = null;
  loadExams();
};

// 从自然语言需求中粗提取题型构成 ("3道单选、2道判断、1道简答" 或 "生成6道题目")
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
    // 匹配如 "6道题目", "生成6题", "共6道" 等泛指数量
    const totalMatch = text.match(/(\d+)\s*(?:道|个|条)?(?:题|题目|试题)/);
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
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.exam-title-cell {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
}

.pending-badge {
  cursor: pointer;
}

.selected-title {
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 2px;
}

.ai-review-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 480px;
  overflow-y: auto;
}

.ai-review-card {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 12px 14px;
  background: #f8fafc;
}

.ai-review-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.ai-review-index {
  font-weight: 800;
  color: #0f172a;
}

.ai-review-score {
  margin-left: auto;
  font-weight: 700;
  color: #0284c7;
  font-size: 13px;
}

.ai-review-title {
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 4px;
}

.cursor-pointer {
  cursor: pointer;
}

.filters {
  display: flex;
  gap: 12px;
}

.primary-btn {
  background: linear-gradient(135deg, #0284c7, #0369a1);
  border: none;
}

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
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

.selected-box {
  background: #f8fafc;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.box-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  font-weight: 600;
}

.pool-box {
  margin-top: 16px;
  background: #fff;
  padding: 12px;
  border-radius: 12px;
  border: 1px dashed #cbd5e1;
}

.cover-picker {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.cover-opt {
  cursor: pointer;
  border: 2px solid transparent;
  border-radius: 10px;
  padding: 2px;
  position: relative;
}

.cover-opt.selected {
  border-color: #0284c7;
  box-shadow: 0 2px 10px rgba(2, 132, 199, 0.3);
}

.custom-tag {
  position: absolute;
  bottom: 6px;
  left: 6px;
  background: rgba(2, 132, 199, 0.85);
  color: white;
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 6px;
}

.pool-filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pool-filters {
  display: flex;
  gap: 12px;
  align-items: center;
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
</style>
