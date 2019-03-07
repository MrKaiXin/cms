var vm = new Vue({
    el: '#loginform',
    data: {
        host: 'http://127.0.0.1:8000',
        username: '',
        password: '',
        remember: false,

        error_username: false,
        error_pwd: false,

        error_msg: '',    // 提示信息
    },
    mounted: function () {
        // 登录了用户不能访问登录界面
        var token = sessionStorage.token || localStorage.token;
        axios.get(this.host + '/userlogin/', {
                headers: {
                    'Authorization': 'JWT ' + token  // 传递jwt给服务器
                },
            })
            .then(response => {
                // 有token或token未过期, 就跳回访问登录页面前的那个一个的页面
                location.href = '/index.html';
            })
            .catch(error => {
                // token过期, 删除保存在浏览器中的过期的token
                sessionStorage.clear();
                localStorage.clear();
                console.log(error.response);
            });

        // 用户上次登录后, 如果记住登录, 则显示上次的用户名
        if (localStorage.username != "undefined" && localStorage.username) {
            this.username = localStorage.username;
            this.remember = true;
        }
    },
    methods: {
        // 检查数据
        check_username: function(){
            if (!this.username) {
                this.error_username = true;
                this.error_msg = '请填写用户名';
            } else {
                this.error_username = false;
                this.error_msg = '';
            }
        },
        check_pwd: function(){
            if (!this.password) {
                this.error_msg = '请填写密码';
                this.error_pwd = true;
            } else {
                this.error_pwd = false;
                this.error_msg = '';
            }
        },

        // 表单提交
        on_submit: function(){
            this.check_username();
            this.check_pwd();

            if (this.error_username == false && this.error_pwd == false) {
                axios.post(this.host+'/authorizations/', {
                        username: this.username,
                        password: this.password
                    }, {
                        withCredentials: true  // 跨域传递cookie给服务器
                    })
                    .then(response => {
                        // 使用浏览器本地存储保存token
                        sessionStorage.clear();
                        localStorage.clear();
                        if (this.remember) {
                            // 记住登录
                            localStorage.token = response.data.token;
                            localStorage.id = response.data.id;
                            localStorage.username = response.data.username;
                        } else {
                            // 未记住登录
                            sessionStorage.token = response.data.token;
                            sessionStorage.id = response.data.id;
                            sessionStorage.username = response.data.username;
                        }
                        // 跳转页面
                        location.href = '/index.html';
                    })
                    .catch(error => {
                        if (error.response.status == 400) {
                            this.error_msg = '用户名或密码错误';
                        } else {
                            this.error_msg = '服务器错误';
                        }
                    })
            }
        },
    }
});