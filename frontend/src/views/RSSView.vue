<template>
  <div class="rss-view">
    <h2 class="page-title">📡 RSS 订阅</h2>
    
    <!-- 文件夹管理区域 -->
    <div class="folders-section">
      <div class="section-header">
        <button @click="showFolderForm = !showFolderForm" class="btn-toggle folder-btn">
          {{ showFolderForm ? '取消' : '📁 新建文件夹' }}
        </button>
      </div>
      <form v-if="showFolderForm" @submit.prevent="createFolder" class="folder-form">
        <input 
          v-model="newFolder.name" 
          placeholder="文件夹名称" 
          required
        />
        <select v-model="newFolder.parent">
          <option :value="null">根文件夹</option>
          <option v-for="folder in flatFolders" :key="folder.id" :value="folder.id">
            {{ '  '.repeat(folder.depth) }}{{ folder.name }}
          </option>
        </select>
        <button type="submit" :disabled="creatingFolder">
          {{ creatingFolder ? '创建中...' : '创建' }}
        </button>
      </form>
    </div>

    <!-- 导入 OPML 区域 -->
    <div class="import-section">
      <div class="import-buttons">
        <button @click="showImportForm = !showImportForm" class="btn-toggle import-btn">
          {{ showImportForm ? '取消' : '📁 导入 OPML 文件' }}
        </button>
      </div>
      <form v-if="showImportForm" @submit.prevent="importOPML" class="import-form">
        <div class="file-input-wrapper">
          <input
            ref="fileInput"
            type="file"
            accept=".opml,.xml"
            @change="handleFileSelect"
            class="file-input"
          />
          <p class="file-hint">选择 .opml 或 .xml 文件 (支持包含文件夹结构)</p>
        </div>
        <button type="submit" :disabled="!selectedFile || importing" class="btn-import">
          {{ importing ? '导入中...' : '开始导入' }}
        </button>
        <div v-if="importResult" class="import-result" :class="{ success: importResult.success, error: !importResult.success }">
          <p><strong>{{ importResult.message }}</strong></p>
          <p v-if="importResult.details">
            总计: {{ importResult.details.total_found }} | 
            成功: {{ importResult.added }} | 
            跳过: {{ importResult.skipped }} | 
            失败: {{ importResult.failed }}
          </p>
          <ul v-if="importResult.details && importResult.details.failed.length" class="failed-list">
            <li v-for="(fail, index) in importResult.details.failed" :key="index">
              {{ fail.feed }}: {{ fail.error }}
            </li>
          </ul>
        </div>
      </form>
    </div>

    <!-- 添加 Feed 表单 -->
    <div class="add-feed-section">
      <button @click="showAddForm = !showAddForm" class="btn-toggle">
        {{ showAddForm ? '取消' : '+ 添加 RSS Feed' }}
      </button>
      <form v-if="showAddForm" @submit.prevent="addFeed" class="add-feed-form">
        <input 
          v-model="newFeed.title" 
          placeholder="Feed 名称" 
          required
        />
        <input 
          v-model="newFeed.url" 
          placeholder="网站 URL" 
          required
        />
        <input 
          v-model="newFeed.feed_url" 
          placeholder="RSS Feed URL" 
          required
        />
        <textarea 
          v-model="newFeed.description" 
          placeholder="描述 (可选)"
          rows="2"
        ></textarea>
        <select v-model="newFeed.folder">
          <option :value="null">不放入文件夹</option>
          <option v-for="folder in flatFolders" :key="folder.id" :value="folder.id">
            {{ '  '.repeat(folder.depth) }}{{ folder.name }}
          </option>
        </select>
        <button type="submit" :disabled="adding">
          {{ adding ? '添加中...' : '添加' }}
        </button>
      </form>
    </div>

    <!-- Feeds 列表 -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    <div v-else class="content-wrapper">
      <!-- Feed 选择器 -->
      <div class="feeds-sidebar">
        <h3>订阅源</h3>
        
        <!-- 文件夹树形结构 -->
        <div class="folder-tree">
          <div 
            v-for="folder in folders" 
            :key="folder.id"
            class="folder-item"
          >
            <div class="folder-header">
              <span 
                class="folder-toggle"
                @click="toggleFolder(folder.id)"
              >
                {{ isExpanded(folder.id) ? '▼' : '▶' }}
              </span>
              <button 
                :class="['folder-name', { active: selectedFolder === folder.id }]"
                @click="selectFolder(folder.id)"
              >
                📁 {{ folder.name }}
              </button>
              <span class="folder-count">({{ folder.feed_count }})</span>
              <span class="folder-actions">
                <span class="edit-btn" @click.stop="editFolder(folder)">✏️</span>
                <span class="delete-btn" @click.stop="deleteFolder(folder.id)">×</span>
              </span>
            </div>
            
            <!-- 文件夹内的feeds -->
            <div v-if="isExpanded(folder.id)" class="folder-feeds">
              <button 
                v-for="feed in getFeedsInFolder(folder.id)" 
                :key="feed.id"
                :class="['feed-btn', { active: selectedFeed === feed.id }]"
                @click="selectFeed(feed.id)"
              >
                <span class="feed-name">📄 {{ feed.title }}</span>
                <span class="delete-btn" @click.stop="deleteFeed(feed.id)">×</span>
              </button>
            </div>
          </div>
        </div>
        
        <!-- 未分类 Feeds -->
        <div class="folder-item">
          <div class="folder-header">
            <span 
              class="folder-toggle"
              @click="toggleFolder('uncategorized')"
            >
              {{ isExpanded('uncategorized') ? '▼' : '▶' }}
            </span>
            <button 
              :class="['folder-name', { active: selectedFolder === 'uncategorized' }]"
              @click="selectFolder('uncategorized')"
            >
              📁 未分类
            </button>
            <span class="folder-count">({{ uncategorizedFeeds.length }})</span>
          </div>
          
          <div v-if="isExpanded('uncategorized')" class="folder-feeds">
            <button 
              v-for="feed in uncategorizedFeeds" 
              :key="feed.id"
              :class="['feed-btn', { active: selectedFeed === feed.id }]"
              @click="selectFeed(feed.id)"
            >
              <span class="feed-name">📄 {{ feed.title }}</span>
              <span class="delete-btn" @click.stop="deleteFeed(feed.id)">×</span>
            </button>
          </div>
        </div>
        
        <!-- 全部 RSS -->
        <div class="folder-item">
          <button 
            :class="['feed-btn all-feeds', { active: selectedFeed === null && selectedFolder === null }]"
            @click="selectFeed(null)"
          >
            📑 全部 RSS ({{ feeds.length }})
          </button>
        </div>
      </div>

      <!-- Items 列表 -->
      <div class="items-section">
        <div class="items-header">
          <h3>{{ currentFeedTitle }}</h3>
          <button v-if="selectedFeed" @click="showMoveModal = true" class="btn-move">
            移动到文件夹
          </button>
          <button @click="refreshItems" :disabled="refreshing" class="btn-refresh">
            {{ refreshing ? '刷新中...' : '↻ 刷新' }}
          </button>
        </div>
        <div v-if="itemsLoading" class="loading">
          <div class="spinner"></div>
        </div>
        <div v-else-if="items.length === 0" class="empty">
          暂无内容
        </div>
        <div v-else class="items-list">
          <article 
            v-for="item in items" 
            :key="item.id"
            class="news-item"
          >
            <h3 class="item-title">
              <a :href="item.link" target="_blank" rel="noopener">{{ item.title }}</a>
            </h3>
            <p v-if="item.description" class="item-description">
              {{ truncateText(stripHtml(item.description), 200) }}
            </p>
            <div class="item-meta">
              <span class="time">🕐 {{ formatTime(item.published_at || item.created_at) }}</span>
            </div>
          </article>
        </div>
      </div>
    </div>
    
    <!-- 编辑文件夹模态框 -->
    <div v-if="showEditFolderModal" class="modal-overlay" @click.self="showEditFolderModal = false">
      <div class="modal">
        <h3>编辑文件夹</h3>
        <form @submit.prevent="updateFolder">
          <input 
            v-model="editingFolder.name" 
            placeholder="文件夹名称" 
            required
          />
          <select v-model="editingFolder.parent">
            <option :value="null">根文件夹</option>
            <option v-for="folder in flatFolders.filter(f => f.id !== editingFolder.id)" :key="folder.id" :value="folder.id">
              {{ '  '.repeat(folder.depth) }}{{ folder.name }}
            </option>
          </select>
          <div class="modal-actions">
            <button type="submit" class="btn-primary">保存</button>
            <button type="button" @click="showEditFolderModal = false" class="btn-secondary">取消</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- 移动Feed模态框 -->
    <div v-if="showMoveModal" class="modal-overlay" @click.self="showMoveModal = false">
      <div class="modal">
        <h3>移动 Feed 到文件夹</h3>
        <select v-model="targetFolderId">
          <option :value="null">不放入文件夹</option>
          <option v-for="folder in flatFolders" :key="folder.id" :value="folder.id">
            {{ '  '.repeat(folder.depth) }}{{ folder.name }}
          </option>
        </select>
        <div class="modal-actions">
          <button @click="moveFeed" class="btn-primary">移动</button>
          <button @click="showMoveModal = false" class="btn-secondary">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { formatDistanceToNow } from 'date-fns'
