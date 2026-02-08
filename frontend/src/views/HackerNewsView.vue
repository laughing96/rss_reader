<template>
  <div class="hn-view">
    <h2 class="page-title">🔥 Hacker News 热门</h2>
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    <div v-else class="items-list">
      <article 
        v-for="(story, index) in stories" 
        :key="story.id"
        class="news-item"
      >
        <div class="rank">{{ index + 1 }}</div>
        <div class="content">
          <h3 class="item-title">
            <a :href="story.url || `https://news.ycombinator.com/item?id=${story.hn_id}`" 
               target="_blank" rel="noopener">
              {{ story.title }}
            </a>
          </h3>
          <div class="item-meta">
            <span class="score">⭐ {{ story.score }} 分</span>
            <span class="author">👤 {{ story.by }}</span>
            <span class="comments">
              💬 {{ story.descendants }} 评论
            </span>
            <span class="time">🕐 {{ formatTime(story.time) }}</span>
          </div>
        </div>
      </article>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { formatDistanceToNow } from 'date-fns'
import { zhCN } from 'date-fns/locale'

export default {
  name: 'HackerNewsView',
  setup() {
    const stories = ref([])
    const loading = ref(true)
    const error = ref(null)

    const fetchStories = async () => {
      try {
        loading.value = true
        error.value = null
        const response = await axios.get('/api/hn/stories?limit=30')
        stories.value = response.data
      } catch (err) {
        error.value = '加载失败: ' + err.message
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
      error,
      formatTime
    }
  }
}
</script>

<style scoped>
.hn-view {
  padding: 1rem 0;
}

.page-title {
  margin-bottom: 1.5rem;
  color: #ff6600;
  font-size: 1.5rem;
}

.loading, .error {
  text-align: center;
  padding: 3rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #ff6600;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  color: #d32f2f;
  background: #ffebee;
  border-radius: 8px;
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.news-item {
  display: flex;
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.news-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.rank {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ff6600;
  color: white;
  font-weight: bold;
  border-radius: 50%;
  margin-right: 1rem;
  flex-shrink: 0;
}

.content {
  flex: 1;
}

.item-title {
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
  line-height: 1.4;
}

.item-title a {
  color: #333;
  text-decoration: none;
}

.item-title a:hover {
  color: #ff6600;
}

.item-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 0.85rem;
  color: #666;
}

.score {
  color: #ff6600;
  font-weight: 600;
}
</style>
