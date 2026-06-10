<template>
  <div class="home">
    <!-- Hero 区域 -->
    <div class="hero">
      <h1>📚 数据结构智能刷题</h1>
      <p>AI 驱动的交互式学习系统，助你轻松掌握核心算法</p>
    </div>

    <!-- 筛选区域 -->
    <div class="filter-bar">
      <span class="filter-label">筛选知识点：</span>
      <el-select v-model="selectedTopic" placeholder="全部" @change="onTopicChange">
        <el-option label="全部" value="all" />
        <el-option
          v-for="topic in topics"
          :key="topic"
          :label="topic"
          :value="topic"
        />
      </el-select>
      <span class="question-count">（共 {{ filteredQuestions.length }} 题）</span>
    </div>

    <div v-if="currentQuestion">
      <!-- 题目序号 -->
      <div class="question-index">
        第 {{ currentIndex + 1 }} / {{ filteredQuestions.length }} 题
      </div>

      <el-card class="question-card">
        <h2>{{ currentQuestion.title }}</h2>
        <el-radio-group v-model="selectedAnswer">
          <el-radio
            v-for="opt in currentQuestion.options"
            :key="opt"
            :label="opt.charAt(0)"
          >{{ opt }}</el-radio>
        </el-radio-group>
        <el-button
          type="primary"
          @click="submitAnswer"
          style="margin-top: 20px"
        >提交答案</el-button>
      </el-card>

      <!-- 题号快速跳转 -->
      <div class="question-nav">
        <el-button
          v-for="(q, idx) in filteredQuestions"
          :key="q.id"
          :type="idx === currentIndex ? 'primary' : ''"
          size="small"
          circle
          @click="goToQuestion(idx)"
        >{{ idx + 1 }}</el-button>
      </div>

      <!-- 结果区域 -->
      <div v-if="showResult" class="result-box">
        <el-alert
          :title="resultText"
          :type="isCorrect ? 'success' : 'error'"
          :closable="false"
        />
        <el-card class="analysis-card">
          <h3>解析</h3>
          <p>{{ analysis }}</p>
        </el-card>

        <!-- AI 讲解区域 -->
        <el-button
          type="warning"
          @click="getAIExplain"
          :loading="aiLoading"
          style="margin-top: 15px"
        >
          让AI详细讲解
        </el-button>
        <div v-if="aiExplanation" class="ai-box">
          <el-card>
            <h3>AI 讲解</h3>
            <div v-html="formattedAI"></div>
          </el-card>
        </div>

        <el-button
          type="success"
          @click="nextQuestion"
          style="margin-top: 20px"
        >下一题</el-button>
      </div>
    </div>

    <div v-else>
      <p>加载题目中...</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Home',
  data() {
    return {
      questions: [],           // 全部题目
      filteredQuestions: [],   // 筛选后的题目
      topics: [],              // 所有知识点列表
      selectedTopic: 'all',    // 当前选中知识点
      currentIndex: 0,
      selectedAnswer: '',
      showResult: false,
      isCorrect: false,
      analysis: '',
      resultText: '',
      aiExplanation: '',
      aiLoading: false
    }
  },
  computed: {
    currentQuestion() {
      return this.filteredQuestions[this.currentIndex] || null
    },
    formattedAI() {
      return this.aiExplanation.replace(/\n/g, '<br>')
    }
  },
  mounted() {
    this.fetchQuestions()
  },
  methods: {
    async fetchQuestions() {
      try {
        const res = await axios.get('http://127.0.0.1:5000/api/questions')
        this.questions = res.data
        // 提取所有知识点
        this.topics = [...new Set(this.questions.map(q => q.topic || '未分类'))]
        this.applyFilter()
      } catch (err) {
        console.error('获取题目失败', err)
        this.$message.error('无法连接服务器，请检查后端是否启动')
      }
    },
    applyFilter() {
      if (this.selectedTopic === 'all') {
        this.filteredQuestions = [...this.questions]
      } else {
        this.filteredQuestions = this.questions.filter(q => q.topic === this.selectedTopic)
      }
      this.currentIndex = 0
      this.showResult = false
      this.aiExplanation = ''
    },
    onTopicChange() {
      this.applyFilter()
    },
    goToQuestion(index) {
      this.currentIndex = index
      this.selectedAnswer = ''
      this.showResult = false
      this.aiExplanation = ''
    },
    async submitAnswer() {
      if (!this.selectedAnswer) {
        this.$message.warning('请先选择一个答案')
        return
      }
      try {
        const res = await axios.post('http://127.0.0.1:5000/api/submit', {
          id: this.currentQuestion.id,
          answer: this.selectedAnswer
        })
        this.isCorrect = res.data.correct
        this.analysis = res.data.analysis
        this.resultText = this.isCorrect
          ? '回答正确！'
          : `回答错误，正确答案是 ${res.data.correct_answer}`
        this.showResult = true
      } catch (err) {
        console.error('提交失败', err)
        this.$message.error('提交失败，请稍后重试')
      }
    },
    async getAIExplain() {
      this.aiLoading = true
      this.aiExplanation = ''
      try {
        const res = await axios.post('http://127.0.0.1:5000/api/ai-explain', {
          id: this.currentQuestion.id,
          user_answer: this.selectedAnswer
        })
        this.aiExplanation = res.data.explanation
      } catch (err) {
        console.error('AI讲解获取失败', err)
        this.$message.error('AI讲解暂时不可用，请稍后再试')
      } finally {
        this.aiLoading = false
      }
    },
    nextQuestion() {
      this.currentIndex = (this.currentIndex + 1) % this.filteredQuestions.length
      this.selectedAnswer = ''
      this.showResult = false
      this.aiExplanation = ''
    }
  }
}
</script>

<style scoped>
.home {
  max-width: 700px;
  margin: 40px auto;
}

.hero {
  text-align: center;
  padding: 30px 0 20px;
  margin-bottom: 20px;
}
.hero h1 {
  font-size: 32px;
  margin-bottom: 10px;
}
.hero p {
  font-size: 16px;
  color: #666;
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  padding: 0 10px;
}
.filter-label {
  font-weight: 600;
  color: #333;
}
.question-count {
  color: #999;
  font-size: 13px;
}

.question-index {
  text-align: center;
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.question-card {
  margin-bottom: 15px;
}

.question-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-bottom: 20px;
}

.result-box {
  margin-top: 20px;
}
.analysis-card {
  margin-top: 15px;
}
.ai-box {
  margin-top: 15px;
}
</style>