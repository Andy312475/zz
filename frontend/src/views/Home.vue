<template>
  <div class="home">
    <h1>数据结构刷题</h1>
    <div v-if="currentQuestion">
      <el-card class="question-card">
        <h2>{{ currentQuestion.title }}</h2>
        <el-radio-group v-model="selectedAnswer">
          <el-radio v-for="opt in currentQuestion.options" :key="opt" :label="opt.charAt(0)">{{ opt }}</el-radio>
        </el-radio-group>
        <el-button type="primary" @click="submitAnswer" style="margin-top: 20px">提交答案</el-button>
      </el-card>

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

        <el-button type="success" @click="nextQuestion" style="margin-top: 20px">下一题</el-button>
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
      questions: [],
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
      return this.questions[this.currentIndex] || null
    },
    formattedAI() {
      // 简单地将换行符转换为 <br>，后面可以引入 marked 库处理 Markdown
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
      } catch (err) {
        console.error('获取题目失败', err)
        this.$message.error('无法连接服务器，请检查后端是否启动')
      }
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
        this.resultText = this.isCorrect ? '回答正确！' : `回答错误，正确答案是 ${res.data.correct_answer}`
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
      this.currentIndex = (this.currentIndex + 1) % this.questions.length
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
.question-card {
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