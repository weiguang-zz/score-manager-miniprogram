var api = require('../../utils/api')

Component({
  data: {
    staffList: [],
    loading: false,
    addLoading: false,
    newUsername: '',
    newPassword: '',
    roleIndex: 0,
    roleOptions: [
      { label: '只读员工', value: 'staff_readonly' },
      { label: '编辑员工', value: 'staff_editor' }
    ]
  },
  pageLifetimes: {
    show: function () {
      this.loadStaff()
    }
  },
  methods: {
    loadStaff: function () {
      var that = this
      that.setData({ loading: true })
      api.getStaffList().then(function (list) {
        that.setData({ staffList: list, loading: false })
      }).catch(function (err) {
        wx.showToast({ title: err.message || '加载失败', icon: 'none' })
        that.setData({ loading: false })
      })
    },
    onUsernameInput: function (e) {
      this.setData({ newUsername: e.detail.value })
    },
    onPasswordInput: function (e) {
      this.setData({ newPassword: e.detail.value })
    },
    onRoleChange: function (e) {
      this.setData({ roleIndex: parseInt(e.detail.value, 10) })
    },
    handleAddStaff: function () {
      var that = this
      var username = that.data.newUsername.trim()
      var password = that.data.newPassword
      var role = that.data.roleOptions[that.data.roleIndex].value

      if (!username || username.length < 2) {
        wx.showToast({ title: '用户名至少2个字符', icon: 'none' })
        return
      }
      if (!password || password.length < 4) {
        wx.showToast({ title: '密码至少4位', icon: 'none' })
        return
      }

      that.setData({ addLoading: true })
      api.createStaff(username, password, role).then(function () {
        wx.showToast({ title: '添加成功', icon: 'success' })
        that.setData({ newUsername: '', newPassword: '', roleIndex: 0 })
        that.loadStaff()
      }).catch(function (err) {
        wx.showToast({ title: err.message || '添加失败', icon: 'none' })
      }).finally(function () {
        that.setData({ addLoading: false })
      })
    },
    handleToggleRole: function (e) {
      var that = this
      var id = e.currentTarget.dataset.id
      var currentRole = e.currentTarget.dataset.role
      var newRole = currentRole === 'staff_editor' ? 'staff_readonly' : 'staff_editor'

      api.updateStaff(id, newRole).then(function () {
        wx.showToast({ title: '已更新', icon: 'success' })
        that.loadStaff()
      }).catch(function (err) {
        wx.showToast({ title: err.message || '更新失败', icon: 'none' })
      })
    },
    handleDeleteStaff: function (e) {
      var that = this
      var id = e.currentTarget.dataset.id
      var name = e.currentTarget.dataset.name

      wx.showModal({
        title: '确认删除',
        content: '确定删除员工 "' + name + '" 吗？',
        confirmColor: '#ff4d4f',
        success: function (res) {
          if (res.confirm) {
            api.deleteStaff(id).then(function () {
              wx.showToast({ title: '已删除', icon: 'success' })
              that.loadStaff()
            }).catch(function (err) {
              wx.showToast({ title: err.message || '删除失败', icon: 'none' })
            })
          }
        }
      })
    }
  }
})
