const category_api = {
  get_all_category() {
    return axios.get('/api/cate/get_all_category');
  },
  get_category_by_customer_id(customer_id) {
    return axios.get('/api/cate/get_category_by_customer_id?customer_id=' + customer_id);
  },
  add_category(category) {
    return axios.post('/api/cate/add_category', category);
  },
  del_category(category) {
    return axios.post('/api/cate/del_category', category);
  },
};

export default category_api