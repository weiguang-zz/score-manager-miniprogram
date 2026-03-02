var api = require('../../utils/api')

Component({
  data: {
    memberId: 0,
    memberName: '',
    amount: '',
    reason: '',
    isAdd: true,
    loading: false,
    rooms: [],
    roomNames: [],
    roomIndex: -1,
    selectedRoomId: null
  },
  methods: {
    onLoad: function (query) {
      this.setData({
        memberId: parseInt(query.id, 10),
        memberName: decodeURIComponent(query.name || '')
      })
      this.loadRooms()
    },
    loadRooms: function () {
      var that = this
      api.getRooms().then(function (rooms) {
        var names = rooms.map(function (r) { return r.name })
        that.setData({ rooms: rooms, roomNames: names })
      })
    },
    onRoomChange: function (e) {
      var index = parseInt(e.detail.value, 10)
      this.setData({
        roomIndex: index,
        selectedRoomId: this.data.rooms[index].id
      })
    },
    switchType: function (e) {
      var isAdd = e.currentTarget.dataset.type === 'add'
      this.setData({ isAdd: isAdd })
    },
    onAmountInput: function (e) {
      this.setData({ amount: e.detail.value })
    },
    onReasonInput: function (e) {
      this.setData({ reason: e.detail.value })
    },
    handleSubmit: function () {
      var that = this
      var memberId = that.data.memberId
      var amount = that.data.amount
      var reason = that.data.reason
      var isAdd = that.data.isAdd
      var roomId = that.data.selectedRoomId
      var num = parseInt(amount, 10)
      if (!amount || isNaN(num) || num === 0) {
        wx.showToast({ title: '请输入有效数值', icon: 'none' })
        return
      }
      if (!roomId) {
        wx.showToast({ title: '请选择直播间', icon: 'none' })
        return
      }
      var changeAmount = isAdd ? Math.abs(num) : -Math.abs(num)
      that.setData({ loading: true })
      api.createRecord(memberId, changeAmount, reason, roomId).then(function () {
        wx.showToast({ title: '提交成功', icon: 'success' })
        wx.navigateBack()
      }).catch(function (err) {
        wx.showToast({ title: err.message || '提交失败', icon: 'none' })
      }).finally(function () {
        that.setData({ loading: false })
      })
    }
  }
})
