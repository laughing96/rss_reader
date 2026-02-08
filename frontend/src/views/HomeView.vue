<template>
  <div class="home-view">
    <h2 class="page-title">📰 全部新闻</h2>
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    <div v-else class="items-list">
      <article 
        v-for="item in items" 
        :key="`${item.type}-${item.id}`"
        :class="['news-item', item.type]"
      >
        <div class="item-header">
          <span class="source-badge" :class="item.type">
            {{ item.type === 'hn' ? '🔥 HN' : '📡 RSS' }}
          </span>
          <span class="source-name">{{ item.source }}</span>
        </div>
        <h3 class="item-title">
          <a :href="item.url" target="_blank" rel="noopener">{{ item.title }}</a>
        </h3>
        <p v-if="item.description" class="item-description">
          {{ truncateText(item.description, 200) }}
        </p>
        <div class="item-meta">
          <span v-if="item.author" class="author">👤 {{ item.author }}</span>
          <span v-if="item.score > 0" class="score">⭐ {{ item.score }} 分</span>
          <span class="time">🕐 {{ formatTime(item.time) }}</span>
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
  name: 'HomeView',
  setup() {
    const items = ref([])
    const loading = ref(true)
    const error = ref(null)

    const fetchItems = async () => {
      try {
        loading.value = true
        error.value = null
        const response = await axios.get('/api/combined?limit=50')
        items.value = response.data
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
      error,
      formatTime,
      truncateText
    }
  }
}
</script>

<style scoped>
.home-view {
  padding: 1rem 0;
}

.page-title {
  margin-bottom: 1.5rem;
  color: #333;
  font-size: 1.5rem;
}

.loading {
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
  text-align: center;
  padding: 2rem;
  color: #d32f2f;
  background: #ffebee;
  border-radius: 8px;
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.news-item {
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

.news-item.hn {
  border-left: 4px solid #ff6600;
}

.news-item.rss {
  border-left: 4px solid #2196f3;
}

.item-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.source-badge {
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.source-badge.hn {
  background: #fff3e0;
  color: #e65100;
}

.source-badge.rss {
  background: #e3f2fd;
  color: #1565c0;
}

.source-name {
  font-size: 0.85rem;
  color: #666;
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

.item-description {
  color: #666;
  font-size: 0.9rem;
  line-height: 1.5;
  margin-bottom: 0.5rem;
}

.item-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.85rem;
  color: #999;
}
</style>