import { zhCN } from 'date-fns/locale'

export default {
  name: 'RSSView',
  setup() {
    const feeds = ref([])
    const folders = ref([])
    const items = ref([])
    const loading = ref(true)
    const itemsLoading = ref(false)
    const error = ref(null)
    const selectedFeed = ref(null)
    const selectedFolder = ref(null)
    const showAddForm = ref(false)
    const adding = ref(false)
    const refreshing = ref(false)
    const showImportForm = ref(false)
    const importing = ref(false)
    const selectedFile = ref(null)
    const importResult = ref(null)
    const fileInput = ref(null)
    
    // 文件夹管理
    const showFolderForm = ref(false)
    const creatingFolder = ref(false)
    const expandedFolders = ref(['uncategorized'])
    const showEditFolderModal = ref(false)
    const editingFolder = ref({ id: null, name: '', parent: null })
    const showMoveModal = ref(false)
    const targetFolderId = ref(null)
    
    const newFolder = ref({
      name: '',
      parent: null
    })
    
    const newFeed = ref({
      title: '',
      url: '',
      feed_url: '',
      description: '',
      folder: null
    })

    const handleFileSelect = (event) => {
      selectedFile.value = event.target.files[0]
      importResult.value = null
    }

    const importOPML = async () => {
      if (!selectedFile.value) return
      
      try {
        importing.value = true
        importResult.value = null
        
        const formData = new FormData()
        formData.append('file', selectedFile.value)
        
        const response = await axios.post('/api/rss/feeds/import', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        importResult.value = {
          success: true,
          message: response.data.message,
          added: response.data.added,
          skipped: response.data.skipped,
          failed: response.data.failed,
          details: response.data.details
        }
        
        await fetchFeeds()
        await fetchFolders()
        
        selectedFile.value = null
        if (fileInput.value) {
          fileInput.value.value = ''
        }
      } catch (err) {
        importResult.value = {
          success: false,
          message: '导入失败: ' + (err.response?.data?.error || err.message)
        }
      } finally {
        importing.value = false
      }
    }

    const currentFeedTitle = computed(() => {
      if (selectedFolder.value) {
        if (selectedFolder.value === 'uncategorized') {
          return '未分类 Feeds'
        }
        const folder = folders.value.find(f => f.id === selectedFolder.value)
        return folder ? `📁 ${folder.name}` : '全部 RSS'
      }
      if (selectedFeed.value === null) return '全部 RSS'
      const feed = feeds.value.find(f => f.id === selectedFeed.value)
      return feed ? feed.title : '全部 RSS'
    })
    
    // 将文件夹扁平化用于下拉选择
    const flattenFolders = (foldersList, depth = 0) => {
      let result = []
      foldersList.forEach(folder => {
        result.push({ ...folder, depth })
        if (folder.children && folder.children.length > 0) {
          result = result.concat(flattenFolders(folder.children, depth + 1))
        }
      })
      return result
    }
    
    const flatFolders = computed(() => {
      return flattenFolders(folders.value)
    })
    
    // 获取文件夹内的feeds
    const getFeedsInFolder = (folderId) => {
      return feeds.value.filter(feed => feed.folder === folderId)
    }
    
    // 未分类的feeds
    const uncategorizedFeeds = computed(() => {
      return feeds.value.filter(feed => !feed.folder)
    })

    const fetchFeeds = async () => {
      try {
        loading.value = true
        error.value = null
        const response = await axios.get('/api/rss/feeds')
        feeds.value = response.data
      } catch (err) {
        error.value = '加载失败: ' + err.message
      } finally {
        loading.value = false
      }
    }
    
    const fetchFolders = async () => {
      try {
        const response = await axios.get('/api/rss/folders')
        folders.value = response.data
      } catch (err) {
        console.error('Failed to fetch folders:', err)
      }
    }

    const fetchItems = async () => {
      try {
        itemsLoading.value = true
        let params = {}
        
        if (selectedFolder.value) {
          if (selectedFolder.value === 'uncategorized') {
            params = { feed: null }
          } else {
            params = { folder: selectedFolder.value }
          }
        } else if (selectedFeed.value) {
          params = { feed: selectedFeed.value }
        }
        
        const response = await axios.get('/api/rss/items', { params })
        items.value = response.data
      } catch (err) {
        console.error('Failed to fetch items:', err)
      } finally {
        itemsLoading.value = false
      }
    }
    
    const toggleFolder = (folderId) => {
      const index = expandedFolders.value.indexOf(folderId)
      if (index > -1) {
        expandedFolders.value.splice(index, 1)
      } else {
        expandedFolders.value.push(folderId)
      }
    }
    
    const isExpanded = (folderId) => {
      return expandedFolders.value.includes(folderId)
    }
    
    const selectFolder = (folderId) => {
      selectedFolder.value = folderId
      selectedFeed.value = null
      fetchItems()
    }

    const selectFeed = (feedId) => {
      selectedFeed.value = feedId
      selectedFolder.value = null
      fetchItems()
    }
    
    const createFolder = async () => {
      try {
        creatingFolder.value = true
        await axios.post('/api/rss/folders', newFolder.value)
        newFolder.value = { name: '', parent: null }
        showFolderForm.value = false
        await fetchFolders()
      } catch (err) {
        alert('创建文件夹失败: ' + err.message)
      } finally {
        creatingFolder.value = false
      }
    }
    
    const editFolder = (folder) => {
      editingFolder.value = {
        id: folder.id,
        name: folder.name,
        parent: folder.parent
      }
      showEditFolderModal.value = true
    }
    
    const updateFolder = async () => {
      try {
        await axios.put(`/api/rss/folders/${editingFolder.value.id}`, {
          name: editingFolder.value.name,
          parent: editingFolder.value.parent
        })
        showEditFolderModal.value = false
        await fetchFolders()
        await fetchFeeds()
      } catch (err) {
        alert('更新文件夹失败: ' + err.message)
      }
    }
    
    const deleteFolder = async (folderId) => {
      if (!confirm('确定要删除这个文件夹吗？文件夹内的feeds将变为未分类。')) return
      try {
        await axios.delete(`/api/rss/folders/${folderId}`)
        if (selectedFolder.value === folderId) {
          selectedFolder.value = null
          selectedFeed.value = null
        }
        await fetchFolders()
        await fetchFeeds()
      } catch (err) {
        alert('删除文件夹失败: ' + err.message)
      }
    }
    
    const moveFeed = async () => {
      if (!selectedFeed.value) return
      try {
        await axios.post(`/api/rss/feeds/${selectedFeed.value}/move`, {
          folder: targetFolderId.value
        })
        showMoveModal.value = false
        targetFolderId.value = null
        await fetchFeeds()
      } catch (err) {
        alert('移动失败: ' + err.message)
      }
    }

    const addFeed = async () => {
      try {
        adding.value = true
        await axios.post('/api/rss/feeds', newFeed.value)
        newFeed.value = { title: '', url: '', feed_url: '', description: '', folder: null }
        showAddForm.value = false
        await fetchFeeds()
        await fetchItems()
      } catch (err) {
        alert('添加失败: ' + err.message)
      } finally {
        adding.value = false
      }
    }

    const deleteFeed = async (feedId) => {
      if (!confirm('确定要删除这个 RSS 订阅吗？')) return
      try {
        await axios.delete(`/api/rss/feeds/${feedId}`)
        if (selectedFeed.value === feedId) {
          selectedFeed.value = null
        }
        await fetchFeeds()
        await fetchItems()
      } catch (err) {
        alert('删除失败: ' + err.message)
      }
    }

    const refreshItems = async () => {
      try {
        refreshing.value = true
        if (selectedFeed.value) {
          await axios.post(`/api/rss/feeds/${selectedFeed.value}/refresh`)
        }
        await fetchItems()
      } catch (err) {
        console.error('Refresh failed:', err)
      } finally {
        refreshing.value = false
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

    const stripHtml = (html) => {
      if (!html) return ''
      const tmp = document.createElement('DIV')
      tmp.innerHTML = html
      return tmp.textContent || tmp.innerText || ''
    }

    onMounted(() => {
      fetchFolders()
      fetchFeeds().then(() => {
        fetchItems()
      })
    })

    return {
      feeds,
      folders,
      flatFolders,
      items,
      loading,
      itemsLoading,
      error,
      selectedFeed,
      selectedFolder,
      showAddForm,
      adding,
      refreshing,
      showImportForm,
      importing,
      selectedFile,
      importResult,
      fileInput,
      newFeed,
      showFolderForm,
      creatingFolder,
      newFolder,
      showEditFolderModal,
      editingFolder,
      showMoveModal,
      targetFolderId,
      uncategorizedFeeds,
      currentFeedTitle,
      selectFeed,
      selectFolder,
      addFeed,
      deleteFeed,
      refreshItems,
      formatTime,
      truncateText,
      stripHtml,
      handleFileSelect,
      importOPML,
      createFolder,
      editFolder,
      updateFolder,
      deleteFolder,
      moveFeed,
      toggleFolder,
      isExpanded,
      getFeedsInFolder
    }
  }
}
</script>

<style scoped>
.rss-view {
  padding: 1rem 0;
}

.page-title {
  margin-bottom: 1.5rem;
  color: #2196f3;
  font-size: 1.5rem;
}

.folders-section {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.section-header {
  display: flex;
  gap: 0.5rem;
}

.folder-btn {
  background: #9c27b0;
}

.folder-btn:hover {
  background: #7b1fa2;
}

.folder-form {
  margin-top: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.folder-form input,
.folder-form select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.folder-form button {
  padding: 0.5rem 1rem;
  background: #9c27b0;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.folder-form button:disabled {
  background: #ccc;
}

.add-feed-section {
  margin-bottom: 1.5rem;
}

.btn-toggle {
  padding: 0.5rem 1rem;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-toggle:hover {
  background: #1976d2;
}

.add-feed-form {
  margin-top: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.add-feed-form input,
.add-feed-form textarea,
.add-feed-form select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.add-feed-form button {
  padding: 0.5rem 1rem;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.add-feed-form button:disabled {
  background: #ccc;
}

.loading, .error, .empty {
  text-align: center;
  padding: 3rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #2196f3;
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

.content-wrapper {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 1rem;
}

@media (max-width: 768px) {
  .content-wrapper {
    grid-template-columns: 1fr;
  }
}

.feeds-sidebar {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  height: fit-content;
}

.feeds-sidebar h3 {
  margin-bottom: 1rem;
  color: #333;
}

.folder-tree {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.folder-item {
  display: flex;
  flex-direction: column;
}

.folder-header {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.3rem;
}

.folder-toggle {
  cursor: pointer;
  user-select: none;
  font-size: 0.8rem;
  width: 20px;
  text-align: center;
}

.folder-name {
  flex: 1;
  padding: 0.3rem 0.5rem;
  background: transparent;
  border: none;
  cursor: pointer;
  text-align: left;
  font-size: 0.9rem;
  border-radius: 4px;
  transition: background 0.2s;
}

.folder-name:hover {
  background: #e3f2fd;
}

.folder-name.active {
  background: #2196f3;
  color: white;
}

.folder-count {
  font-size: 0.8rem;
  color: #666;
}

.folder-actions {
  display: flex;
  gap: 0.2rem;
}

.edit-btn,
.delete-btn {
  padding: 0.2rem 0.4rem;
  cursor: pointer;
  border-radius: 3px;
  font-size: 0.8rem;
}

.edit-btn:hover {
  background: #e3f2fd;
}

.delete-btn {
  color: #f44336;
}

.delete-btn:hover {
  background: #ffebee;
}

.folder-feeds {
  margin-left: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.feed-btn {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.3rem 0.5rem;
  background: #f5f5f5;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  text-align: left;
  transition: background 0.2s;
  font-size: 0.85rem;
}

.feed-btn:hover {
  background: #e0e0e0;
}

.feed-btn.active {
  background: #2196f3;
  color: white;
}

.feed-btn.all-feeds {
  background: #4caf50;
  color: white;
}

.feed-btn.all-feeds:hover {
  background: #45a049;
}

.feed-btn.all-feeds.active {
  background: #2e7d32;
}

.feed-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.items-section {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.items-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  gap: 0.5rem;
}

.items-header h3 {
  color: #333;
  flex: 1;
}

.btn-refresh {
  padding: 0.3rem 0.8rem;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}

.btn-refresh:disabled {
  background: #ccc;
}

.btn-move {
  padding: 0.3rem 0.8rem;
  background: #ff9800;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}

.btn-move:hover {
  background: #f57c00;
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.news-item {
  padding: 1rem;
  border-bottom: 1px solid #eee;
  transition: background 0.2s;
}

.news-item:hover {
  background: #f5f5f5;
}

.news-item:last-child {
  border-bottom: none;
}

.item-title {
  font-size: 1rem;
  margin-bottom: 0.5rem;
}

.item-title a {
  color: #333;
  text-decoration: none;
}

.item-title a:hover {
  color: #2196f3;
}

.item-description {
  color: #666;
  font-size: 0.85rem;
  line-height: 1.4;
  margin-bottom: 0.5rem;
}

.item-meta {
  font-size: 0.8rem;
  color: #999;
}

.import-section {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.import-buttons {
  display: flex;
  gap: 0.5rem;
}

.import-btn {
  background: #ff9800;
}

.import-btn:hover {
  background: #f57c00;
}

.import-form {
  margin-top: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.file-input-wrapper {
  margin-bottom: 1rem;
}

.file-input {
  width: 100%;
  padding: 0.5rem;
  border: 2px dashed #ccc;
  border-radius: 4px;
  cursor: pointer;
}

.file-hint {
  margin-top: 0.5rem;
  font-size: 0.85rem;
  color: #666;
}

.btn-import {
  padding: 0.5rem 1rem;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-import:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.import-result {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 4px;
}

.import-result.success {
  background: #e8f5e9;
  color: #2e7d32;
}

.import-result.error {
  background: #ffebee;
  color: #c62828;
}

.failed-list {
  margin-top: 0.5rem;
  padding-left: 1.5rem;
  font-size: 0.85rem;
}

.failed-list li {
  margin-bottom: 0.25rem;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

.modal h3 {
  margin-bottom: 1rem;
  color: #333;
}

.modal input,
.modal select {
  width: 100%;
  padding: 0.5rem;
  margin-bottom: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.modal-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.btn-primary {
  padding: 0.5rem 1rem;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary:hover {
  background: #1976d2;
}

.btn-secondary {
  padding: 0.5rem 1rem;
  background: #e0e0e0;
  color: #333;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-secondary:hover {
  background: #d0d0d0;
}
</style>
