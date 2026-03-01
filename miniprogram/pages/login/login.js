var api = require('../../utils/api')

Component({
  data: {
    username: '',
    password: '',
    loading: false
  },
  methods: {
    onUsernameInput: function (e) {
      this.setData({ username: e.detail.value })
    },
    onPasswordInput: function (e) {
      this.setData({ password: e.detail.value })
    },
    handleLogin: function () {
      var that = this
      var username = that.data.username
      var password = that.data.password
      if (!username || !password) {
        wx.showToast({ title: '请输入用户名和密码', icon: 'none' })
        return
      }
      that.setData({ loading: true })
      api.login(username, password).then(function () {
        wx.redirectTo({ url: '/pages/home/home' })
      }).catch(function (err) {
        wx.showToast({ title: err.message || '登录失败', icon: 'none' })
      }).finally(function () {
        that.setData({ loading: false })
      })
    }
  }
})
