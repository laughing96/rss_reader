// 创建vue应用-注入插件-挂载到页面上

import { createApp } from 'vue' // 从vue核心库中导入createApp, 创建一个Vue应用实例
import { createPinia } from 'pinia' // Pinia 状态管理库 用来存放全局数据, 登录用户,主题,购物车等
import router from './router' // 引入自己定义的路由系统,用来切换页面
import App from './App.vue' //整个应用的根组件,页面\组件嵌套在里面

const app = createApp(App) //创建根组件

app.use(createPinia()) //将pinia注入到整个vue应用中
app.use(router) // this.$router.push('/login')  <router-view>

app.mount('#app') // 把vue应用渲染到HTML里id=app的那个dom节点上
