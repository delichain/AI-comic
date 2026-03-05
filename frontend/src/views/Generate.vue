<template>
  <div class="generate-container">
    <el-row :gutter="20">
      <!-- Left: Preview -->
      <el-col :span="14">
        <el-card class="preview-card">
          <template #header>
            <div class="card-header">
              <span>预览</span>
              <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
            </div>
          </template>
          
          <div class="preview-area">
            <div v-if="!currentImage" class="empty-preview">
              <el-icon size="64"><Picture /></el-icon>
              <p>选择文件开始生成</p>
            </div>
            <img v-else :src="currentImage" alt="Preview" class="preview-image" />
          </div>
          
          <div class="preview-controls">
            <el-button 
              :disabled="currentPage <= 1" 
              @click="prevPage"
            >
              <el-icon><ArrowLeft /></el-icon>
              上一页
            </el-button>
            <el-button 
              :disabled="currentPage >= totalPages" 
              @click="nextPage"
            >
              下一页
              <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </el-card>
      </el-col>
      
      <!-- Right: Settings -->
      <el-col :span="10">
        <el-card class="settings-card">
          <template #header>
            <span>生成设置</span>
          </template>
          
          <el-form label-width="100px">
            <!-- Select File -->
            <el-form-item label="选择文件">
              <el-select 
                v-model="selectedFileId" 
                placeholder="请选择上传的文件"
                @change="handleFileChange"
              >
                <el-option
                  v-for="item in fileList"
                  :key="item.id"
                  :label="item.filename"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
            
            <!-- AI Model -->
            <el-form-item label="AI 模型">
              <el-select v-model="settings.modelId" placeholder="选择 AI 模型">
                <el-option
                  v-for="item in modelList"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
            
            <!-- Style -->
            <el-form-item label="动漫风格">
              <el-select v-model="settings.style" placeholder="选择风格">
                <el-option label="日漫" value="japanese" />
                <el-option label="美漫" value="american" />
                <el-option label="韩漫" value="korean" />
                <el-option label="写实" value="realistic" />
                <el-option label="卡通风" value="cartoon" />
              </el-select>
            </el-form-item>
            
            <!-- Quality -->
            <el-form-item label="清晰度">
              <el-radio-group v-model="settings.quality">
                <el-radio label="low">低 (512x512)</el-radio>
                <el-radio label="medium">中 (1024x1024)</el-radio>
                <el-radio label="high">高 (2048x2048)</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <!-- Effects -->
            <el-form-item label="动态效果">
              <el-checkbox-group v-model="settings.effects">
                <el-checkbox label="motion">动态模糊</el-checkbox>
                <el-checkbox label="particle">粒子效果</el-checkbox>
                <el-checkbox label="zoom">镜头推拉</el-checkbox>
                <el-checkbox label="pan">平移效果</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            
            <!-- Prompt -->
            <el-form-item label="自定义 Prompt">
              <el-input
                v-model="settings.prompt"
                type="textarea"
                :rows="3"
                placeholder="可选输入自定义提示词，使用 {{prompt}} 引用"
              />
            </el-form-item>
          </el-form>
          
          <!-- Generate Button -->
          <div class="generate-actions">
            <el-button 
              type="primary" 
              size="large"
              :loading="generating"
              :disabled="!selectedFileId || !settings.modelId"
              @click="startGenerate"
            >
              {{ generating ? '生成中...' : '开始生成' }}
            </el-button>
            <el-button 
              v-if="generating"
              type="danger"
              @click="stopGenerate"
            >
              停止
            </el-button>
          </div>
        </el-card>
        
        <!-- Progress -->
        <el-card v-if="generating || progress > 0" class="progress-card">
          <el-progress 
            :percentage="progress" 
            :stroke-width="20"
            :status="progressStatus"
          />
          <p class="progress-info">
            正在处理第 {{ currentProcessPage }} / {{ totalPages }} 页
          </p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElNotification } from 'element-plus'
