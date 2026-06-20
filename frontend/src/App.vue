<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <div class="header-content">
        <h1>AI视频生成平台</h1>
        <p class="subtitle">输入视频链接，自动生成带字幕的配音视频</p>
      </div>
    </el-header>

    <el-main class="app-main">
      <router-view />
    </el-main>

    <el-footer class="app-footer">
      <p>AI Video Generation Platform © 2024</p>
    </el-footer>
  </el-container>
</template>

<script setup lang="ts">
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background-color: #f5f7fa;
}

.app-container {
  min-height: 100vh;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 120px !important;
}

.header-content {
  text-align: center;
}

.header-content h1 {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 14px;
  opacity: 0.9;
}

.app-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
}

.app-footer {
  text-align: center;
  color: #909399;
  font-size: 12px;
  height: 50px !important;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
