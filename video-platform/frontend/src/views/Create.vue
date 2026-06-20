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
          />
          <div class="form-tip">支持抖音、B站、YouTube等主流视频平台</div>
        </el-form-item>

        <el-divider>API配置</el-divider>

        <el-form-item label="配置方案">
          <el-select v-model="form.config_id" placeholder="选择已有配置" clearable @change="handleConfigChange">
            <el-option
              v-for="config in configs"
              :key="config.id"
              :label="config.name"
              :value="config.id"
            />
          </el-select>
          <el-button type="primary" link @click="goToConfigs" style="margin-left: 10px;">
            管理配置
          </el-button>
        </el-form-item>

        <template v-if="!form.config_id">
          <el-form-item label="MiMo API Key" prop="mimo_api_key">
            <el-input
              v-model="form.mimo_api_key"
              placeholder="请输入MiMo API Key"
              show-password
            />
          </el-form-item>

          <el-form-item label="Pexels API Key" prop="pexels_api_key">
            <el-input
              v-model="form.pexels_api_key"
              placeholder="请输入Pexels API Key（可选，用于搜图）"
              show-password
            />
          </el-form-item>

          <el-form-item label="豆包API Key" prop="seedream_api_key">
            <el-input
              v-model="form.seedream_api_key"
              placeholder="格式: ark-xxx（用于AI生图）"
              show-password
            />
            <div class="form-tip">用于AI生图保底，格式为 ark-xxx</div>
          </el-form-item>
        </template>

        <el-form-item label="TTS语音">
          <el-select v-model="form.tts_voice" placeholder="选择语音">
            <el-option label="云希（男声）" value="zh-CN-YunxiNeural" />
            <el-option label="晓晓（女声）" value="zh-CN-XiaoxiaoNeural" />
            <el-option label="云扬（男声）" value="zh-CN-YunyangNeural" />
            <el-option label="晓涵（女声）" value="zh-CN-XiaohanNeural" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" size="large" @click="handleSubmit" :loading="submitting">
            开始生成
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const formRef = ref()
const submitting = ref(false)
const configs = ref<any[]>([])

const form = ref({
  video_url: '',
  config_id: '',
  mimo_api_key: '',
  pexels_api_key: '',
  seedream_api_key: '',
  tts_voice: 'zh-CN-YunxiNeural',
})

const rules = {
  video_url: [
    { required: true, message: '请输入视频链接', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL', trigger: 'blur' },
  ],
}

const fetchConfigs = async () => {
  try {
    const res = await axios.get('/api/configs')
    configs.value = res.data.configs
  } catch (error) {
    console.error('获取配置失败', error)
  }
}

const handleConfigChange = (configId: string) => {
  if (configId) {
    const config = configs.value.find(c => c.id === configId)
    if (config) {
      form.value.tts_voice = config.tts_voice || 'zh-CN-YunxiNeural'
    }
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
  } catch {
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
</style>
