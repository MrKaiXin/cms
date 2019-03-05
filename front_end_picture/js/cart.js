var vm = new Vue({
    el: '#app',
    data: {
        host,
        goods_list: [],         // 购物车中的商品
    },

    computed: {
        select_all: function() {
            for (let i = 0; i < this.goods_list.length; i++) {
                let goods = this.goods_list[i];
                if (!goods.selected) {
                    return false;
                }
            }
            return true;
        },

        // 获取选中的商品的数量
        selected_count: function() {
            let total_count = 0;
            for (let i = 0; i < this.goods_list.length; i++) {
                let goods = this.goods_list[i];
                // 重新计算小计金额, 自动刷新界面显示
                if (goods.selected) {
                    total_count += parseInt(goods.count);
                }
            }
            return total_count;
        },

        // 获取选中的商品的总金额
        selected_amount: function() {
            let total_amount = 0;
            for (let i = 0; i < this.goods_list.length; i++) {
                let goods = this.goods_list[i];
                goods.amount = parseFloat(goods.sell_price) * parseInt(goods.count);
                if (goods.selected) {
                    total_amount += parseFloat(goods.sell_price) * parseInt(goods.count);
                }
            }
            // 金额保存两位有效数字
            return total_amount.toFixed(2);
        },
    },

    mounted: function () {
        this.get_cart_goods();
    },

    methods: {
        // 全选和全不选
        on_select_all: function() {
            let select = !this.select_all;
            //发送请求
            if (this.goods_list.length) {
                let config = {
                    /*
                     headers: { // 通过请求头往服务器传递登录状态
                     'Authorization': 'JWT ' + this.token
                     },*/
                    withCredentials: true   // 注意： 跨域请求传递cookie给服务器
                };
                axios.put(this.host + '/cart/seletions/', {
                    'selected': select
                }, config)
                    .then(response => {
                        for (let i = 0; i < this.goods_list.length; i++) {
                            this.goods_list[i].selected = select;
                        }
                    })
                    .catch(error => {
                        console.log(error.response);
                    })
            }
        },

        // 获取购物车商品数据
        get_cart_goods: function () {

            //发送请求
            let config = {
                /*
                headers: { // 通过请求头往服务器传递登录状态
                    'Authorization': 'JWT ' + this.token
                },*/
                withCredentials: true   // 注意： 跨域请求传递cookie给服务器
            };
            axios.get(this.host + '/cart/', config)
                .then(response => {
                    this.goods_list = response.data;
                    for(i=0; i<this.goods_list.length; i++){
                        this.goods_list[i].amount = parseFloat(this.goods_list[i].sell_price) * parseInt(this.goods_list[i].count);
                    }
                    get_cart_count()
                })
                .catch(error => {
                    console.log(error.response);
                })
        },

        // 点击增加购买数量
        on_add: function(index) {
            let goods = this.goods_list[index];
            let count = goods.count + 1;
            this.update_cart_count(goods.id, count, goods.selected, index);
        },

        // 点击减少购买数量
        on_minus: function(index){
            let goods = this.goods_list[index];
            let count = goods.count;
            if (count > 1) {
                count--;
                this.update_cart_count(goods.id, count, goods.selected, index);
            }
        },

        // 更新购物车商品购买数量
        on_input: function(e, index) {
            // 输入的数量不能超过最大库存
            let goods = this.goods_list[index];
            this.update_cart_count(goods.id, goods.count, goods.selected, index);
            e.currentTarget.blur();
        },

        // 点击选中商品
        on_selected: function(index) {
            let goods = this.goods_list[index];
            this.update_cart_count(goods.id, goods.count, !goods.selected, index);
        },

        // 更新购物车商品数量
        update_cart_count: function(goods_id, goods_count, goods_selected, index) {
            //发送请求
            let config = {
                /*
                headers: { // 通过请求头往服务器传递登录状态
                    'Authorization': 'JWT ' + this.token
                },*/
                withCredentials: true   // 注意： 跨域请求传递cookie给服务器
            };
            axios.put(this.host + '/cart/', {
                'id':goods_id,
                'count': goods_count,
                'selected': goods_selected
            },config)
                .then(response => {
                    this.goods_list[index].count = parseInt(goods_count);
                    this.goods_list[index].selected = goods_selected;
                    this.goods_list[index].amount = parseFloat(this.goods_list[index].sell_price) * parseInt(this.goods_list[index].count);
                    get_cart_count()
                })
                .catch(error => {
                    console.log(error.response);
                })
        },

        // 删除购物车中的一个商品
        delete_goods: function(index){
            //发送请求
            id = this.goods_list[index].id;
            let config = {
                /*
                headers: { // 通过请求头往服务器传递登录状态
                    'Authorization': 'JWT ' + this.token
                },*/
                data: {
                    'id': id
                },
                withCredentials: true   // 注意： 跨域请求传递cookie给服务器
            };
            axios.delete(this.host + '/cart/', config)
                .then(response => {
                    this.goods_list.splice(index, 1);
                    console.log(response.data);
                    get_cart_count()
                })
                .catch(error => {
                    console.log(error.response);
                })
        },

        // 清空购物车
        clearCart: function(index){
            if (this.goods_list.length) {
                //发送请求
                let config = {
                    /*
                    headers: { // 通过请求头往服务器传递登录状态
                        'Authorization': 'JWT ' + this.token
                    },*/
                    withCredentials: true   // 注意： 跨域请求传递cookie给服务器
                };
                axios.delete(this.host + '/carts/', config)
                    .then(response => {
                        this.goods_list = [];
                        console.log(response.data);
                        get_cart_count()
                    })
                    .catch(error => {
                        console.log(error.response);
                    })
            }
        },
    }
});