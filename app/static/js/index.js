import api from './api/api.js';
import { formatFileSize } from './util.js';

const { createApp, ref, onMounted, onUnmounted } = Vue;

// 获取所有图标组件
const {
    Folder,
    Back,
    Document,
    Monitor,
    TrendCharts,
    Connection,
    Setting,
    Search,
    Picture,
    VideoCamera,
    Files
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

        // ref对象
        const serverFileTable = ref(null);
        const monitoredFileTable = ref(null);

        // 服务器文件
        const serverFiles = ref([]);
        // 服务器当前路径
        const serverCurrentPath = ref(null)
        // 当前目录文件数量
        const serverFileCount = ref(0)

        // 模拟数据
        const stats = ref({
            totalDistributions: 3651,
            dailyIncrease: 24,
            monitoredFiles: 62,
            activePaths: 3,
            serverStatus: '在线',
            uptime: '24天'
        });

        // 初始化数据
        onMounted(async () => {
            // 获取服务器文件列表
            let response = await api.admin.getDirectoryContents();
            flushServerFileList(response.data.data)
        })

        const flushServerFileList = (data) => {
            serverFileCount.value = data.count
            serverCurrentPath.value = data.current_path
            let files = [{ name: "[返回上一级]", isDir: true, isBack: true }]
            for (let item of data.directories) {
                files.push({
                    name: item.name,
                    path: item.path,
                    isDir: true
                })
            }
            for (let item of data.files) {
                files.push({
                    name: item.name,
                    path: item.path,
                    isDir: false,
                    size: formatFileSize(item.size),
                    lastModified: item.last_modified
                })
            }
            serverFiles.value = files;
        }

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

        const selectable = (row) => {
            if (row.isBack) {
                return false;
            }
            return true;
        };

        const handleServerFileTableRowClick = async (row, column, event) => {
            // 如果点击的是文件夹，进入下一层
            if (row.isDir) {
                // 取消所有选择
                selectedServerFiles.value = [];
                serverFileTable.value.clearSelection();
                try {
                    let response = null
                    if (row.isBack) {
                        // 返回上一级目录
                        let lastIndex = serverCurrentPath.value.lastIndexOf("\\");
                        if (lastIndex !== -1) serverCurrentPath.value = serverCurrentPath.value.slice(0, lastIndex)
                        response = await api.admin.getDirectoryContents(serverCurrentPath.value, undefined);
                    } else {
                        // 异步获取新目录内容
                        response = await api.admin.getDirectoryContents(serverCurrentPath.value + "\\" + row.name, undefined);
                    }
                    // 刷新文件列表
                    flushServerFileList(response.data.data)
                } catch (error) {
                    console.error("获取目录内容失败～", error);
                }
            } else {
                serverFileTable.value.toggleRowSelection(row);
            }
        };

        const handleMonitoredFileTableRowClick = (row, column, event) => {
            monitoredFileTable.value.toggleRowSelection(row);
        };

        const getServerFileTableRowClassName = ({ row }) => {
            return selectedServerFiles.value.includes(row) ? 'selected-row' : '';
        };
        const getMonitoredFileTableRowClassName = ({ row }) => {
            return selectedMonitorFiles.value.includes(row) ? 'selected-row' : '';
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

        const getFileIcon = (fileName) => {
            const ext = fileName.split('.').pop().toLowerCase();
            const iconMap = {
                png: Picture,
                jpg: Picture,
                jpeg: Picture,
                gif: Picture,
                mp4: VideoCamera,
                avi: VideoCamera,
                mkv: VideoCamera,
                doc: Document,
                docx: Document,
                pdf: Document
            };
            return iconMap[ext] || Files;
        }


        return {
            currentSection,
            stats,
            serverFiles,
            monitoredFiles,
            switchSection,
            handleServerSelection,
            handleMonitorSelection,
            selectable,
            serverFileTable,
            monitoredFileTable,
            getServerFileTableRowClassName,
            getMonitoredFileTableRowClassName,
            handleServerFileTableRowClick,
            handleMonitoredFileTableRowClick,
            addToMonitor,
            removeFromMonitor,
            getFileIcon
        };
    }
});

// 注册Element Plus
app.use(ElementPlus);

// 注册所有用到的图标组件
app.component('Folder', Folder);
app.component('Back', Back);
app.component('Document', Document);
app.component('Monitor', Monitor);
app.component('TrendCharts', TrendCharts);
app.component('Connection', Connection);
app.component('Setting', Setting);
app.component('Search', Search);
app.component('Picture', Picture);
app.component('VideoCamera', VideoCamera);
app.component('Files', Files);

app.mount('#app');