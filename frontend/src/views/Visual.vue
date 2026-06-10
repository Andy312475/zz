<template>
  <div class="visual">
    <h1>数据结构可视化</h1>

    <el-tabs v-model="activeTab" type="border-card">
      <!-- 栈动画 -->
      <el-tab-pane label="栈 (Stack)" name="stack">
        <div class="canvas-container">
          <canvas ref="stackCanvas" width="600" height="400"></canvas>
        </div>
        <div class="controls">
          <el-input-number v-model="pushValue" :min="1" :max="99" />
          <el-button type="primary" @click="pushToStack">压入 (Push)</el-button>
          <el-button type="danger" @click="popFromStack">弹出 (Pop)</el-button>
          <el-button @click="resetStack">重置</el-button>
        </div>
        <p class="info">栈顶: {{ stack.length ? stack[stack.length-1] : '空' }} | 元素个数: {{ stack.length }}</p>
      </el-tab-pane>

      <!-- 排序动画 -->
      <el-tab-pane label="冒泡排序 (Bubble Sort)" name="sort">
        <div class="canvas-container">
          <canvas ref="sortCanvas" width="600" height="300"></canvas>
        </div>
        <div class="controls">
          <el-button type="primary" @click="startSort" :loading="sorting">开始排序</el-button>
          <el-button @click="resetSort">重置</el-button>
        </div>
        <p class="info">数据: [{{ arr.join(', ') }}]</p>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
export default {
  name: 'Visual',
  data() {
    return {
      activeTab: 'stack',
      // 栈相关
      stack: [],
      pushValue: Math.floor(Math.random() * 99) + 1,
      // 排序相关
      arr: [45, 12, 78, 34, 23, 67, 89, 10],
      sorting: false,
      animationSpeed: 500,
    }
  },
  methods: {
    // ========== 栈方法 ==========
    drawStack() {
      const canvas = this.$refs.stackCanvas
      if (!canvas) return
      const ctx = canvas.getContext('2d')
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // 画底座
      ctx.fillStyle = '#333'
      ctx.fillRect(200, 300, 200, 10)

      // 画栈元素
      const len = this.stack.length
      for (let i = 0; i < len; i++) {
        const y = 300 - (i + 1) * 40
        // 方块
        ctx.fillStyle = '#409EFF'
        ctx.fillRect(220, y, 160, 35)
        ctx.strokeStyle = '#fff'
        ctx.lineWidth = 2
        ctx.strokeRect(220, y, 160, 35)
        // 文字
        ctx.fillStyle = '#fff'
        ctx.font = '16px Arial'
        ctx.textAlign = 'center'
        ctx.fillText(this.stack[i], 300, y + 24)
      }

      // 栈顶指针
      if (len > 0) {
        const topY = 300 - len * 40 + 5
        ctx.fillStyle = '#E6A23C'
        ctx.font = 'bold 14px Arial'
        ctx.textAlign = 'left'
        ctx.fillText('← 栈顶', 390, topY + 18)
      }
    },

    pushToStack() {
      if (this.stack.length >= 7) {
        this.$message.warning('栈已满（最多演示7个元素）')
        return
      }
      this.stack.push(this.pushValue)
      this.pushValue = Math.floor(Math.random() * 99) + 1
      this.drawStack()
    },

    popFromStack() {
      if (this.stack.length === 0) {
        this.$message.warning('栈已空')
        return
      }
      this.stack.pop()
      this.drawStack()
    },

    resetStack() {
      this.stack = []
      this.pushValue = Math.floor(Math.random() * 99) + 1
      this.drawStack()
    },

    // ========== 排序方法 ==========
    drawSort() {
      const canvas = this.$refs.sortCanvas
      if (!canvas) return
      const ctx = canvas.getContext('2d')
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      const n = this.arr.length
      const barWidth = 50
      const startX = 50
      const baseY = 250

      for (let i = 0; i < n; i++) {
        const height = this.arr[i] * 2
        ctx.fillStyle = '#409EFF'
        ctx.fillRect(startX + i * (barWidth + 15), baseY - height, barWidth, height)
        ctx.fillStyle = '#333'
        ctx.font = '14px Arial'
        ctx.textAlign = 'center'
        ctx.fillText(this.arr[i], startX + i * (barWidth + 15) + barWidth / 2, baseY - height - 8)
      }
    },

    sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms))
    },

    async startSort() {
      this.sorting = true
      const n = this.arr.length
      const canvas = this.$refs.sortCanvas
      if (!canvas) return
      const ctx = canvas.getContext('2d')

      for (let i = 0; i < n - 1; i++) {
        for (let j = 0; j < n - i - 1; j++) {
          // 高亮当前比较的两个柱子
          this.drawSort()
          const barWidth = 50
          const startX = 50
          const baseY = 250
          // 绘制高亮
          ctx.fillStyle = '#F56C6C'
          ctx.fillRect(startX + j * (barWidth + 15), baseY - this.arr[j] * 2, barWidth, this.arr[j] * 2)
          ctx.fillRect(startX + (j + 1) * (barWidth + 15), baseY - this.arr[j + 1] * 2, barWidth, this.arr[j + 1] * 2)
          await this.sleep(this.animationSpeed)

          if (this.arr[j] > this.arr[j + 1]) {
            // 交换
            const temp = this.arr[j]
            this.arr[j] = this.arr[j + 1]
            this.arr[j + 1] = temp
            this.drawSort()
            await this.sleep(this.animationSpeed)
          }
        }
      }
      this.sorting = false
      this.drawSort()
      this.$message.success('排序完成！')
    },

    resetSort() {
      this.arr = [45, 12, 78, 34, 23, 67, 89, 10]
      this.sorting = false
      this.drawSort()
    }
  },

  mounted() {
    this.$nextTick(() => {
      this.drawStack()
      this.drawSort()
    })
  }
}
</script>

<style scoped>
.visual {
  max-width: 900px;
  margin: 40px auto;
}
.canvas-container {
  display: flex;
  justify-content: center;
  margin: 20px 0;
}
.controls {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 15px;
  flex-wrap: wrap;
  justify-content: center;
}
.info {
  text-align: center;
  font-size: 14px;
  color: #666;
}
</style>