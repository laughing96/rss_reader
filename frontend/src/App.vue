<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-brand">
        <span class="logo">📰</span>
        <h1>HN + RSS Reader</h1>
      </div>
      <div class="nav-links">
        <router-link to="/" :class="{ active: $route.path === '/' }">
          全部
        </router-link>
        <router-link to="/hackernews" :class="{ active: $route.path === '/hackernews' }">
          Hacker News
        </router-link>
        <router-link to="/rss" :class="{ active: $route.path === '/rss' }">
          RSS Feeds
        </router-link>
      </div>
    </nav>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script>
export default {
  name: 'App'
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
  background-color: #f6f6ef;
  color: #333;
}

.navbar {
  background-color: #ff6600;
  padding: 0.5rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-brand .logo {
  font-size: 1.5rem;
}

.nav-brand h1 {
  color: white;
  font-size: 1.1rem;
  font-weight: 600;
}

.nav-links {
  display: flex;
  gap: 1rem;
}

.nav-links a {
  color: white;
  text-decoration: none;
  padding: 0.3rem 0.8rem;
  border-radius: 4px;
  transition: background-color 0.2s;
  font-size: 0.9rem;
}

.nav-links a:hover,
.nav-links a.active {
  background-color: rgba(255,255,255,0.2);
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

@media (max-width: 768px) {
  .navbar {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .nav-links {
    gap: 0.5rem;
  }
  
  .nav-links a {
    font-size: 0.8rem;
    padding: 0.2rem 0.5rem;
  }
}
</style>
