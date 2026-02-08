import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import HackerNewsView from '../views/HackerNewsView.vue'
import RSSView from '../views/RSSView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView
  },
  {
    path: '/hackernews',
    name: 'HackerNews',
    component: HackerNewsView
  },
  {
    path: '/rss',
    name: 'RSS',
    component: RSSView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
