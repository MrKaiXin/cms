var vm = new Vue({
    el: '#app',
    data: {
        host,
        messages: [1, 2, 3],
        slide_news: [],
        top_news: [],
        image_news: [],
        categories: []
    },

    mounted: function () {
        this.init_top_news();
        this.init_category_news();
    },

    methods: {
        // 初始化显示顶部的新闻数据
        init_top_news: function () {
            // console.log('11111');
            axios.get(this.host+'/news/top/')
                .then(response => {
                    // alert(response)
                    this.slide_news = response.data.slide_news;
                    this.top_news = response.data.top_news;
                    this.image_news = response.data.image_news;
                    // console.log(response.data);
                    // console.log(this.top_news);
                    // alert(response)
                })
                .catch(error => {
                    console.log(error.response.data)
                });
        },

        // 初始化显示类别新闻数据
        init_category_news: function () {
            axios.get(this.host+'/news/category/')
                .then(response => {
                    this.categories=response.data;

                    // console.log(response.data);
                    // console.log(this.top_news);
                })


        },
    },

    filters: {
        formatDate: function (time) {
            return dateFormat(time, "yyyy-mm-dd");
        },

        formatDate2: function (time) {
            return dateFormat(time, "yyyy-mm-dd HH:MM:ss");
        },
    },

    // 数据发生改变并渲染刷新完成后调用
    updated: function () {
        // 界面刷新后开始轮播
        $("#focus-box").flexslider({
            directionNav: false,
            pauseOnAction: false
        });
    }
});
