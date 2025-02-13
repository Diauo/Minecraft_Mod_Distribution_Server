const admin_api = {
  modifyMonitor_list(add, monitor_list) {
    return axios.post('/api/him/modify_monitor', {
      'add': add,
      'monitor_list': monitor_list
    });
  },
  queryMonitor(page, size, name, server_path, client_path, is_directory, allow,
    created_date_start, created_date_end, updated_date_start, updated_date_end) {
    return axios.post('/api/him/query_monitor', {
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
    return axios.get('/api/him/query_monitor')
  },
  reloadConfig() {
    return axios.get('/api/him/reload_config')
  },
  getDirectoryContents(path, filter) {
    return axios.post('/api/him/get_directory', { 'path': path, 'filter': filter })
  }
};

export default admin_api