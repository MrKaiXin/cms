var vm = new Vue({
    el: '#app',
    data: {
        host: host,
        token: sessionStorage.token || localStorage.token,

        provinces: [],
        cities: [],
        districts: [],

        addresses: [],
        limit: '',
        default_address_id: '',
        form_address: {
            receiver: '',
            province_id: '',
            city_id: '',
            district_id: '',
            place: '',
            mobile: '',
            tel: '',
            email: '',
        },

        error_receiver: false,
        error_place: false,
        error_mobile: false,
        error_email: false,
    },

    mounted: function () {
        // 获取所有的省份,发送请求
		axios.get(this.host + '/areas/')
            .then(response => {
                this.provinces = response.data;
            })
            .catch(error => {
                alert(error.response.data);
            });
    },

    // 监听属性：监听vue的一个变量，每当这个变量发生改变，都执行特定的操作
    watch: {
    	// 省份改变，获取城市
        'form_address.province_id': function () {
            if (this.form_address.province_id) { // province_id 不为空
                this.cities = [];
                this.districts = [];
                axios.get(this.host + '/areas/' + this.form_address.province_id + '/')
                    .then(response => {
                        this.cities = response.data.subs;
                    })
                    .catch(error => {
                        console.log(error.response.data);
                        this.cities = [];
                    });
            }
        },

        // 城市改变，获取区县
        'form_address.city_id': function () {
            if (this.form_address.city_id) { // city_id 不为空
                this.districts = [];
                axios.get(this.host + '/areas/' + this.form_address.city_id + '/')
                    .then(response => {
                        this.districts = response.data.subs;
                    })
                    .catch(error => {
                        console.log(error.response.data);
                        this.districts = [];
                    });
            }
        }
    },

    methods: {
        // 展示新增地址界面
        show_add: function () {
            this.form_address.receiver = '';
            this.form_address.province_id = '';
            this.form_address.city_id = '';
            this.form_address.district_id = '';
            this.form_address.place = '';
            this.form_address.mobile = '';
            this.form_address.tel = '';
            this.form_address.email = '';
        },

        check_receiver: function () {
            if (!this.form_address.receiver) {
                this.error_receiver = true;
            } else {
                this.error_receiver = false;
            }
        },

        check_place: function () {
            if (!this.form_address.place) {
                this.error_place = true;
            } else {
                this.error_place = false;
            }
        },

        check_mobile: function () {
            var re = /^1[345789]\d{9}$/;
            if (re.test(this.form_address.mobile)) {
                this.error_mobile = false;
            } else {
                this.error_mobile = true;
            }
        },

        check_email: function () {
            if (this.form_address.email) {
                var re = /^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$/;
                if (re.test(this.form_address.email)) {
                    this.error_email = false;
                } else {
                    this.error_email = true;
                }
            }
        },

        // 保存地址
        save_address: function(){
            if (this.error_receiver || this.error_place
                || this.error_mobile || this.error_email
                || !this.form_address.province_id
                || !this.form_address.city_id
                || !this.form_address.district_id ) {
                alert('信息填写有误');
                return
            }
            // 设置地址标题
            this.form_address.title = this.form_address.receiver;
            // 新增地址
            axios.post(this.host + '/addresses/', this.form_address, {
                headers: {
                    'Authorization': 'JWT ' + this.token
                }
            })
            .then(response => {
                // 将新地址添加到数组的头部（作为第一个元素）
                this.addresses.splice(0, 0, response.data);
                location.href = '/user_center_address.html';
            })
            .catch(error => {
                console.log(error.response.data);
            })
        },
    }
});