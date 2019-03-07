var vm = new Vue({
    el: '#app',
    data: {
        recommend_goods: [],
        categories: [],
    },

    mounted: function () {
        this.get_recommend_goods();
        // this.get_category_goods();
    },

    methods: {
		//获取推荐商品
        get_recommend_goods: function () {
            // {
            //     headers: {  // 传递登录状态jwt
            //         'Authorization': 'JWT ' + this.token
            //     },
            //     withCredentials: true  // 跨域传递cookie给服务器
            // }
            // 发送请求
            axios.get('http://127.0.0.1:8000/goods/', {
                responseType:'json'
            })
            .then(response => {
                this.recommend_goods = response.data.recommend;
                this.categories = response.data.advertisement;
            })
            .catch(error => {
                console.log(error.response);
            })
        },
		//获取分类商品
        // get_category_goods: function () {
         //   //发送请求
         //        })
        // },
    },

    filters: {
        formatDate: function (time) {
            return dateFormat(time, "yyyy-mm-dd");
        },

        formatDate2: function (time) {
            return dateFormat(time, "yyyy-mm-dd HH:MM:ss");
        },
    },
});
