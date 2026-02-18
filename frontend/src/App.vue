<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <div class="header-content">
        <div class="logo">
          <el-icon :size="28" color="#fff"><Reading /></el-icon>
          <span class="logo-text">HN + RSS Reader</span>
        </div>
        <el-menu
          :default-active="$route.path"
          class="nav-menu"
          mode="horizontal"
          background-color="#ff6600"
          text-color="#fff"
          active-text-color="#fff"
          router
        >
          <el-menu-item index="/">
            <el-icon><House /></el-icon>
            <span>全部</span>
          </el-menu-item>
          <el-menu-item index="/hackernews">
            <el-icon><TrendCharts /></el-icon>
            <span>Hacker News</span>
          </el-menu-item>
          <el-menu-item index="/rss">
            <el-icon><Collection /></el-icon>
            <span>RSS Feeds</span>
          </el-menu-item>
        </el-menu>
      </div>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script>
import { House, TrendCharts, Collection, Reading } from '@element-plus/icons-vue'

export default {
  name: 'App',
  setup() {
    return {
      House,
      TrendCharts,
      Collection,
      Reading
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background-color: #f5f7fa;
}

.app-container {
  min-height: 100vh;
}

.app-header {
  background-color: #ff6600;
  padding: 0;
  height: 60px !important;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-text {
  color: white;
  font-size: 1.2rem;
  font-weight: 600;
}
.nav-menu {
  display: flex;
  justify-content: center; /* 菜单在中间 */
  flex: 1;
  border-bottom: none !important;
  background-color: transparent !important;
  padding: 0;
}

/* 每个菜单项平分宽度并居中 */
.nav-menu :deep(.el-menu-item) {
  flex: 1;
  text-align: center;
  font-size: 0.95rem;
  border-bottom: none !important;
}

/* hover 和 active 效果 */
.nav-menu :deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.15) !important;
}

.nav-menu :deep(.el-menu-item.is-active) {
  background-color: rgba(255, 255, 255, 0.2) !important;
  border-bottom: 2px solid white !important;
}

.app-main {
  padding: 0;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}

/* 响应式 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    padding: 10px;
  }
  
  .app-header {
    height: auto !important;
    min-height: 60px;
  }
  
  .nav-menu {
    margin-top: 10px;
  }
  
  .app-main {
    min-height: calc(100vh - 100px);
  }
}
</style>
