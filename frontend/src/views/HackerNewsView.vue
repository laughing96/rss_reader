<template>
  <div class="hn-view">
    <el-page-header title="首页" content="Hacker News 热门" />
    
    <el-row :gutter="20" class="content-row">
      <el-col :span="24">
        <div v-loading="loading" class="items-container">
          <el-empty v-if="stories.length === 0 && !loading" description="暂无内容" />
          
          <el-card 
            v-for="(story, index) in stories" 
            :key="story.id"
            class="story-card"
            shadow="hover"
            :body-style="{ padding: '15px' }"
          >
            <div class="story-content">
              <el-avatar 
                :size="40" 
                :class="['rank-avatar', index < 3 ? 'top-rank' : '']"
              >
                {{ index + 1 }}
              </el-avatar>
              
              <div class="story-info">
                <h4 class="story-title">
                  <a :href="story.url || `https://news.ycombinator.com/item?id=${story.hn_id}`" 
                     target="_blank" rel="noopener">
                    {{ story.title }}
                  </a>
                </h4>
                
                <div class="story-meta">
                  <el-space wrap>
                    <el-tag type="danger" size="small" effect="plain">
                      <el-icon><Star /></el-icon> {{ story.score }} 分
                    </el-tag>
                    <el-tag type="info" size="small" effect="plain">
                      <el-icon><User /></el-icon> {{ story.by }}
                    </el-tag>
                    <el-tag type="success" size="small" effect="plain">
                      <el-icon><ChatDotRound /></el-icon> {{ story.descendants }} 评论
                    </el-tag>
                    <el-tag type="warning" size="small" effect="plain">
                      <el-icon><Timer /></el-icon> {{ formatTime(story.time) }}
                    </el-tag>
                  </el-space>
                </div>
              </div>
            </div>
          </el-card>
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
import { Star, User, ChatDotRound, Timer } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'HackerNewsView',
  setup() {
    const stories = ref([])
    const loading = ref(true)

    const fetchStories = async () => {
      try {
        loading.value = true
        const response = await axios.get('/api/hn/stories?limit=30')
        stories.value = response.data
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

    onMounted(() => {
      fetchStories()
    })

    return {
      stories,
      loading,
      formatTime,
      Star,
      User,
      ChatDotRound,
      Timer
    }
  }
}
</script>

<style scoped>
.hn-view {
  padding: 20px;
}

.content-row {
  margin-top: 20px;
}

.items-container {
  min-height: 400px;
}

.story-card {
  margin-bottom: 10px;
  transition: all 0.3s;
}

.story-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.story-content {
  display: flex;
  align-items: flex-start;
  gap: 15px;
}

.rank-avatar {
  background-color: #909399;
  color: white;
  font-weight: bold;
  flex-shrink: 0;
}

.rank-avatar.top-rank {
  background-color: #ff6600;
}

.story-info {
  flex: 1;
}

.story-title {
  margin: 0 0 10px 0;
  font-size: 16px;
  line-height: 1.5;
}

.story-title a {
  color: #303133;
  text-decoration: none;
  transition: color 0.3s;
}

.story-title a:hover {
  color: #ff6600;
}

.story-meta {
  margin-top: 8px;
}
</style>
