<template>
  <div class="works-container">
    <!-- Filter -->
    <el-card class="filter-card">
      <el-form inline>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable>
            <el-option label="全部" value="" />
            <el-option label="处理中" value="processing" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadWorks">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- Works List -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的作品</span>
          <span class="total">共 {{ total }} 个作品</span>
        </div>
      </template>
      
      <el-table 
        :data="works" 
        style="width: 100%"
        v-loading="loading"
      >
        <el-table-column label="缩略图" width="120">
          <template #default="{ row }">
            <el-image 
              v-if="row.thumbnail"
              :src="row.thumbnail"
              fit="cover"
              class="thumbnail"
              :preview-src-list="[row.thumbnail]"
            />
            <div v-else class="no-image">
              <el-icon><Picture /></el-icon>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="name" label="作品名称" min-width="200">
          <template #default="{ row }">
            <el-link type="primary" @click="viewDetail(row)">
              {{ row.name }}
            </el-link>
          </template>
        </el-table-column>
        
        <el-table-column prop="source_file" label="源文件" min-width="150" />
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="pages" label="页数" width="80" />
        
        <el-table-column prop="progress" label="进度" width="120">
          <template #default="{ row }">
            <el-progress 
              v-if="row.status === 'processing'" 
              :percentage="row.progress" 
              :stroke-width="10"
            />
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="180" />
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button 
              size="small" 
              type="primary" 
              :disabled="row.status !== 'completed'"
              @click="downloadWork(row)"
            >
              下载
            </el-button>
            <el-button 
              size="small" 
              :disabled="row.status !== 'completed'"
              @click="regenerate(row)"
            >
              重新生成
            </el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click="deleteWork(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- Pagination -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadWorks"
          @current-change="loadWorks"
        />
      </div>
    </el-card>
    
    <!-- Detail Dialog -->
    <el-dialog
      v-model="detailVisible"
      title="作品详情"
      width="80%"
    >
      <div v-if="currentWork" class="work-detail">
        <el-row :gutter="20">
          <el-col :span="12">
            <h4>源文件</h4>
            <el-image 
              v-if="currentWork.source_image"
              :src="currentWork.source_image"
              fit="contain"
              class="detail-image"
            />
          </el-col>
          <el-col :span="12">
            <h4>生成结果</h4>
            <el-image 
              v-if="currentWork.result_image"
              :src="currentWork.result_image"
              fit="contain"
              class="detail-image"
            />
          </el-col>
        </el-row>
        
        <el-descriptions :column="2" border style="margin-top: 20px">
          <el-descriptions-item label="作品名称">{{ currentWork.name }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ getStatusText(currentWork.status) }}</el-descriptions-item>
          <el-descriptions-item label="页数">{{ currentWork.pages }}</el-descriptions-item>
          <el-descriptions-item label="AI 模型">{{ currentWork.model_name }}</el-descriptions-item>
          <el-descriptions-item label="风格">{{ currentWork.style }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentWork.created_at }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import { Picture } from '@element-plus/icons-vue'
import api from '../api'

const router = useRouter()

const loading = ref(false)
const works = ref([])
const total = ref(0)
const filters = reactive({
  status: ''
})
const pagination = reactive({
  page: 1,
  pageSize: 10
})

const detailVisible = ref(false)
const currentWork = ref(null)

onMounted(() => {
  loadWorks()
})

async function loadWorks() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...filters
    }
    
    // Remove empty filters
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null) {
        delete params[key]
      }
    })
    
    const response = await api.get('/works', { params })
    works.value = response.items || []
    total.value = response.total || 0
  } catch (error) {
    ElMessage.error('加载作品列表失败')
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filters.status = ''
  pagination.page = 1
  loadWorks()
}

function getStatusType(status) {
  const types = {
    processing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return types[status] || 'info'
}

function getStatusText(status) {
  const texts = {
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return texts[status] || '未知'
}

function viewDetail(row) {
  currentWork.value = row
  detailVisible.value = true
}

async function downloadWork(row) {
  try {
    const response = await api.get(`/works/${row.id}/download`, {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = `${row.name}.zip`
    link.click()
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('下载成功')
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

function regenerate(row) {
  router.push({
    path: '/generate',
    query: { fileId: row.source_file_id, regenerate: row.id }
  })
}

async function deleteWork(row) {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个作品吗？此操作不可恢复。',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await api.delete(`/works/${row.id}`)
    ElMessage.success('删除成功')
    loadWorks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}
</script>

<style scoped>
.works-container {
  min-height: 100%;
}

.filter-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.total {
  color: #909399;
  font-size: 14px;
}

.thumbnail {
  width: 80px;
  height: 60px;
  border-radius: 4px;
}

.no-image {
  width: 80px;
  height: 60px;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  color: #909399;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.detail-image {
  width: 100%;
  max-height: 300px;
}
</style>
