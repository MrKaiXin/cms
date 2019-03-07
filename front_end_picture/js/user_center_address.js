var vm = new Vue({
    el: '#app',
    data: {
        host: host,
        user_id: sessionStorage.user_id || localStorage.user_id,
        token: sessionStorage.token || localStorage.token,
        username: sessionStorage.username || localStorage.username,
        addresses: [],      // 当前登录用户的地址列表
        default_address_id: '',     // 当前登录用户的默认地址的id
    },

    mounted: function(){
        // 查询用户的收件地址
        axios.get(this.host + '/addresses/', {
                headers: {
                    'Authorization': 'JWT ' + this.token
                }
            })
            .then(response => {
                this.addresses = response.data.addresses;
                this.default_address_id = response.data.default_address_id;
            })
            .catch(error => {
                console.log(error.response);
            })
    },

    methods: {
        set_default: function(index){
            axios.put(this.host + '/addresses/' + this.addresses[index].id + '/status/', {}, {
                    headers: {
                        'Authorization': 'JWT ' + this.token
                    },
                    responseType: 'json'
                })
                .then(response => {
                    this.default_address_id = this.addresses[index].id;
                })
                .catch(error => {
                    console.log(error.response);
                })
        },

        // 删除地址
        delete_address: function(address_id){
            axios.delete(this.host + '/addresses/' + this.addresses[address_id].id + '/', {
                    headers: {
                        'Authorization': 'JWT ' + this.token
                    },
                    responseType: 'json'
                })
                .then(response => {
                    // 从数组中移除地址
                    this.addresses.splice(address_id, 1);
                })
                .catch(error => {
                    console.log(error.response);
                })
        },
    }
});