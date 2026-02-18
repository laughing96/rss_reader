<template>
  <div class="home-view">
    <el-page-header title="首页" content="全部新闻" />
    
    <el-row :gutter="20" class="content-row">
      <el-col :span="24">
        <div v-loading="loading" class="items-container">
          <el-empty v-if="items.length === 0 && !loading" description="暂无内容" />
          
          <el-timeline v-else>
            <el-timeline-item
              v-for="item in items"
              :key="`${item.type}-${item.id}`"
              :timestamp="formatTime(item.time)"
              placement="top"
            >
              <el-card class="news-card" shadow="hover" :body-style="{ padding: '15px' }">
                <template #header>
                  <div class="card-header">
                    <el-tag :type="item.type === 'hn' ? 'danger' : 'primary'" size="small">
                      <el-icon v-if="item.type === 'hn'"><Lightning /></el-icon>
                      <el-icon v-else><Document /></el-icon>
                      {{ item.type === 'hn' ? 'Hacker News' : 'RSS' }}
                    </el-tag>
                    <span class="source-name">{{ item.source }}</span>
                  </div>
                </template>
                
                <h4 class="news-title">
                  <a :href="item.url" target="_blank" rel="noopener">{{ item.title }}</a>
                </h4>
                
                <p v-if="item.description" class="news-description">
                  {{ truncateText(item.description, 200) }}
                </p>
                
                <div class="news-meta">
                  <el-space>
                    <el-tag v-if="item.author" type="info" size="small" effect="plain">
                      <el-icon><User /></el-icon> {{ item.author }}
                    </el-tag>
                    <el-tag v-if="item.score > 0" type="warning" size="small" effect="plain">
                      <el-icon><StarFilled /></el-icon> {{ item.score }} 分
                    </el-tag>
                  </el-space>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { formatDistanceToNow } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import { Lightning, Document, User, StarFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'HomeView',
  setup() {
    const items = ref([])
    const loading = ref(true)

    const fetchItems = async () => {
      try {
        loading.value = true
        const response = await axios.get('/api/combined?limit=50')
        items.value = response.data
      } catch (err) {
        ElMessage.error('加载失败: ' + err.message)
      } finally {
        loading.value = false
      }
    }

    const formatTime = (time) => {
      try {
        return formatDistanceToNow(new Date(time), { 
          addSuffix: true,
          locale: zhCN 
        })
      } catch {
        return time
      }
    }

    const truncateText = (text, maxLength) => {
      if (!text) return ''
      if (text.length <= maxLength) return text
      return text.substring(0, maxLength) + '...'
    }

    onMounted(() => {
      fetchItems()
      // 每 5 分钟刷新一次
      setInterval(fetchItems, 5 * 60 * 1000)
    })

    return {
      items,
      loading,
      formatTime,
      truncateText,
      Lightning,
      Document,
      User,
      StarFilled
    }
  }
}
</script>

<style scoped>
.home-view {
  padding: 20px;
}

.content-row {
  margin-top: 20px;
}

.items-container {
  min-height: 400px;
}

.news-card {
  margin-bottom: 10px;
  border-left: 4px solid #409eff;
}

.news-card:has(.el-tag--danger) {
  border-left-color: #f56c6c;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.source-name {
  color: #909399;
  font-size: 14px;
}

.news-title {
  margin: 0 0 10px 0;
  font-size: 16px;
  line-height: 1.5;
}

.news-title a {
  color: #303133;
  text-decoration: none;
  transition: color 0.3s;
}

.news-title a:hover {
  color: #409eff;
}

.news-description {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  margin: 0 0 10px 0;
}

.news-meta {
  margin-top: 10px;
}

:deep(.el-timeline-item__timestamp) {
  color: #909399;
  font-size: 13px;
}
</style>
