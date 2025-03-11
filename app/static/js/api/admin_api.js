const admin_api = {
  modifyMonitorList(add, allow, monitor_list) {
    return axios.post('/api/him/monitor/modify', {
      'add': add,
      'allow': allow,
      'monitor_list': monitor_list
    });
  },
  queryMonitor(page, size, name, server_path, client_path, is_directory, allow,
    created_date_start, created_date_end, updated_date_start, updated_date_end) {
    return axios.post('/api/him/monitor/query', {
      'page': page,
      'size': size,
      'name': name,
      'server_path': server_path,
      'client_path': client_path,
      'is_directory': is_directory,
      'allow': allow,
      'created_date_start': created_date_start,
      'created_date_end': created_date_end,
      'updated_date_start': updated_date_start,
      'updated_date_end': updated_date_end,
    });
  },
  genVersion() {
    return axios.get('/api/him/version/gen')
  },
  reloadConfig() {
    return axios.get('/api/him/config/reload')
  },
  getDirectoryContents(path, filter) {
    return axios.post('/api/him/directory/get', { 'path': path, 'filter': filter })
  },
  getMonitorDirectoryContents(client_path) {
    return axios.post('/api/him/monitor/get_directory', { 'client_path': client_path })
  }
};

export default admin_api