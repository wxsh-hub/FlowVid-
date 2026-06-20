<template>
  <div class="configs">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>API配置管理</span>
          <div>
            <el-button type="primary" @click="showDialog()">新建配置</el-button>
            <el-button @click="goBack">返回</el-button>
          </div>
        </div>
      </template>

      <el-table :data="configs" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="配置名称" width="150" />
        <el-table-column prop="mimo_api_key" label="MiMo API Key" width="200" />
        <el-table-column prop="pexels_api_key" label="Pexels API Key" width="200" />
        <el-table-column prop="seedream_api_key" label="豆包API Key" width="200" />
        <el-table-column prop="tts_voice" label="TTS语音" width="150">
          <template #default="{ row }">
            {{ getVoiceName(row.tts_voice) }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" link @click="showDialog(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editingConfig ? '编辑配置' : '新建配置'" width="500px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="配置名称">
          <el-input v-model="form.name" placeholder="请输入配置名称" />
        </el-form-item>
        <el-form-item label="MiMo API Key">
          <el-input v-model="form.mimo_api_key" placeholder="请输入MiMo API Key" show-password />
        </el-form-item>
        <el-form-item label="MiMo Base URL">
          <el-input v-model="form.mimo_base_url" placeholder="API基础URL" />
        </el-form-item>
        <el-form-item label="Pexels API Key">
          <el-input v-model="form.pexels_api_key" placeholder="请输入Pexels API Key" show-password />
        </el-form-item>
        <el-form-item label="豆包API Key">
          <el-input v-model="form.seedream_api_key" placeholder="格式: ark-xxx" show-password />
          <div class="form-tip">用于AI生图，格式为 ark-xxx</div>
        </el-form-item>
        <el-form-item label="TTS语音">
          <el-select v-model="form.tts_voice" placeholder="选择语音">
            <el-option label="云希（男声）" value="zh-CN-YunxiNeural" />
            <el-option label="晓晓（女声）" value="zh-CN-XiaoxiaoNeural" />
            <el-option label="云扬（男声）" value="zh-CN-YunyangNeural" />
            <el-option label="晓涵（女声）" value="zh-CN-XiaohanNeural" />
          </el-select>
        </el-form-item>
        <el-form-item label="语速">
          <el-input v-model="form.tts_rate" placeholder="如: +0%, +10%, -10%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const configs = ref<any[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)
const editingConfig = ref<any>(null)

const form = ref({
  name: '默认配置',
  mimo_api_key: '',
  mimo_base_url: 'https://api.mimoai.com/v1',
  pexels_api_key: '',
  seedream_api_key: '',
  tts_voice: 'zh-CN-YunxiNeural',
  tts_rate: '+0%',
})

const fetchConfigs = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/configs')
    configs.value = res.data.configs
  } catch (error) {
    ElMessage.error('获取配置失败')
  } finally {
    loading.value = false
  }
}

const showDialog = (config?: any) => {
  if (config) {
    editingConfig.value = config
    form.value = {
      name: config.name,
      mimo_api_key: '',
      mimo_base_url: config.mimo_base_url || 'https://api.mimoai.com/v1',
      pexels_api_key: '',
      seedream_api_key: '',
      tts_voice: config.tts_voice || 'zh-CN-YunxiNeural',
      tts_rate: config.tts_rate || '+0%',
    }
  } else {
    editingConfig.value = null
    form.value = {
      name: '默认配置',
      mimo_api_key: '',
      mimo_base_url: 'https://api.mimoai.com/v1',
      pexels_api_key: '',
      seedream_api_key: '',
      tts_voice: 'zh-CN-YunxiNeural',
      tts_rate: '+0%',
    }
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  submitting.value = true
  try {
    if (editingConfig.value) {
      await axios.put(`/api/configs/${editingConfig.value.id}`, form.value)
      ElMessage.success('更新成功')
    } else {
      await axios.post('/api/configs', form.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchConfigs()
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (id: string) => {
  try {
    await ElMessageBox.confirm('确定删除该配置吗？', '提示', { type: 'warning' })
    await axios.delete(`/api/configs/${id}`)
    ElMessage.success('删除成功')
    fetchConfigs()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
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

const formatTime = (time: string) => {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN')
}

const goBack = () => {
  router.push('/')
}

onMounted(fetchConfigs)
</script>

<style scoped>
.configs {
  max-width: 1200px;
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
