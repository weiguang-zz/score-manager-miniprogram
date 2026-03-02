var api = require('../../utils/api')

Component({
  data: {
    id: 0,
    name: '',
    currentScore: 0,
    records: [],
    loading: false,
    canEdit: false,
    startDate: '',
    endDate: ''
  },
  methods: {
    onLoad: function (query) {
      var id = parseInt(query.id, 10)
      var name = decodeURIComponent(query.name || '')
      var score = parseInt(query.score, 10) || 0
      this.setData({
        id: id,
        name: name,
        currentScore: score,
        canEdit: api.canEdit()
      })
    },
    onShow: function () {
      this.loadRecords()
    },
    loadRecords: function () {
      var that = this
      that.setData({ loading: true })
      api.getRecords(that.data.id).then(function (records) {
        var currentScore = records.length > 0 ? records[0].balance_after : 0
        that.setData({ records: records, currentScore: currentScore, loading: false })
      }).catch(function (err) {
        wx.showToast({ title: err.message || '加载失败', icon: 'none' })
        that.setData({ loading: false })
      })
    },
    goAddRecord: function () {
      var id = this.data.id
      var name = this.data.name
      wx.navigateTo({
        url: '/pages/add-record/add-record?id=' + id + '&name=' + encodeURIComponent(name)
      })
    },
    onStartDateChange: function (e) {
      this.setData({ startDate: e.detail.value })
    },
    onEndDateChange: function (e) {
      this.setData({ endDate: e.detail.value })
    },
    exportRecords: function () {
      var path = '/api/export/members/' + this.data.id + '/records'
      api.downloadExport(path, this.data.startDate, this.data.endDate)
    },
    handleDelete: function () {
      var that = this
      wx.showModal({
        title: '确认删除',
        content: '删除后该成员的所有积分记录将被清除，不可恢复。',
        confirmColor: '#ff4d4f',
        success: function (res) {
          if (res.confirm) {
            api.deleteMember(that.data.id).then(function () {
              wx.showToast({ title: '已删除', icon: 'success' })
              wx.navigateBack()
            }).catch(function (err) {
              wx.showToast({ title: err.message || '删除失败', icon: 'none' })
            })
          }
        }
      })
    }
  }
})
