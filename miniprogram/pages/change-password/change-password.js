var api = require('../../utils/api')

Component({
  data: {
    oldPassword: '',
    newPassword: '',
    confirmPassword: '',
    loading: false
  },
  methods: {
    onOldPasswordInput: function (e) {
      this.setData({ oldPassword: e.detail.value })
    },
    onNewPasswordInput: function (e) {
      this.setData({ newPassword: e.detail.value })
    },
    onConfirmPasswordInput: function (e) {
      this.setData({ confirmPassword: e.detail.value })
    },
    handleSubmit: function () {
      var that = this
      var oldPwd = that.data.oldPassword
      var newPwd = that.data.newPassword
      var confirmPwd = that.data.confirmPassword

      if (!oldPwd) {
        wx.showToast({ title: '请输入旧密码', icon: 'none' })
        return
      }
      if (!newPwd || newPwd.length < 4) {
        wx.showToast({ title: '新密码至少4位', icon: 'none' })
        return
      }
      if (newPwd !== confirmPwd) {
        wx.showToast({ title: '两次密码不一致', icon: 'none' })
        return
      }

      that.setData({ loading: true })
      api.changePassword(oldPwd, newPwd).then(function () {
        wx.showToast({ title: '修改成功', icon: 'success' })
        setTimeout(function () {
          wx.navigateBack()
        }, 1500)
      }).catch(function (err) {
        wx.showToast({ title: err.message || '修改失败', icon: 'none' })
      }).finally(function () {
        that.setData({ loading: false })
      })
    }
  }
})