import { Picture, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import api from '../api'

const route = useRoute()

const selectedFileId = ref(null)
const fileList = ref([])
const modelList = ref([])
const currentImage = ref(null)
const currentPage = ref(0)
const totalPages = ref(0)
const generating = ref(false)
const progress = ref(0)
const currentProcessPage = ref(0)
const progressStatus = ref('')

const settings = reactive({
  modelId: null,
  style: 'japanese',
  quality: 'high',
  effects: ['motion'],
  prompt: ''
})

onMounted(async () => {
  await Promise.all([loadFiles(), loadModels()])
  
  // If fileId in query
  if (route.query.fileId) {
    selectedFileId.value = parseInt(route.query.fileId)
    handleFileChange()
  }
})

async function loadFiles() {
  try {
    const response = await api.get('/upload/history')
    fileList.value = response.items || []
  } catch (error) {
    console.error('加载文件列表失败', error)
  }
}

async function loadModels() {
  try {
    const response = await api.get('/ai-models')
    modelList.value = response || []
  } catch (error) {
    console.error('加载模型列表失败', error)
  }
}

async function handleFileChange() {
  if (!selectedFileId.value) return
  
  try {
    const response = await api.get(`/upload/${selectedFileId.value}/pages`)
    totalPages.value = response.pages || 0
    currentPage.value = 1
    
    // Load first page preview
    if (totalPages.value > 0) {
      await loadPagePreview(1)
    }
  } catch (error) {
    ElMessage.error('加载文件信息失败')
  }
}

async function loadPagePreview(pageNum) {
  try {
    const response = await api.get(`/upload/${selectedFileId.value}/page/${pageNum}`)
    currentImage.value = response.url
    currentPage.value = pageNum
  } catch (error) {
    console.error('加载预览失败', error)
  }
}

function prevPage() {
  if (currentPage.value > 1) {
    loadPagePreview(currentPage.value - 1)
  }
}

function nextPage() {
  if (currentPage.value < totalPages.value) {
    loadPagePreview(currentPage.value + 1)
  }
}

async function startGenerate() {
  if (!selectedFileId.value || !settings.modelId) {
    ElMessage.warning('请选择文件和模型')
    return
  }
  
  generating.value = true
  progress.value = 0
  currentProcessPage.value = 1
  progressStatus.value = ''
  
  try {
    const response = await api.post('/generate/start', {
      file_id: selectedFileId.value,
      model_id: settings.modelId,
      style: settings.style,
      quality: settings.quality,
      effects: settings.effects,
      prompt: settings.prompt
    })
    
    // 轮询进度
    await pollProgress(response.task_id)
    
  } catch (error) {
    ElMessage.error(error || '生成失败')
    generating.value = false
    progressStatus.value = 'exception'
  }
}

async function pollProgress(taskId) {
  const pollInterval = setInterval(async () => {
    try {
      const response = await api.get(`/generate/${taskId}/status`)
      
      progress.value = response.progress || 0
      currentProcessPage.value = response.current_page || 0
      
      if (response.status === 'completed') {
        clearInterval(pollInterval)
        generating.value = false
        progressStatus.value = 'success'
        ElNotification.success({
          title: '生成完成',
          message: '漫画生成成功！'
        })
      } else if (response.status === 'failed') {
        clearInterval(pollInterval)
        generating.value = false
        progressStatus.value = 'exception'
        ElMessage.error(response.error || '生成失败')
      }
    } catch (error) {
      console.error('轮询进度失败', error)
    }
  }, 2000)
}

function stopGenerate() {
  generating.value = false
  ElMessage.info('已停止生成')
}
</script>

<style scoped>
.generate-container {
  min-height: 100%;
}

.preview-card, .settings-card, .progress-card {
  border-radius: 8px;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-info {
  color: #909399;
  font-size: 14px;
}

.preview-area {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 8px;
  overflow: hidden;
}

.empty-preview {
  text-align: center;
  color: #909399;
}

.empty-preview p {
  margin-top: 16px;
}

.preview-image {
  max-width: 100%;
  max-height: 400px;
  object-fit: contain;
}

.preview-controls {
  margin-top: 16px;
  display: flex;
  justify-content: center;
  gap: 16px;
}

.generate-actions {
  margin-top: 24px;
  text-align: center;
}

.progress-card {
  margin-top: 20px;
}

.progress-info {
  text-align: center;
  color: #606266;
  margin-top: 12px;
}
</style>
