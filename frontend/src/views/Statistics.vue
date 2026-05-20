<template>
  <div class="statistics">
    <h1>学习统计</h1>
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <p>总刷题数</p>
          <h2>{{ total }}</h2>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <p>正确题数</p>
          <h2>{{ correct }}</h2>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <p>总正确率</p>
          <h2>{{ (accuracy * 100).toFixed(0) }}%</h2>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top: 20px">
      <h3>知识点正确率</h3>
      <div ref="chartDom" style="width: 100%; height: 400px"></div>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios'
import * as echarts from 'echarts'

export default {
  name: 'Statistics',
  data() {
    return {
      total: 0,
      correct: 0,
      accuracy: 0,
      topics: []
    }
  },
  mounted() {
    this.fetchStatistics()
  },
  methods: {
    async fetchStatistics() {
      try {
        const res = await axios.get('http://127.0.0.1:5000/api/statistics')
        const data = res.data
        this.total = data.total
        this.correct = data.correct
        this.accuracy = data.accuracy
        this.topics = data.topics
        this.$nextTick(() => {
          this.drawChart()
        })
      } catch (err) {
        console.error('获取统计失败', err)
        this.$message.error('无法获取学习数据')
      }
    },
    drawChart() {
      const chartDom = this.$refs.chartDom
      if (!chartDom) return
      const myChart = echarts.init(chartDom)
      const option = {
        tooltip: {
          trigger: 'item'
        },
        legend: {
          data: ['正确率']
        },
        radar: {
          indicator: this.topics.map(t => ({ name: t.topic, max: 100 }))
        },
        series: [{
          type: 'radar',
          data: [{
            value: this.topics.map(t => t.accuracy * 100),
            name: '正确率'
          }]
        }]
      }
      myChart.setOption(option)
    }
  }
}
</script>

<style scoped>
.statistics {
  max-width: 800px;
  margin: 40px auto;
}
h2 {
  color: #409EFF;
}
</style>