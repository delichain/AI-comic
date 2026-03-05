<template>
  <div class="upload-container">
    <el-card class="upload-card">
      <template #header>
        <div class="card-header">
          <span>上传 PDF 文件</span>
        </div>
      </template>
      
      <!-- Upload Area -->
      <div 
        class="upload-area"
        :class="{ 'is-dragover': isDragover }"
        @dragover.prevent="isDragover = true"
        @dragleave.prevent="isDragover = false"
        @drop.prevent="handleDrop"
      >
        <el-upload
          ref="uploadRef"
          class="upload-demo"
          drag
          :auto-upload="false"
          :limit="1"
          :on-change="handleFileChange"
          :on-exceed="handleExceed"
          accept=".pdf"
          :before-upload="beforeUpload"
        >
          <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
          <div class="el-upload__text">
            拖拽文件到此处 或 <em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持 PDF 文件，最大 {{ maxFileSize }}MB
            </div>
          </template>
        </el-upload>
      </div>
      
      <!-- File Info -->
      <div v-if="file" class="file-info">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="文件名">{{ file.name }}</el-descriptions-item>
          <el-descriptions-item label="文件大小">{{ formatFileSize(file.size) }}</el-descriptions-item>
        </el-descriptions>
      </div>
      
      <!-- Actions -->
      <div class="actions">
        <el-button 
          type="primary" 
          :loading="uploading" 
          :disabled="!file"
          @click="handleUpload"
        >
          {{ uploading ? '上传中...' : '开始上传' }}
        </el-button>
      </div>
      
      <!-- Upload Progress -->
      <div v-if="uploading" class="progress-area">
        <el-progress 
          :percentage="uploadProgress" 
          :status="uploadStatus"
          :stroke-width="20"
        />
        <p class="progress-text">{{ progressText }}</p>
      </div>
      
      <!-- Upload Result -->
      <div v-if="uploadResult" class="result-area">
        <el-alert
          :title="uploadResult.success ? '上传成功' : '上传失败'"
          :type="uploadResult.success ? 'success' : 'error'"
          :description="uploadResult.message"
          show-icon
          :closable="false"
        />
      </div>
    </el-card>
    
    <!-- History -->
    <el-card class="history-card">
      <template #header>
        <div class="card-header">
          <span>上传历史</span>
          <el-button size="small" @click="loadHistory">刷新</el-button>
        </div>
      </template>
      
      <el-table :data="uploadHistory" style="width: 100%">
        <el-table-column prop="filename" label="文件名" />
        <el-table-column prop="pages" label="页数" width="80" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : 'warning'">
              {{ row.status === 'completed' ? '已完成' : '处理中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="上传时间" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="goToGenerate(row)">
              生成漫画
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElNotification } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import api from '../api'

const router = useRouter()

const uploadRef = ref()
const file = ref(null)
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadStatus = ref('')
const progressText = ref('正在上传...')
const uploadResult = ref(null)
const uploadHistory = ref([])
const isDragover = ref(false)

const maxFileSize = 100 // MB

function handleFileChange(uploadFile) {
  file.value = uploadFile.raw
  uploadResult.value = null
}

function handleExceed() {
  ElMessage.warning('只能上传一个文件')
}

function beforeUpload(uploadFile) {
  return false // 手动上传
}

function handleDrop(e) {
  isDragover.value = false
  const files = e.dataTransfer.files
  if (files.length > 0) {
    const f = files[0]
    if (f.type !== 'application/pdf') {
      ElMessage.error('只能上传 PDF 文件')
      return
    }
    if (f.size > maxFileSize * 1024 * 1024) {
      ElMessage.error(`文件大小不能超过 ${maxFileSize}MB`)
      return
    }
    file.value = f
    uploadResult.value = null
  }
}

function formatFileSize(size) {
  if (size < 1024) return size + ' B'
  if (size < 1024 * 1024) return (size / 1024).toFixed(2) + ' KB'
  return (size / (1024 * 1024)).toFixed(2) + ' MB'
}

async function handleUpload() {
  if (!file.value) return
  
  uploading.value = true
  uploadProgress.value = 0
  uploadResult.value = null
  
  const formData = new FormData()
  formData.append('file', file.value)
  
  try {
    // 模拟进度（实际应使用 onUploadProgress）
    const interval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += 10
      }
    }, 200)
    
    const response = await api.post('/upload/pdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    clearInterval(interval)
    uploadProgress.value = 100
    uploadStatus.value = 'success'
    progressText.value = '上传完成！'
    
    uploadResult.value = {
      success: true,
      message: `文件已上传，共 ${response.pages} 页`,
      data: response
    }
    
    ElNotification.success({
      title: '上传成功',
      message: `文件已上传，共 ${response.pages} 页`
    })
    
    loadHistory()
  } catch (error) {
    clearInterval(interval)
    uploadProgress.value = 100
    uploadStatus.value = 'exception'
    progressText.value = '上传失败'
    
    uploadResult.value = {
      success: false,
      message: error || '上传失败'
    }
    
    ElMessage.error(error || '上传失败')
  } finally {
    uploading.value = false
  }
}

async function loadHistory() {
  try {
    const response = await api.get('/upload/history')
    uploadHistory.value = response.items || []
  } catch (error) {
    console.error('加载历史失败', error)
  }
}

function goToGenerate(item) {
  router.push({ 
    path: '/generate', 
    query: { fileId: item.id } 
  })
}

loadHistory()
</script>

<style scoped>
.upload-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.upload-card, .history-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.upload-area {
  margin-bottom: 20px;
}

.upload-area.is-dragover {
  background: #f5f7fa;
  border-radius: 8px;
}

.file-info {
  margin: 20px 0;
}

.actions {
  margin: 20px 0;
  text-align: center;
}

.progress-area {
  margin: 20px 0;
}

.progress-text {
  text-align: center;
  color: #909399;
  margin-top: 10px;
}

.result-area {
  margin-top: 20px;
}
</style>
