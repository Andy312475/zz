<template>
  <div class="knowledge">
    <h1>数据结构知识点学习</h1>
    <el-row :gutter="20">
      <el-col :span="6" v-for="item in topics" :key="item.id">
        <el-card :body-style="{ padding: '20px' }" class="topic-card">
          <h2>{{ item.name }}</h2>
          <p>{{ item.description }}</p>
          <el-button type="primary" @click="goToDetail(item.id)">进入学习</el-button>
          <el-button
            type="success"
            @click="generateQuestion(item.id)"
            :loading="generating === item.id"
            style="margin-left: 10px; margin-top: 10px;"
          >
            生成新题
          </el-button>
        </el-card>
      </el-col>
    </el-row>

    <!-- 知识点详情弹窗 -->
    <el-dialog
      :title="currentTopic.name"
      v-model="dialogVisible"
      width="70%"
      :before-close="handleClose"
    >
      <div v-if="currentTopic.content">
        <div v-html="currentTopic.content"></div>
      </div>
      <el-divider />
      <h3>相关题目</h3>
      <el-button @click="goToPractice(currentTopic.id)">去刷题页面练习</el-button>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Knowledge',
  data() {
    return {
      dialogVisible: false,
      currentTopic: {},
      generating: null, // 当前正在生成题目的知识点 id
      topics: [
        {
          id: 'linear-list',
          name: '线性表',
          description: '顺序表、链表、栈、队列等线性结构的基本概念与操作。',
          content: `
            <h3>线性表</h3>
            <p>线性表是最常用且最简单的一种数据结构。一个线性表是 n 个数据元素的有限序列。</p>
            <h4>顺序表</h4>
            <p>用一组地址连续的存储单元依次存储线性表的数据元素。支持随机存取，但插入和删除需要移动大量元素。</p>
            <h4>链表</h4>
            <p>用一组任意的存储单元存储线性表的数据元素，通过指针链接。插入和删除不需要移动元素，但无法随机存取。</p>
            <h4>栈</h4>
            <p>限定仅在表尾进行插入或删除操作的线性表，后进先出（LIFO）。</p>
            <h4>队列</h4>
            <p>只允许在一端插入、另一端删除的线性表，先进先出（FIFO）。</p>
          `
        },
        {
          id: 'tree',
          name: '树',
          description: '二叉树、二叉搜索树、平衡树等树形结构的遍历与性质。',
          content: `
            <h3>树</h3>
            <p>树是 n 个结点的有限集合，有且仅有一个根结点，其余结点可分为若干互不相交的子树。</p>
            <h4>二叉树</h4>
            <p>每个结点最多有两个子树（左子树和右子树），具有五种基本形态。</p>
            <h4>遍历方式</h4>
            <ul>
              <li>先序遍历：根左右</li>
              <li>中序遍历：左根右</li>
              <li>后序遍历：左右根</li>
              <li>层次遍历：从上到下、从左到右</li>
            </ul>
            <h4>二叉搜索树</h4>
            <p>左子树结点值 < 根结点值 < 右子树结点值，查找效率高。</p>
          `
        },
        {
          id: 'graph',
          name: '图',
          description: '图的存储（邻接矩阵、邻接表）、遍历（DFS、BFS）与应用。',
          content: `
            <h3>图</h3>
            <p>图由顶点集合和边集合组成，分为有向图和无向图。</p>
            <h4>存储方式</h4>
            <ul>
              <li>邻接矩阵：二维数组，适合稠密图。</li>
              <li>邻接表：顶点数组 + 链表，适合稀疏图。</li>
            </ul>
            <h4>遍历算法</h4>
            <p>深度优先搜索（DFS）：类似于树的先序遍历，递归或栈实现。</p>
            <p>广度优先搜索（BFS）：类似于树的层次遍历，使用队列实现。</p>
          `
        },
        {
          id: 'sort',
          name: '排序',
          description: '冒泡、选择、插入、快速、归并等排序算法的思想与实现。',
          content: `
            <h3>排序</h3>
            <h4>冒泡排序</h4>
            <p>重复走访要排序的元素列，依次比较相邻元素，如果逆序则交换，大的元素逐渐沉底。</p>
            <h4>快速排序</h4>
            <p>通过一趟排序将待排记录分割成独立的两部分，其中一部分记录的关键字均比另一部分小，再递归排序。</p>
            <h4>插入排序</h4>
            <p>每次将一个待排序的记录，按其关键字大小插入到前面已经排好序的子序列中的适当位置。</p>
            <h4>归并排序</h4>
            <p>将已有序的子序列合并，得到完全有序的序列；即先使每个子序列有序，再使子序列段间有序。</p>
          `
        }
      ]
    }
  },
  methods: {
    goToDetail(topicId) {
      this.currentTopic = this.topics.find(t => t.id === topicId) || {}
      this.dialogVisible = true
    },
    goToPractice(topicId) {
      // 跳转到刷题页，并传递知识点参数（后续可配合筛选功能）
      this.$router.push({ path: '/', query: { topic: topicId } })
      this.dialogVisible = false
    },
    handleClose() {
      this.dialogVisible = false
    },
    async generateQuestion(topicId) {
      this.generating = topicId
      try {
        const topicName = this.topics.find(t => t.id === topicId)?.name || topicId
        const res = await axios.post('http://127.0.0.1:5000/api/generate', {
          topic: topicName,
          difficulty: '中等'  // 可改为“简单”或“困难”
        })
        if (res.data.success) {
          this.$message.success('新题目已生成，快去刷题吧！')
        }
      } catch (err) {
        console.error('生成失败', err)
        this.$message.error('题目生成失败')
      } finally {
        this.generating = null
      }
    }
  }
}
</script>

<style scoped>
.knowledge {
  max-width: 1000px;
  margin: 40px auto;
}
.topic-card {
  margin-bottom: 20px;
}
.topic-card h2 {
  margin-top: 0;
}
</style>