<template>
  <div class="home-container">
    <el-container>
      <!-- Sidebar -->
      <el-aside width="220px">
        <div class="logo">
          <h2>🍏 AI Comic</h2>
        </div>
        <el-menu
          :default-active="activeMenu"
          router
          class="menu"
        >
          <el-menu-item index="/home">
            <el-icon><House /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/upload">
            <el-icon><Upload /></el-icon>
            <span>上传PDF</span>
          </el-menu-item>
          <el-menu-item index="/generate">
            <el-icon><MagicStick /></el-icon>
            <span>生成漫画</span>
          </el-menu-item>
          <el-menu-item index="/works">
            <el-icon><Folder /></el-icon>
            <span>作品管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <!-- Main Content -->
      <el-container>
        <el-header>
          <div class="header-left">
            <h3>{{ pageTitle }}</h3>
          </div>
          <div class="header-right">
            <el-dropdown @command="handleCommand">
              <span class="user-info">
                <el-icon><User /></el-icon>
                {{ userInfo?.username || '用户' }}
                <el-icon><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                  <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'
import { House, Upload, MagicStick, Folder, User, ArrowDown } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const userInfo = computed(() => userStore.userInfo)
const activeMenu = computed(() => route.path)

const pageTitle = computed(() => {
  const titles = {
    '/home': '首页',
    '/upload': '上传PDF',
    '/generate': '生成漫画',
    '/works': '作品管理'
  }
  return titles[route.path] || '首页'
})

function handleCommand(command) {
  if (command === 'logout') {
    userStore.logout()
    router.push('/login')
  } else if (command === 'profile') {
    ElMessage.info('个人中心开发中')
  }
}

onMounted(() => {
  if (userStore.token && !userStore.userInfo) {
    userStore.getUserProfile()
  }
})
</script>

<style scoped>
.home-container {
  height: 100vh;
}

.el-container {
  height: 100%;
}

.el-aside {
  background: #304156;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #263445;
}

.logo h2 {
  color: #fff;
  font-size: 20px;
}

.menu {
  border-right: none;
  background: #304156;
}

.menu .el-menu-item {
  color: #bfcbd9;
}

.menu .el-menu-item:hover,
.menu .el-menu-item.is-active {
  background: #263445;
  color: #409eff;
}

.el-header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}

.header-left h3 {
  color: #333;
  font-size: 18px;
  font-weight: 500;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #606266;
}

.user-info:hover {
  color: #409eff;
}

.el-main {
  background: #f5f7fa;
  padding: 20px;
}
</style>
