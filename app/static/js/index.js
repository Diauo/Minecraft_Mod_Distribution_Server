import api from './api/api.js';

const { createApp, ref, onMounted, onUnmounted } = Vue;

// 获取所有图标组件
const {
    Back,
    Document,
    Monitor,
    TrendCharts,
    Connection,
    Setting,
    Search
} = ElementPlusIconsVue;

// 添加防抖函数
function debounce(fn, delay) {
    let timer = null;
    return function (...args) {
        if (timer) clearTimeout(timer);
        timer = setTimeout(() => {
            fn.apply(this, args);
        }, delay);
    };
}

const app = createApp({
    setup() {
        const currentSection = ref('dashboard');
        const selectedServerFiles = ref([]);
        const selectedMonitorFiles = ref([]);
        let chart = null; // 存储图表实例

        // 模拟数据
        const stats = ref({
            totalDistributions: 3651,
            dailyIncrease: 24,
            monitoredFiles: 62,
            activePaths: 3,
            serverStatus: '在线',
            uptime: '24天'
        });

        const serverFiles = ref([
            { name: 'server.properties', size: '2KB' },
            { name: 'mods/fabric-api.jar', size: '1.2MB' },
            { name: 'config/fabric.conf', size: '4KB' }
        ]);

        const monitoredFiles = ref([
            { name: 'server.properties', lastUpdate: '2025-02-12 14:28:31' },
            { name: 'mods/fabric-api.jar', lastUpdate: '2025-02-12 14:28:31' }
        ]);

        // 切换页面
        const switchSection = (section) => {
            currentSection.value = section;
        };

        // 文件选择处理
        const handleServerSelection = (selection) => {
            selectedServerFiles.value = selection;
        };

        const handleMonitorSelection = (selection) => {
            selectedMonitorFiles.value = selection;
        };

        // 添加到监控
        const addToMonitor = () => {
            // 这里添加实际的添加逻辑
            console.log('添加到监控:', selectedServerFiles.value);
        };

        // 从监控中移除
        const removeFromMonitor = () => {
            // 这里添加实际的移除逻辑
            console.log('从监控中移除:', selectedMonitorFiles.value);
        };

        // 初始化趋势图表
        onMounted(() => {
            chart = echarts.init(document.getElementById('trend-chart'));
            const option = {
                xAxis: {
                    type: 'category',
                    data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00']
                },
                yAxis: {
                    type: 'value'
                },
                series: [{
                    data: [150, 230, 224, 218, 135, 147, 260],
                    type: 'line',
                    smooth: true,
                    areaStyle: {}
                }]
            };
            chart.setOption(option);

            // 使用防抖处理 resize
            const debouncedResize = debounce(() => {
                if (chart) {
                    chart.resize();
                }
            }, 100); // 100ms 的防抖延迟

            window.addEventListener('resize', debouncedResize);

            // 在组件卸载时清理
            onUnmounted(() => {
                window.removeEventListener('resize', debouncedResize);
                if (chart) {
                    chart.dispose();
                    chart = null;
                }
            });
        });

        return {
            currentSection,
            stats,
            serverFiles,
            monitoredFiles,
            switchSection,
            handleServerSelection,
            handleMonitorSelection,
            addToMonitor,
            removeFromMonitor
        };
    }
});

// 注册Element Plus
app.use(ElementPlus);

// 注册所有用到的图标组件
app.component('Back', Back);
app.component('Document', Document);
app.component('Monitor', Monitor);
app.component('TrendCharts', TrendCharts);
app.component('Connection', Connection);
app.component('Setting', Setting);
app.component('Search', Search);

app.mount('#app');