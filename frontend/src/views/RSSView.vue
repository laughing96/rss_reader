<template>
    <div class="rss-view">
        <el-page-header title="返回" content="RSS 订阅管理" />

        <!-- 操作按钮区域 -->
        <el-row :gutter="20" class="action-area">
            <el-col :span="24">
                <el-button type="primary" :icon="FolderAdd" @click="showFolderDialog = true">
                    新建文件夹
                </el-button>
                <el-button type="success" :icon="Plus" @click="showAddDialog = true">
                    添加 RSS Feed
                </el-button>
                <el-button type="warning" :icon="Upload" @click="showImportDialog = true">
                    导入 OPML
                </el-button>
            </el-col>
        </el-row>

        <!-- 主内容区域 -->
        <el-row :gutter="20" class="main-content">
            <!-- 左侧文件夹和Feed列表 -->
            <el-col :xs="24" :sm="24" :md="8" :lg="6">
                <el-card class="folder-card" :body-style="{ padding: '10px' }">
                    <template #header>
                        <div class="card-header">
                            <span><el-icon>
                                    <Folder />
                                </el-icon>
                                订阅源</span>
                            <el-tag type="info" size="small">{{ feeds.length }}</el-tag>
                        </div>
                    </template>

                    <el-scrollbar height="calc(100vh - 300px)">
                        <!-- 全部 RSS -->
                        <div :class="[
                            'folder-item',
                            { active: selectedFeed === null && selectedFolder === null },
                        ]" @click="selectAllFeeds">
                            <el-icon>
                                <Document />
                            </el-icon>
                            <span class="folder-name">全部 RSS</span>
                            <el-tag type="info" size="small" class="count-tag">{{
                                feeds.length
                                }}</el-tag>
                        </div>

                        <!-- 未分类 -->
                        <div :class="[
                            'folder-item',
                            { active: selectedFolder === 'uncategorized' },
                        ]" @click="selectUncategorized">
                            <el-icon>
                                <FolderRemove />
                            </el-icon>
                            <span class="folder-name">未分类</span>
                            <el-tag type="warning" size="small" class="count-tag">{{
                                uncategorizedFeeds.length
                                }}</el-tag>
                        </div>

                        <!-- 文件夹列表 -->
                        <el-collapse v-model="expandedFolders" class="folder-collapse">
                            <el-collapse-item v-for="folder in folders" :key="folder.id" :name="folder.id">
                                <template #title>
                                    <div class="collapse-title">
                                        <el-icon>
                                            <FolderOpened />
                                        </el-icon>
                                        <span>{{ folder.name }}</span>
                                        <el-tag type="primary" size="small" class="count-tag">{{
                                            folder.feed_count
                                            }}</el-tag>
                                        <el-dropdown @command="handleFolderCommand($event, folder)" @click.stop>
                                            <el-icon class="folder-menu">
                                                <More />
                                            </el-icon>
                                            <template #dropdown>
                                                <el-dropdown-menu>
                                                    <el-dropdown-item command="edit">
                                                        <el-icon>
                                                            <Edit />
                                                        </el-icon>
                                                        编辑
                                                    </el-dropdown-item>
                                                    <el-dropdown-item command="delete" divided>
                                                        <el-icon>
                                                            <Delete />
                                                        </el-icon>
                                                        删除
                                                    </el-dropdown-item>
                                                </el-dropdown-menu>
                                            </template>
                                        </el-dropdown>
                                    </div>
                                </template>

                                <div class="feeds-in-folder">
                                    <div v-for="feed in getFeedsInFolder(folder.id)" :key="feed.id"
                                        :class="['feed-item', { active: selectedFeed === feed.id }]"
                                        @click="selectFeed(feed.id)">
                                        <el-icon>
                                            <DocumentCopy />
                                        </el-icon>
                                        <span class="feed-name">{{ feed.title }}</span>
                                        <el-dropdown @command="handleFeedCommand($event, feed)" @click.stop>
                                            <el-icon class="feed-menu">
                                                <More />
                                            </el-icon>
                                            <template #dropdown>
                                                <el-dropdown-menu>
                                                    <el-dropdown-item command="refresh">
                                                        <el-icon>
                                                            <RefreshRight />
                                                        </el-icon>
                                                        刷新
                                                    </el-dropdown-item>
                                                    <el-dropdown-item command="move">
                                                        <el-icon>
                                                            <Rank />
                                                        </el-icon>
                                                        移动
                                                    </el-dropdown-item>
                                                    <el-dropdown-item command="delete" divided>
                                                        <el-icon>
                                                            <Delete />
                                                        </el-icon>
                                                        删除
                                                    </el-dropdown-item>
                                                </el-dropdown-menu>
                                            </template>
                                        </el-dropdown>
                                    </div>
                                    <el-empty v-if="getFeedsInFolder(folder.id).length === 0" description="暂无订阅"
                                        :image-size="60" />
                                </div>
                            </el-collapse-item>
                        </el-collapse>

                        <!-- 未分类的Feeds -->
                        <div v-if="
                            uncategorizedFeeds.length > 0 &&
                            selectedFolder === 'uncategorized'
                        " class="uncategorized-feeds">
                            <div v-for="feed in uncategorizedFeeds" :key="feed.id"
                                :class="['feed-item', { active: selectedFeed === feed.id }]"
                                @click="selectFeed(feed.id)">
                                <el-icon>
                                    <DocumentCopy />
                                </el-icon>
                                <span class="feed-name">{{ feed.title }}</span>
                                <el-dropdown @command="handleFeedCommand($event, feed)" @click.stop>
                                    <el-icon class="feed-menu">
                                        <More />
                                    </el-icon>
                                    <template #dropdown>
                                        <el-dropdown-menu>
                                            <el-dropdown-item command="refresh">
                                                <el-icon>
                                                    <RefreshRight />
                                                </el-icon>
                                                刷新
                                            </el-dropdown-item>
                                            <el-dropdown-item command="move">
                                                <el-icon>
                                                    <Rank />
                                                </el-icon>
                                                移动
                                            </el-dropdown-item>
                                            <el-dropdown-item command="delete" divided>
                                                <el-icon>
                                                    <Delete />
                                                </el-icon>
                                                删除
                                            </el-dropdown-item>
                                        </el-dropdown-menu>
                                    </template>
                                </el-dropdown>
                            </div>
                        </div>
                    </el-scrollbar>
                </el-card>
            </el-col>

            <!-- 右侧内容列表 -->
            <el-col :xs="24" :sm="24" :md="16" :lg="18">
                <el-card class="content-card">
                    <template #header>
                        <div class="content-header">
                            <span>{{ currentTitle }}</span>
                            <div class="header-actions">
                                <el-button v-if="selectedFeed" type="primary" size="small" :icon="Rank"
                                    @click="showMoveFeedDialog">
                                    移动
                                </el-button>
                                <el-button type="primary" size="small" :icon="RefreshRight" :loading="refreshing"
                                    @click="refreshItems">
                                    刷新
                                </el-button>
                            </div>
                        </div>
                    </template>

                    <div class="items-container">
                        <el-empty v-if="!selectedFeed" description="请选择一个 RSS Feed" />

                        <el-card v-else class="feed-card" shadow="hover">
                            <el-form :model="selectedFeed" label-width="80px">
                                <!-- 标题 -->
                                <el-form-item label="Title">
                                    <el-input v-model="selectedFeed.title" placeholder="Feed Title"></el-input>
                                </el-form-item>

                                <!-- 描述 -->
                                <el-form-item label="Description">
                                    <el-input type="textarea" v-model="selectedFeed.description"
                                        placeholder="Feed Description" :rows="3"></el-input>
                                </el-form-item>

                                <!-- URL -->
                                <el-form-item label="URL">
                                    <el-input v-model="selectedFeed.url" placeholder="Feed URL"></el-input>
                                </el-form-item>

                                <!-- 可选：保存按钮 -->
                                <el-form-item>
                                    <el-button type="primary" @click="saveFeed">保存</el-button>
                                </el-form-item>
                            </el-form>
                        </el-card>
                    </div>
                </el-card>
            </el-col>
        </el-row>

        <!-- 新建文件夹对话框 -->
        <el-dialog v-model="showFolderDialog" title="新建文件夹" width="400px" destroy-on-close>
            <el-form :model="newFolder" label-width="80px">
                <el-form-item label="名称">
                    <el-input v-model="newFolder.name" placeholder="输入文件夹名称" />
                </el-form-item>
                <el-form-item label="父文件夹">
                    <el-select v-model="newFolder.parent" placeholder="选择父文件夹（可选）" clearable style="width: 100%">
                        <el-option label="根文件夹" :value="null" />
                        <el-option v-for="folder in flatFolders" :key="folder.id"
                            :label="'  '.repeat(folder.depth) + folder.name" :value="folder.id" />
                    </el-select>
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="showFolderDialog = false">取消</el-button>
                <el-button type="primary" @click="createFolder" :loading="creatingFolder">创建</el-button>
            </template>
        </el-dialog>

        <!-- 添加 Feed 对话框 -->
        <el-dialog v-model="showAddDialog" title="添加 RSS Feed" width="500px" destroy-on-close>
            <el-form :model="newFeed" label-width="100px">
                <el-form-item label="名称" required>
                    <el-input v-model="newFeed.title" placeholder="输入 Feed 名称" />
                </el-form-item>
                <el-form-item label="网站 URL" required>
                    <el-input v-model="newFeed.url" placeholder="https://example.com" />
                </el-form-item>
                <el-form-item label="Feed URL" required>
                    <el-input v-model="newFeed.feed_url" placeholder="https://example.com/feed.xml" />
                </el-form-item>
                <el-form-item label="描述">
                    <el-input v-model="newFeed.description" type="textarea" rows="3" placeholder="描述（可选）" />
                </el-form-item>
                <el-form-item label="文件夹">
                    <el-select v-model="newFeed.folder" placeholder="选择文件夹（可选）" clearable style="width: 100%">
                        <el-option label="不放入文件夹" :value="null" />
                        <el-option v-for="folder in flatFolders" :key="folder.id"
                            :label="'  '.repeat(folder.depth) + folder.name" :value="folder.id" />
                    </el-select>
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="showAddDialog = false">取消</el-button>
                <el-button type="primary" @click="addFeed" :loading="adding">添加</el-button>
            </template>
        </el-dialog>

        <!-- 导入 OPML 对话框 -->
        <el-dialog v-model="showImportDialog" title="导入 OPML 文件" width="500px" destroy-on-close>
            <el-upload class="upload-demo" drag action="" :auto-upload="false" :on-change="handleFileChange"
                accept=".opml,.xml" :limit="1">
                <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                <div class="el-upload__text">拖拽文件到此处或 <em>点击上传</em></div>
                <template #tip>
                    <div class="el-upload__tip">
                        支持 .opml 或 .xml 文件（支持包含文件夹结构）
                    </div>
                </template>
            </el-upload>

            <el-result v-if="importResult" :icon="importResult.success ? 'success' : 'error'"
                :title="importResult.success ? '导入成功' : '导入失败'" :sub-title="importResult.message">
                <template v-if="importResult.success && importResult.details" #extra>
                    <el-descriptions :column="3" border>
                        <el-descriptions-item label="总计">{{
                            importResult.details.total_found || feeds.length
                            }}</el-descriptions-item>
                        <el-descriptions-item label="成功">
                            <el-tag type="success">{{ importResult.added }}</el-tag>
                        </el-descriptions-item>
                        <el-descriptions-item label="跳过">
                            <el-tag type="warning">{{ importResult.skipped }}</el-tag>
                        </el-descriptions-item>
                        <el-descriptions-item label="失败">
                            <el-tag type="danger">{{ importResult.failed }}</el-tag>
                        </el-descriptions-item>
                    </el-descriptions>
                </template>
            </el-result>

            <template #footer>
                <el-button @click="showImportDialog = false">关闭</el-button>
                <el-button type="primary" @click="importOPML" :loading="importing" :disabled="!selectedFile">
                    开始导入
                </el-button>
            </template>
        </el-dialog>

        <!-- 编辑文件夹对话框 -->
        <el-dialog v-model="showEditFolderDialog" title="编辑文件夹" width="400px" destroy-on-close>
            <el-form :model="editingFolder" label-width="80px">
                <el-form-item label="名称">
                    <el-input v-model="editingFolder.name" placeholder="输入文件夹名称" />
                </el-form-item>
                <el-form-item label="父文件夹">
                    <el-select v-model="editingFolder.parent" placeholder="选择父文件夹" clearable style="width: 100%">
                        <el-option label="根文件夹" :value="null" />
                        <el-option v-for="folder in flatFolders.filter(
                            (f) => f.id !== editingFolder.id,
                        )" :key="folder.id" :label="'  '.repeat(folder.depth) + folder.name" :value="folder.id" />
                    </el-select>
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="showEditFolderDialog = false">取消</el-button>
                <el-button type="primary" @click="updateFolder" :loading="updatingFolder">保存</el-button>
            </template>
        </el-dialog>

        <!-- 移动 Feed 对话框 -->
        <el-dialog v-model="showMoveDialog" title="移动 Feed" width="400px" destroy-on-close>
            <el-form label-width="80px">
                <el-form-item label="目标文件夹">
                    <el-select v-model="targetFolderId" placeholder="选择文件夹" clearable style="width: 100%">
                        <el-option label="不放入文件夹" :value="null" />
                        <el-option v-for="folder in flatFolders" :key="folder.id"
                            :label="'  '.repeat(folder.depth) + folder.name" :value="folder.id" />
                    </el-select>
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="showMoveDialog = false">取消</el-button>
                <el-button type="primary" @click="moveFeed" :loading="movingFeed">移动</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import axios from "axios";
