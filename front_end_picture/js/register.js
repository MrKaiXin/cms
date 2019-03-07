var vm = new Vue({
    el: '#app',
    data: {
        host,
        // 双向绑定变量
        username: '',
        password: '',
        password2: '',
        mobile: '',
        sms_code: '',
        allow: false,

        // 控制元素是否显示
        error_name: false,
        error_password: false,
        error_check_password: false,
        error_phone: false,
        error_sms_code: false,
        error_allow: false,

        // 出错提示
        error_name_message: '请输入5-20个字符的用户名',
        error_password_message: '请输入8-20位的登录密码',
        error_phone_message: '请输入正确的手机号',
        error_sms_code_message: '请输入短信验证码',

        sms_code_tip: '获取验证码',
        sending_flag: false, 			// 正在发送短信标志

        // 图片验证码
        image_code_id: '',
        image_code_url: '',
    },

    // 当vue实例挂载到界面后执行, 可以在此方法中执行界面初始化操作
    mounted: function () {
    },

    methods: {
        check_username: function () {
            var len = this.username.length;
            if (len < 5 || len > 20) {
                this.error_name_message = '请输入5-20个字符的用户名';
                this.error_name = true;
            } else {
                this.error_name = false;
                axios.get(this.host + '/usernames/' + this.username + '/count/')
                    .then(response => {
                        if (response.data.count) {
                            this.error_name_message = '用户名已被注册';
                            this.error_name = true;
                        } else {
                            this.error_name = false;
                        }
                    })
                    .catch(error => {
                        console.log(error.response);
                    })
            }
        },

        check_pwd: function () {
            var len = this.password.length;
            if (len < 8 || len > 20) {
                this.error_password_message = '请输入8-20位的登录密码';
                this.error_password = true;
            } else {
                this.error_password = false;
            }
        },

        check_cpwd: function () {
            if (this.password !== this.password2 || !this.password || !this.password2) {
                this.error_check_password = true;
            } else {
                this.error_check_password = false;
            }
        },

        check_phone: function () {
            var re = /^((13[0-9])|(14[5,7])|(15[0-3,5-9])|(17[0,3,5-8])|(18[0-9])|166|198|199|(147))\d{8}$/;
            if (re.test(this.mobile)) {
                this.error_phone = false;
                axios.get(this.host + '/mobile/' + this.mobile + '/count/')
                    .then(response => {
                        if (response.data.count) {
                            this.error_phone_message = '手机号已被注册';
                            this.error_phone = true;
                        } else {
                            this.error_phone = false;
                        }
                    })
                    .catch(error => {
                        console.log(error.response);
                    })
            } else {
                this.error_phone_message = '请输入正确的手机号';
                this.error_phone = true;
            }
        },

        check_sms_code: function () {
            var len = this.sms_code.length;
            if (len === 0) {
                this.error_sms_code_message = '请输入短信验证码';
                this.error_sms_code = true;
            } else {
                this.error_sms_code = false;
            }
        },

        check_allow: function () {
            if (!this.allow) {
                this.error_allow = true;
            } else {
                this.error_allow = false;
            }
        },

        // 获取短信
        get_sms_code: function() {
            // 如果显示了短信验证码出错提示, 则隐藏它
            this.error_sms_code = false;

            // 如果正在发送短信验证码, 则不重复发送
            if (this.sending_flag) {
                // 正在下发短信验证码
                return
            }

            this.check_phone();
            if (this.error_phone) {
                // 短信验证码校验出错
                this.sending_flag = false;
                return
            }
            this.sending_flag = true;  // 表示正在等待服务器下发短信

            if (!this.error_phone) {
				//发送获取请求
				axios.get(this.host + '/sms_codes/' + this.mobile + '/')
                    .then(response => {
                        var num = 60;
                        // 设置一个计时器
                        var t = setInterval(() => {
                            if (num == 1) {
                                // 如果计时器到最后, 清除计时器对象
                                clearInterval(t);
                                // 将点击获取验证码的按钮展示的文本恢复成原始文本
                                this.sms_code_tip = '获取验证码';
                                // 将点击按钮的onclick事件函数恢复回去
                                this.sending_flag = false;
                            } else {
                                num -= 1;
                                // 展示倒计时信息
                                this.sms_code_tip = num + '秒';
                            }
                        }, 1000, 60);
                    })
                    .catch(error => {
                        if (error.response.data) {
                            if (error.response.data.message === '发送短信过于频繁') {
                                this.error_sms_code_message = '发送短信过于频繁';
                                this.error_sms_code = true;
                            } else if (error.response.data.message === '手机号已被注册') {
                                this.error_phone_message = '手机号已被注册';
                                this.error_phone = true;
                            }

                        }

                        console.log(error.response);
                        this.sending_flag = false;
                    })
            }
        },

        // 点击注册按钮
        on_submit: function () {

            this.check_username();
            this.check_pwd();
            this.check_cpwd();
            this.check_phone();
            this.check_sms_code();
            this.check_allow();

            if (this.error_name === false
                && this.error_password === false
                && this.error_check_password === false
                && this.error_phone === false
                && this.error_sms_code === false
                && this.error_allow === false) {

                var data = {
                    username: this.username,
                    password: this.password,
                    password2: this.password2,
                    mobile: this.mobile,
                    sms_code: this.sms_code,
                    allow: this.allow
                };

				//发送注册请求
                axios.post(this.host + '/users/', data, {
                        withCredentials: true  // 跨域传递cookie给服务器
                    })
                    .then(response => {
                        // 清除之前保存的数据
                        sessionStorage.clear();
                        localStorage.clear();
                        // 保存用户的登录状态数据
                        localStorage.token = response.data.token;
                        localStorage.username = response.data.username;
                        localStorage.user_id = response.data.id;
                        location.href = '/index.html';  // 注册成功跳转到首页
                    })
                    .catch(error => {
                        console.log(error.response);
                    })
            } else {
                alert('填写有误')
            }
        },
    }
});

