<template>
  <div id="app">
    <el-menu :default-active="activeIndex" mode="horizontal" router>
      <el-menu-item index="/">刷题</el-menu-item>
      <el-menu-item index="/knowledge">知识点</el-menu-item>
      <el-menu-item index="/statistics">学习统计</el-menu-item>
    </el-menu>
    <router-view />
  </div>
</template>

<script>
export default {
  data() {
    return {
      activeIndex: '/'
    }
  },
  watch: {
    $route(to) {
      this.activeIndex = to.path
    }
  }
}
</script>