import { formatDistanceToNow } from "date-fns";
import { zhCN } from "date-fns/locale";
import { ElMessage, ElMessageBox } from "element-plus";
import { reactive } from 'vue'
import {
    FolderAdd,
    Plus,
    Upload,
    Folder,
    FolderOpened,
    FolderRemove,
    Document,
    DocumentCopy,
    More,
    Edit,
    Delete,
    RefreshRight,
    Rank,
    UploadFilled,
} from "@element-plus/icons-vue";

export default {
    name: "RSSView",
    setup() {
        const feeds = ref([]);
        const folders = ref([]);
        const items = ref([]);
        const itemsLoading = ref(false);
        const selectedFeed = ref(null);
        const selectedFolder = ref(null);
        const refreshing = ref(false);
        const importing = ref(false);
        const selectedFile = ref(null);
        const importResult = ref(null);

        // 对话框显示状态
        const showFolderDialog = ref(false);
        const showAddDialog = ref(false);
        const showImportDialog = ref(false);
        const showEditFolderDialog = ref(false);
        const showMoveDialog = ref(false);

        // 操作状态
        const creatingFolder = ref(false);
        const adding = ref(false);
        const updatingFolder = ref(false);
        const movingFeed = ref(false);

        // 展开的文件夹
        const expandedFolders = ref([]);

        // 表单数据
        const newFolder = ref({ name: "", parent: null });
        const newFeed = ref({
            title: "",
            url: "",
            feed_url: "",
            description: "",
            folder: null,
        });
        const editingFolder = ref({ id: null, name: "", parent: null });
        const targetFolderId = ref(null);
        const currentMovingFeed = ref(null);

        // 将文件夹扁平化用于下拉选择
        const flattenFolders = (foldersList, depth = 0) => {
            let result = [];
            foldersList.forEach((folder) => {
                result.push({ ...folder, depth });
                if (folder.children && folder.children.length > 0) {
                    result = result.concat(flattenFolders(folder.children, depth + 1));
                }
            });
            return result;
        };

        const flatFolders = computed(() => {
            return flattenFolders(folders.value);
        });

        // 未分类的feeds
        const uncategorizedFeeds = computed(() => {
            return feeds.value.filter((feed) => !feed.folder);
        });

        // 当前标题
        const currentTitle = computed(() => {
            if (selectedFolder.value) {
                if (selectedFolder.value === "uncategorized") {
                    return "📁 未分类";
                }
                const folder = folders.value.find((f) => f.id === selectedFolder.value);
                return folder ? `📁 ${folder.name}` : "全部 RSS";
            }
            if (selectedFeed.value === null) return "📑 全部 RSS";
            const feed = feeds.value.find((f) => f.id === selectedFeed.value);
            return feed ? `📄 ${feed.title}` : "全部 RSS";
        });

        // 获取文件夹内的feeds
        const getFeedsInFolder = (folderId) => {
            return feeds.value.filter((feed) => feed.folder === folderId);
        };

        const fetchFeeds = async () => {
            try {
                const response = await axios.get("/api/rss/feeds");
                feeds.value = response.data;
            } catch (err) {
                ElMessage.error("加载 Feeds 失败: " + err.message);
            }
        };

        const fetchFolders = async () => {
            try {
                const response = await axios.get("/api/rss/folders");
                folders.value = response.data;
            } catch (err) {
                ElMessage.error("加载文件夹失败: " + err.message);
            }
        };

        const fetchItems = async () => {
            try {
                itemsLoading.value = true;
                let params = {};

                console.log("selcted feed is", selectedFeed.value);
                if (selectedFeed.value) {
                    params = { feed: selectedFeed.value };
                }

                console.log("params", params);

                // Check if params object is empty
                if (Object.keys(params).length === 0) {
                    console.log("params is empty");
                } else {
                    console.log("params is ", params);
                    const response = await axios.get("/api/rss/items", { params });
                    items.value = response.data;
                }
            } catch (err) {
                ElMessage.error("加载内容失败: " + err.message);
            } finally {
                itemsLoading.value = false;
            }
        };
        const selectAllFeeds = () => {
            selectedFeed.value = null;
            selectedFolder.value = null;
            fetchItems();
        };

        const selectUncategorized = () => {
            selectedFolder.value = "uncategorized";
            selectedFeed.value = null;
            // 显示未分类的feeds内容
            const uncategorizedItems = [];
            uncategorizedFeeds.value.forEach((feed) => {
                // 这里需要获取未分类feed的内容
            });
            fetchItems();
        };

        const selectFeed = (feedId) => {
            const feed = feeds.value.find((f) => f.id === feedId);
            if (feed) {
                selectedFeed.value = reactive({ ...feed }); // 保存整个对象
                selectedFolder.value = null;
                console.log("选中的 Feed 对象:", selectedFeed.value);
            }
            fetchItems();
        };
        // 保存方法
        const saveFeed = () => {
            // 找到原来的 feed 在 feeds 数组中的索引
            const index = feeds.value.findIndex(
                (f) => f.id === selectedFeed.value.id,
            );
            if (index !== -1) {
                // 用修改后的对象替换原来的
                feeds.value[index] = { ...selectedFeed.value };
                console.log("已保存修改后的 Feed:", feeds.value[index]);
                // 可选：调用 API 保存到后端
            }
        };

        const createFolder = async () => {
            if (!newFolder.value.name.trim()) {
                ElMessage.warning("请输入文件夹名称");
                return;
            }

            try {
                creatingFolder.value = true;
                await axios.post("/api/rss/folders", newFolder.value);
                ElMessage.success("文件夹创建成功");
                newFolder.value = { name: "", parent: null };
                showFolderDialog.value = false;
                await fetchFolders();
            } catch (err) {
                ElMessage.error(
                    "创建文件夹失败: " + (err.response?.data?.detail || err.message),
                );
            } finally {
                creatingFolder.value = false;
            }
        };

        const addFeed = async () => {
            if (
                !newFeed.value.title.trim() ||
                !newFeed.value.url.trim() ||
                !newFeed.value.feed_url.trim()
            ) {
                ElMessage.warning("请填写完整信息");
                return;
            }

            try {
                adding.value = true;
                await axios.post("/api/rss/feeds", newFeed.value);
                ElMessage.success("Feed 添加成功");
                newFeed.value = {
                    title: "",
                    url: "",
                    feed_url: "",
                    description: "",
                    folder: null,
                };
                showAddDialog.value = false;
                await fetchFeeds();
                await fetchItems();
            } catch (err) {
                ElMessage.error(
                    "添加 Feed 失败: " + (err.response?.data?.detail || err.message),
                );
            } finally {
                adding.value = false;
            }
        };

        const handleFileChange = (file) => {
            selectedFile.value = file.raw;
            importResult.value = null;
        };

        const importOPML = async () => {
            if (!selectedFile.value) {
                ElMessage.warning("请选择文件");
                return;
            }

            try {
                importing.value = true;
                importResult.value = null;

                const formData = new FormData();
                formData.append("file", selectedFile.value);

                const response = await axios.post("/api/rss/feeds/import", formData, {
                    headers: {
                        "Content-Type": "multipart/form-data",
                    },
                });

                importResult.value = {
                    success: true,
                    message: response.data.message,
                    added: response.data.added,
                    skipped: response.data.skipped,
                    failed: response.data.failed,
                    details: response.data.details,
                };

                await fetchFeeds();
                await fetchFolders();

                selectedFile.value = null;
            } catch (err) {
                importResult.value = {
                    success: false,
                    message: "导入失败: " + (err.response?.data?.error || err.message),
                };
            } finally {
                importing.value = false;
            }
        };

        const handleFolderCommand = (command, folder) => {
            if (command === "edit") {
                editingFolder.value = {
                    id: folder.id,
                    name: folder.name,
                    parent: folder.parent,
                };
                showEditFolderDialog.value = true;
            } else if (command === "delete") {
                ElMessageBox.confirm(
                    `确定要删除文件夹 "${folder.name}" 吗？文件夹内的feeds将变为未分类。`,
                    "删除确认",
                    {
                        confirmButtonText: "删除",
                        cancelButtonText: "取消",
                        type: "warning",
                    },
                )
                    .then(() => {
                        deleteFolder(folder.id);
                    })
                    .catch(() => { });
            }
        };

        const updateFolder = async () => {
            try {
                updatingFolder.value = true;
                await axios.put(`/api/rss/folders/${editingFolder.value.id}`, {
                    name: editingFolder.value.name,
                    parent: editingFolder.value.parent,
                });
                ElMessage.success("文件夹更新成功");
                showEditFolderDialog.value = false;
                await fetchFolders();
                await fetchFeeds();
            } catch (err) {
                ElMessage.error("更新文件夹失败: " + err.message);
            } finally {
                updatingFolder.value = false;
            }
        };

        const deleteFolder = async (folderId) => {
            try {
                await axios.delete(`/api/rss/folders/${folderId}`);
                ElMessage.success("文件夹删除成功");
                if (selectedFolder.value === folderId) {
                    selectedFolder.value = null;
                    selectedFeed.value = null;
                }
                await fetchFolders();
                await fetchFeeds();
            } catch (err) {
                ElMessage.error("删除文件夹失败: " + err.message);
            }
        };

        const handleFeedCommand = (command, feed) => {
            if (command === "refresh") {
                refreshFeed(feed.id);
            } else if (command === "move") {
                currentMovingFeed.value = feed;
                targetFolderId.value = feed.folder;
                showMoveDialog.value = true;
            } else if (command === "delete") {
                ElMessageBox.confirm(
                    `确定要删除 RSS 订阅 "${feed.title}" 吗？`,
                    "删除确认",
                    {
                        confirmButtonText: "删除",
                        cancelButtonText: "取消",
                        type: "warning",
                    },
                )
                    .then(() => {
                        deleteFeed(feed.id);
                    })
                    .catch(() => { });
            }
        };

        const showMoveFeedDialog = () => {
            const feed = feeds.value.find((f) => f.id === selectedFeed.value);
            if (feed) {
                currentMovingFeed.value = feed;
                targetFolderId.value = feed.folder;
                showMoveDialog.value = true;
            }
        };

        const moveFeed = async () => {
            if (!currentMovingFeed.value) return;

            try {
                movingFeed.value = true;
                await axios.post(`/api/rss/feeds/${currentMovingFeed.value.id}/move`, {
                    folder: targetFolderId.value,
                });
                ElMessage.success("移动成功");
                showMoveDialog.value = false;
                targetFolderId.value = null;
                currentMovingFeed.value = null;
                await fetchFeeds();
            } catch (err) {
                ElMessage.error("移动失败: " + err.message);
            } finally {
                movingFeed.value = false;
            }
        };

        const deleteFeed = async (feedId) => {
            try {
                await axios.delete(`/api/rss/feeds/${feedId}`);
                ElMessage.success("Feed 删除成功");
                if (selectedFeed.value === feedId) {
                    selectedFeed.value = null;
                    await fetchItems();
                }
                await fetchFeeds();
            } catch (err) {
                ElMessage.error("删除失败: " + err.message);
            }
        };

        const refreshFeed = async (feedId) => {
            try {
                await axios.post(`/api/rss/feeds/${feedId}/refresh`);
                ElMessage.success("刷新成功");
                if (selectedFeed.value === feedId) {
                    await fetchItems();
                }
            } catch (err) {
                ElMessage.error("刷新失败: " + err.message);
            }
        };

        const refreshItems = async () => {
            try {
                refreshing.value = true;
                if (selectedFeed.value) {
                    await axios.post(`/api/rss/feeds/${selectedFeed.value}/refresh`);
                }
                await fetchItems();
            } catch (err) {
                console.error("Refresh failed:", err);
            } finally {
                refreshing.value = false;
            }
        };

        const formatTime = (time) => {
            try {
                return formatDistanceToNow(new Date(time), {
                    addSuffix: true,
                    locale: zhCN,
                });
            } catch {
                return time;
            }
        };

        const truncateText = (text, maxLength) => {
            if (!text) return "";
            if (text.length <= maxLength) return text;
            return text.substring(0, maxLength) + "...";
        };

        const stripHtml = (html) => {
            if (!html) return "";
            const tmp = document.createElement("DIV");
            tmp.innerHTML = html;
            return tmp.textContent || tmp.innerText || "";
        };

        onMounted(() => {
            fetchFolders();
            fetchFeeds().then(() => {
                fetchItems();
            });
        });

        return {
            feeds,
            folders,
            flatFolders,
            items,
            itemsLoading,
            selectedFeed,
            selectedFolder,
            refreshing,
            importing,
            selectedFile,
            importResult,
            showFolderDialog,
            showAddDialog,
            showImportDialog,
            showEditFolderDialog,
            showMoveDialog,
            creatingFolder,
            adding,
            updatingFolder,
            movingFeed,
            expandedFolders,
            newFolder,
            newFeed,
            editingFolder,
            targetFolderId,
            uncategorizedFeeds,
            currentTitle,
            selectAllFeeds,
            selectUncategorized,
            selectFeed,
            saveFeed,
            createFolder,
            addFeed,
            handleFileChange,
            importOPML,
            handleFolderCommand,
            updateFolder,
            deleteFolder,
            handleFeedCommand,
            showMoveFeedDialog,
            moveFeed,
            deleteFeed,
            refreshFeed,
            refreshItems,
            formatTime,
            truncateText,
            stripHtml,
            getFeedsInFolder,
            // Icons
            FolderAdd,
            Plus,
            Upload,
            Folder,
            FolderOpened,
            FolderRemove,
            Document,
            DocumentCopy,
            More,
            Edit,
            Delete,
            RefreshRight,
            Rank,
            UploadFilled,
        };
    },
};
</script>

