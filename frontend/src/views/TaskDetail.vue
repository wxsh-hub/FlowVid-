<template>
  <div class="task-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>任务详情</span>
          <el-button @click="goBack">返回列表</el-button>
        </div>
      </template>

      <template v-if="task">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务ID">{{ task.id }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(task.status)">
              {{ getStatusText(task.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="视频链接" :span="2">
            <el-link type="primary" :href="task.video_url" target="_blank">
              {{ task.video_url }}
            </el-link>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatTime(task.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="完成时间">{{ formatTime(task.completed_at) }}</el-descriptions-item>
        </el-descriptions>

        <el-divider />

        <h3>处理进度</h3>
        <el-progress
          :percentage="task.progress"
          :status="task.status === 'completed' ? 'success' : task.status === 'failed' ? 'exception' : undefined"
          :stroke-width="20"
          style="margin: 20px 0;"
        />

        <el-steps :active="activeStep" finish-status="success" direction="vertical">
          <el-step
            v-for="(step, index) in task.steps"
            :key="index"
            :title="step.name"
            :description="getStepDescription(step)"
            :status="getStepStatus(step)"
          />
        </el-steps>

        <el-divider />

        <div v-if="task.status === 'completed' && task.output_path" class="result-section">
          <h3>生成结果</h3>
          <div class="video-container">
            <video
              :src="getVideoUrl(task.output_path)"
              controls
              style="width: 100%; max-width: 800px;"
            />
          </div>
          <el-button type="primary" size="large" @click="downloadVideo" style="margin-top: 20px;">
            <el-icon><Download /></el-icon>
            下载视频
          </el-button>
        </div>

        <div v-if="task.status === 'failed' && task.error_message" class="error-section">
          <h3>错误信息</h3>
          <el-alert :title="task.error_message" type="error" show-icon :closable="false" />
        </div>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Download } from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const task = ref<any>(null)
const loading = ref(false)
let timer: any = null

const activeStep = computed(() => {
  if (!task.value) return 0
  const steps = task.value.steps
  for (let i = steps.length - 1; i >= 0; i--) {
    if (steps[i].status === 'completed') return i + 1
    if (steps[i].status === 'processing') return i
  }
  return 0
})

const fetchTask = async () => {
  const taskId = route.params.id as string
  try {
    const res = await axios.get(`/api/tasks/${taskId}`)
    task.value = res.data
  } catch (error) {
    console.error('获取任务失败', error)
  }
}

const startPolling = () => {
  timer = setInterval(fetchTask, 3000)
}

const stopPolling = () => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

const getVideoUrl = (path: string) => {
  if (!path) return ''
  // 将绝对路径转换为相对路径
  const relativePath = path.replace(/.*storage/, '/storage')
  return relativePath
}

const downloadVideo = () => {
  if (task.value?.output_path) {
    const url = getVideoUrl(task.value.output_path)
    const link = document.createElement('a')
    link.href = url
    link.download = 'generated_video.mp4'
    link.click()
  }
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger',
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '等待中',
    processing: '处理中',
    completed: '已完成',
    failed: '失败',
  }
  return map[status] || status
}

const getStepDescription = (step: any) => {
  if (step.status === 'completed') return '已完成'
  if (step.status === 'processing') return `进行中 ${step.progress}%`
  if (step.status === 'failed') return '失败'
  return '等待中'
}

const getStepStatus = (step: any) => {
  const map: Record<string, string> = {
    completed: 'success',
    processing: 'process',
    failed: 'error',
    pending: 'wait',
  }
  return map[step.status] || 'wait'
}

const formatTime = (time: string) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

const goBack = () => {
  router.push('/')
}

onMounted(() => {
  fetchTask()
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.task-detail {
  max-width: 900px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-section {
  text-align: center;
  padding: 20px 0;
}

.video-container {
  margin: 20px 0;
  display: flex;
  justify-content: center;
}

.error-section {
  margin-top: 20px;
}

h3 {
  margin-bottom: 15px;
  color: #303133;
}
</style>
