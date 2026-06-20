<template>
  <div class="configs">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>配置方案管理</span>
          <div>
            <el-button type="primary" @click="showDialog()">新建配置方案</el-button>
            <el-button @click="goBack">返回</el-button>
          </div>
        </div>
      </template>

      <el-empty v-if="!loading && configs.length === 0" description="暂无配置方案，请先创建" />

      <el-table v-else :data="configs" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="方案名称" width="150" />
        <el-table-column label="文本模型" width="200">
          <template #default="{ row }">
            <div>{{ row.text_model }}</div>
            <div class="model-url">{{ row.text_base_url }}</div>
          </template>
        </el-table-column>
        <el-table-column label="图片模型" width="200">
          <template #default="{ row }">
            <div>{{ row.image_model }}</div>
            <div class="model-url">{{ row.image_base_url }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="tts_voice" label="TTS语音" width="120">
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

    <el-dialog v-model="dialogVisible" :title="editingConfig ? '编辑配置方案' : '新建配置方案'" width="700px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="方案名称" required>
          <el-input v-model="form.name" placeholder="请输入方案名称，如：GPT-4方案" />
        </el-form-item>

        <el-divider>文本模型配置（关键词提取）</el-divider>

        <el-form-item label="协议类型">
          <el-select v-model="form.text_protocol" placeholder="选择协议">
            <el-option label="OpenAI兼容" value="openai" />
            <el-option label="Anthropic" value="anthropic" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="Base URL" required>
          <el-input v-model="form.text_base_url" placeholder="如：https://api.openai.com/v1" />
        </el-form-item>
        <el-form-item label="模型名称" required>
          <el-input v-model="form.text_model" placeholder="如：gpt-4o, claude-3-5-sonnet" />
        </el-form-item>
        <el-form-item label="API Key" required>
          <el-input v-model="form.text_api_key" placeholder="请输入API Key" show-password />
          <div class="form-tip" v-if="editingConfig">留空表示不修改</div>
        </el-form-item>

        <el-divider>图片模型配置（AI生图）</el-divider>

        <el-form-item label="协议类型">
          <el-select v-model="form.image_protocol" placeholder="选择协议" @change="handleProtocolChange">
            <el-option label="豆包Seedream" value="doubao" />
            <el-option label="OpenAI DALL-E" value="openai" />
            <el-option label="通义万相" value="dashscope" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="Base URL" required>
          <el-input v-model="form.image_base_url" placeholder="API调用地址" />
        </el-form-item>
        <el-form-item label="模型名称" required>
          <el-input v-model="form.image_model" placeholder="模型名称" />
        </el-form-item>
        <el-form-item label="API Key" required>
          <el-input v-model="form.image_api_key" placeholder="请输入API Key" show-password />
          <div class="form-tip" v-if="editingConfig">留空表示不修改</div>
        </el-form-item>

        <el-divider>TTS语音配置</el-divider>

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
        <el-button type="primary" @click="handleSubmit" :loading="submitting">保存</el-button>
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

const defaultForm = {
  name: '',
  text_base_url: 'https://api.openai.com/v1',
  text_model: 'gpt-4o',
  text_api_key: '',
  text_protocol: 'openai',
  image_base_url: 'https://ark.cn-beijing.volces.com/api/v3/images/generations',
  image_model: 'doubao-seedream-4-5-251128',
  image_api_key: '',
  image_protocol: 'doubao',
  tts_voice: 'zh-CN-YunxiNeural',
  tts_rate: '+0%',
}

const form = ref({ ...defaultForm })

const protocolPresets: Record<string, any> = {
  doubao: {
    image_base_url: 'https://ark.cn-beijing.volces.com/api/v3/images/generations',
    image_model: 'doubao-seedream-4-5-251128',
  },
  openai: {
    image_base_url: 'https://api.openai.com/v1',
    image_model: 'dall-e-3',
  },
  dashscope: {
    image_base_url: 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis',
    image_model: 'wanx-v1',
  },
}

const handleProtocolChange = (protocol: string) => {
  const preset = protocolPresets[protocol]
  if (preset) {
    form.value.image_base_url = preset.image_base_url
    form.value.image_model = preset.image_model
  }
}

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

const showDialog = async (config?: any) => {
  if (config) {
    editingConfig.value = config
    try {
      const res = await axios.get('/api/configs/' + config.id)
      const fullConfig = res.data
      form.value = {
        name: fullConfig.name,
        text_base_url: fullConfig.text_base_url || 'https://api.openai.com/v1',
        text_model: fullConfig.text_model || 'gpt-4o',
        text_api_key: fullConfig.text_api_key ? '**********' : '',
        text_protocol: fullConfig.text_protocol || 'openai',
        image_base_url: fullConfig.image_base_url || 'https://ark.cn-beijing.volces.com/api/v3/images/generations',
        image_model: fullConfig.image_model || 'doubao-seedream-4-5-251128',
        image_api_key: fullConfig.image_api_key ? '**********' : '',
        image_protocol: fullConfig.image_protocol || 'doubao',
        tts_voice: fullConfig.tts_voice || 'zh-CN-YunxiNeural',
        tts_rate: fullConfig.tts_rate || '+0%',
      }
    } catch (error) {
      ElMessage.error('获取配置详情失败')
      return
    }
  } else {
    editingConfig.value = null
    form.value = { ...defaultForm }
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!form.value.name) {
    ElMessage.warning('请输入方案名称')
    return
  }

  submitting.value = true
  try {
    if (editingConfig.value) {
      await axios.put('/api/configs/' + editingConfig.value.id, form.value)
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
    await ElMessageBox.confirm('确定删除该配置方案吗？', '提示', { type: 'warning' })
    await axios.delete('/api/configs/' + id)
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

.model-url {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

:deep(.el-divider__text) {
  font-weight: 600;
  color: #303133;
}
</style>