<style scoped>
.rss-view {
    padding: 20px;
}

.action-area {
    margin-top: 20px;
    margin-bottom: 20px;
}

.main-content {
    margin-top: 0;
}

.folder-card {
    height: calc(100vh - 200px);
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: bold;
}

.folder-item {
    display: flex;
    align-items: center;
    padding: 10px;
    margin: 5px 0;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s;
}

.folder-item:hover {
    background-color: #f5f7fa;
}

.folder-item.active {
    background-color: #ecf5ff;
    color: #409eff;
}

.folder-name {
    flex: 1;
    margin-left: 8px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.count-tag {
    margin-left: 8px;
}

.folder-collapse {
    border: none;
}

.folder-collapse :deep(.el-collapse-item__header) {
    padding-left: 0;
    border-bottom: none;
}

.folder-collapse :deep(.el-collapse-item__content) {
    padding-bottom: 0;
}

.collapse-title {
    display: flex;
    align-items: center;
    flex: 1;
}

.collapse-title span {
    margin-left: 8px;
    flex: 1;
}

.folder-menu {
    padding: 4px;
    border-radius: 4px;
    cursor: pointer;
}

.folder-menu:hover {
    background-color: #f5f7fa;
}

.feeds-in-folder {
    margin-left: 20px;
}

.feed-item {
    display: flex;
    align-items: center;
    padding: 8px 10px;
    margin: 3px 0;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s;
    font-size: 14px;
}

.feed-item:hover {
    background-color: #f5f7fa;
}

.feed-item.active {
    background-color: #ecf5ff;
    color: #409eff;
}

.feed-name {
    flex: 1;
    margin-left: 8px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.feed-menu {
    padding: 2px;
    border-radius: 4px;
    opacity: 0;
    transition: opacity 0.3s;
}

.feed-item:hover .feed-menu {
    opacity: 1;
}

.feed-menu:hover {
    background-color: #e4e7ed;
}

.uncategorized-feeds {
    margin-left: 10px;
    margin-top: 10px;
}

.content-card {
    min-height: calc(100vh - 200px);
}

.content-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: bold;
}

.header-actions {
    display: flex;
    gap: 10px;
}

.items-container {
    min-height: 400px;
}

.item-card {
    margin-bottom: 10px;
}

.item-title {
    margin: 0 0 10px 0;
    font-size: 16px;
}

.item-title a {
    color: #303133;
    text-decoration: none;
    transition: color 0.3s;
}

.item-title a:hover {
    color: #409eff;
}

.item-description {
    color: #606266;
    font-size: 14px;
    line-height: 1.6;
    margin: 0;
}

:deep(.el-timeline-item__timestamp) {
    color: #909399;
    font-size: 13px;
}

.upload-demo {
    text-align: center;
}

.upload-demo :deep(.el-upload-dragger) {
    width: 100%;
}

.feed-card {
    padding: 1rem;
    margin: 1rem 0;
}

.feed-title {
    font-size: 1rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
}

.feed-description {
    font-size: 1rem;
    color: #666;
    line-height: 1.4;
}
</style>
