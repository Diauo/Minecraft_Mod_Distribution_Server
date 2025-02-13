
const { createApp, ref, onMounted } = Vue

const App = {
    setup() {
        const isLoading = ref(true)

        onMounted(() => {
            // 模拟页面加载完成
            setTimeout(() => {
                isLoading.value = false
            }, 1500)
        })

        return {
            isLoading
        }
    },
    template: `
        <div class="content">
          <h1>页面内容</h1>
          <p>这里是你的页面内容</p>
          <div class="mask-container" :class="{ 'mask-hidden': !isLoading }">
            <div class="diagonal-line"></div>
            <div class="mask-top"></div>
            <div class="mask-bottom"></div>
          </div>
        </div>
      `
}

createApp(App).mount('#app')