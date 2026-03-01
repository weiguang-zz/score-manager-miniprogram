var api = require('../../utils/api')

Component({
  data: {
    name: '',
    initialScore: '0',
    loading: false
  },
  methods: {
    onNameInput: function (e) {
      this.setData({ name: e.detail.value })
    },
    onScoreInput: function (e) {
      this.setData({ initialScore: e.detail.value })
    },
    handleSubmit: function () {
      var that = this
      var name = that.data.name
      var initialScore = that.data.initialScore
      if (!name.trim()) {
        wx.showToast({ title: '请输入姓名', icon: 'none' })
        return
      }
      var score = parseInt(initialScore, 10) || 0
      that.setData({ loading: true })
      api.createMember(name.trim(), score).then(function () {
        wx.showToast({ title: '添加成功', icon: 'success' })
        wx.navigateBack()
      }).catch(function (err) {
        wx.showToast({ title: err.message || '添加失败', icon: 'none' })
      }).finally(function () {
        that.setData({ loading: false })
      })
    }
  }
})
