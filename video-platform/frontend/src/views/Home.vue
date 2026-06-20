<template>
  <div class="home">
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="task-list-card">
          <template #header>
            <div class="card-header">
              <span>任务列表</span>
              <el-button type="primary" @click="goToCreate">
                <el-icon><Plus /></el-icon>
                新建任务
              </el-button>
            </div>
          </template>

          <el-table :data="tasks" style="width: 100%" v-loading="loading">
            <el-table-column prop="video_url" label="视频链接" min-width="200">
              <template #default="{ row }">
                <el-link type="primary" :href="row.video_url" target="_blank" :underline="false">
                  {{ truncateUrl(row.video_url) }}
                </el-link>
              </template>
            </el-table-column>

            <el-table-column prop="status" label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column prop="progress" label="进度" width="150">
              <template #default="{ row }">
                <el-progress
                  :percentage="row.progress"
                  :status="row.status === 'completed' ? 'success' : row.status === 'failed' ? 'exception' : undefined"
                />
              </template>
            </el-table-column>

            <el-table-column prop="current_step" label="当前步骤" width="150" />

            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.created_at) }}
              </template>
            </el-table-column>

            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button type="primary" link @click="goToDetail(row.id)">
                  查看详情
                </el-button>
                <el-button type="danger" link @click="handleDelete(row.id)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination" v-if="total > 20">
            <el-pagination
              v-model:current-page="currentPage"
              :page-size="20"
              :total="total"
              layout="prev, pager, next"
              @current-change="fetchTasks"
            />
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="info-card">
          <template #header>
            <span>快速开始</span>
          </template>

          <div class="quick-start">
            <el-steps direction="vertical" :active="0">
              <el-step title="配置API" description="在设置中配置MiMo、Pexels等API密钥" />
              <el-step title="创建任务" description="输入视频链接，选择配置" />
              <el-step title="等待处理" description="系统自动下载、转写、搜图、生成视频" />
              <el-step title="下载结果" description="处理完成后下载生成的视频" />
            </el-steps>
          </div>

          <el-divider />

          <div class="stats">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-statistic title="总任务数" :value="total" />
              </el-col>
              <el-col :span="12">
                <el-statistic title="已完成" :value="completedCount" />
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()
const tasks = ref<any[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)

const completedCount = computed(() => tasks.value.filter(t => t.status === 'completed').length)

const fetchTasks = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/tasks', {
      params: { limit: 20, offset: (currentPage.value - 1) * 20 }
    })
    tasks.value = res.data.tasks
    total.value = res.data.total
  } catch (error) {
    ElMessage.error('获取任务列表失败')
  } finally {
    loading.value = false
  }
}

const goToCreate = () => {
  router.push('/create')
}

const goToDetail = (id: string) => {
  router.push(`/task/${id}`)
}

const handleDelete = async (id: string) => {
  try {
    await ElMessageBox.confirm('确定删除该任务吗？', '提示', { type: 'warning' })
    await axios.delete(`/api/tasks/${id}`)
    ElMessage.success('删除成功')
    fetchTasks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const truncateUrl = (url: string) => {
  if (!url) return ''
  return url.length > 50 ? url.substring(0, 50) + '...' : url
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

const formatTime = (time: string) => {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN')
}

onMounted(fetchTasks)
</script>

<style scoped>
.home {
  width: 100%;
}

.task-list-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-card {
  position: sticky;
  top: 20px;
}

.quick-start {
  padding: 10px 0;
}

.stats {
  margin-top: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
