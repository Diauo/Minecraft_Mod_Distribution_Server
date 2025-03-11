export function formatFileSize(bytes) {
    if (bytes === 0) return "0 Bytes";
    if (!bytes) return "";

    const units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];
    const k = 1024; // 1 KB = 1024 Bytes
    const i = Math.floor(Math.log(bytes) / Math.log(k)); // 计算单位索引

    // 保留两位小数，并添加单位
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + units[i];
}

