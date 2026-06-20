<template>
  <div class="create">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>创建视频生成任务</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="视频链接" prop="video_url">
          <el-input
            v-model="form.video_url"
            placeholder="请输入视频链接（支持抖音、B站等）"
            clearable
            @blur="validateUrl"
          />
          <div class="form-tip">支持抖音、B站、YouTube等主流视频平台</div>
          <el-alert
            v-if="urlWarning"
            :title="urlWarning"
            type="warning"
            show-icon
            :closable="false"
            style="margin-top: 10px;"
          />
        </el-form-item>

        <el-form-item label="截取时长">
          <el-select v-model="form.duration" placeholder="选择截取时长">
            <el-option label="全部" :value="0" />
            <el-option label="1分钟" :value="60" />
            <el-option label="3分钟" :value="180" />
            <el-option label="5分钟" :value="300" />
            <el-option label="10分钟" :value="600" />
          </el-select>
          <div class="form-tip">选择"全部"则使用完整视频</div>
        </el-form-item>

        <el-divider>AI模型配置</el-divider>

        <el-form-item label="配置方案" prop="config_id">
          <el-select v-model="form.config_id" placeholder="请选择配置方案" style="width: 100%">
            <el-option
              v-for="config in configs"
              :key="config.id"
              :label="config.name"
              :value="config.id"
            >
              <div class="config-option">
                <span>{{ config.name }}</span>
                <span class="config-info">{{ config.text_model }} / {{ config.image_model }}</span>
              </div>
            </el-option>
          </el-select>
          <div class="form-tip">
            请先在
            <el-button type="primary" link @click="goToConfigs">配置管理</el-button>
            中创建配置方案
          </div>
        </el-form-item>

        <template v-if="selectedConfig">
          <el-descriptions :column="2" border class="config-detail">
            <el-descriptions-item label="文本处理模型">
              {{ selectedConfig.text_model }}
            </el-descriptions-item>
            <el-descriptions-item label="AI生图模型">
              {{ selectedConfig.image_model }}
            </el-descriptions-item>
            <el-descriptions-item label="TTS语音">
              {{ getVoiceName(selectedConfig.tts_voice) }}
            </el-descriptions-item>
            <el-descriptions-item label="语速">
              {{ selectedConfig.tts_rate }}
            </el-descriptions-item>
          </el-descriptions>
        </template>

        <el-form-item>
          <el-button type="primary" size="large" @click="handleSubmit" :loading="submitting" :disabled="!form.config_id">
            开始生成
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const formRef = ref()
const submitting = ref(false)
const configs = ref<any[]>([])
const urlWarning = ref('')

const form = ref({
  video_url: '',
  config_id: '',
  duration: 0,  // 默认全部
})

const validateUrl = () => {
  const url = form.value.video_url
  urlWarning.value = ''

  if (!url) return

  // 检测搜索链接
  const searchPatterns = [
    /\/search\//,
    /\/jingxuan\/search/,
    /type=general/,
  ]

  for (const pattern of searchPatterns) {
    if (pattern.test(url)) {
      urlWarning.value = '这是一个搜索链接，请提供视频详情页链接（如：https://www.douyin.com/video/xxx）'
      return
    }
  }
}

const rules = {
  video_url: [
    { required: true, message: '请输入视频链接', trigger: 'blur' },
  ],
  config_id: [
    { required: true, message: '请选择配置方案', trigger: 'change' },
  ],
}

const selectedConfig = computed(() => {
  if (!form.value.config_id) return null
  return configs.value.find(c => c.id === form.value.config_id)
})

const fetchConfigs = async () => {
  try {
    const res = await axios.get('/api/configs')
    configs.value = res.data.configs
    if (configs.value.length === 1) {
      form.value.config_id = configs.value[0].id
    }
  } catch (error) {
    console.error('获取配置失败', error)
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  if (!form.value.config_id) {
    ElMessage.warning('请先选择配置方案')
    return
  }

  submitting.value = true
  try {
    const res = await axios.post('/api/tasks', form.value)
    ElMessage.success('任务创建成功')
    router.push(`/task/${res.data.task_id}`)
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '创建失败')
  } finally {
    submitting.value = false
  }
}

const getVoiceName = (voice: string) => {
  const map: Record<string, string> = {
    'zh-CN-YunxiNeural': '云希（男声）',
    'zh-CN-XiaoxiaoNeural': '晓晓（女声）',
    'zh-CN-YunyangNeural': '云扬（男声）',
    'zh-CN-XiaohanNeural': '晓涵（女声）',
  }
  return map[voice] || voice
}

const goBack = () => {
  router.push('/')
}

const goToConfigs = () => {
  router.push('/configs')
}

onMounted(fetchConfigs)
</script>

<style scoped>
.create {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.config-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.config-info {
  font-size: 12px;
  color: #909399;
}

.config-detail {
  margin-bottom: 20px;
}
</style>
