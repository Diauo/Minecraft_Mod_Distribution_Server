const feature_api = {
  get_all_feature() {
    return axios.get('/api/feat/get_all_feature');
  },
  get_feature_by_customer_id(id) {
    return axios.get('/api/feat/get_feature_by_customer_id?customer_id=' + id);
  }
};

export default feature_api